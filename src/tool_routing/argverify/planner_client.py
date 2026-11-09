"""Planner-as-config for the second-planner replication runs.

A planner is selected by a spec string:

    ollama:<model>                 local Ollama /api/chat (as the frozen runs)
    api:<provider>:<model>         HTTP API; key read from an env var, never
                                   stored in traces or printed
    mock:<path/to/traces.json>     replays saved model outputs (dry run)

Every ``chat()`` returns the raw assistant text plus a ``call_record``
with: model id as sent, model build (Ollama full digest / API response
model-version string), every sampling parameter actually sent, the
request timestamp (UTC), latency, and provider-reported usage when
present. Secrets never enter the record — only the env-var NAME.

Providers (``api:``):
    openai       OPENAI_API_KEY       https://api.openai.com/v1
    openrouter   OPENROUTER_API_KEY   https://openrouter.ai/api/v1
    groq         GROQ_API_KEY         https://api.groq.com/openai/v1
    together     TOGETHER_API_KEY     https://api.together.xyz/v1
    deepseek     DEEPSEEK_API_KEY     https://api.deepseek.com/v1
    compat       OPENAI_COMPAT_API_KEY + OPENAI_COMPAT_BASE_URL (any
                 OpenAI-compatible endpoint)
    anthropic    ANTHROPIC_API_KEY    https://api.anthropic.com/v1/messages
                 (no ``seed`` parameter — recorded as unsupported)

planner-client-1.1 (Amendment 1, 2026-11-08 — written before any
second-planner model output existed): ``api:openai`` sends
``max_completion_tokens`` (2048) instead of ``max_tokens``, omits
``temperature`` (provider accepts only the default 1), keeps ``seed``,
and probes ``reasoning_effort`` once at startup in order
none -> minimal -> low, sending the lowest accepted. All API backends
retry HTTP 429/5xx with exponential backoff (max 5 tries, recorded per
call) and store the full error body on failure. ``finish_reason=
"length"`` or empty content is flagged ``budget_exhausted`` — never
an abstention.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

PLANNER_CLIENT_VERSION = "planner-client-1.1"

_OPENAI_COMPAT = {
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    "together": ("TOGETHER_API_KEY", "https://api.together.xyz/v1"),
    "deepseek": ("DEEPSEEK_API_KEY", "https://api.deepseek.com/v1"),
    "compat": ("OPENAI_COMPAT_API_KEY", None),  # base from env
}


@dataclass
class Sampling:
    """Sampling parameters requested by the harness (the frozen qwen
    settings). Backends record what they actually sent."""
    temperature: float = 0.7
    max_tokens: int = 512
    seed: int | None = None
    think: bool = False


@dataclass
class ChatResult:
    ok: bool
    raw: str = ""
    error: str = ""
    call_record: dict = field(default_factory=dict)


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _post_json(url: str, body: dict, headers: dict, timeout: int = 180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class _HTTPFailure(Exception):
    """HTTP error after the retry policy gave up (or a non-retryable
    status). Carries status, full error body, and the retry log."""
    def __init__(self, code: int, body: str, attempts: list):
        self.code, self.body, self.attempts = code, body, attempts
        super().__init__(f"HTTP {code}")


def _post_json_retry(url: str, body: dict, headers: dict,
                     tries: int = 5, timeout: int = 180):
    """POST json; exponential backoff on HTTP 429 and 5xx (max ``tries``
    attempts). Returns (resp, retry_log). Raises _HTTPFailure with the
    full error body and the complete retry log."""
    log, delay = [], 1.0
    for i in range(tries):
        try:
            return _post_json(url, body, headers, timeout), log
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")[:16000]
            log.append({"try": i + 1, "status": e.code,
                        "error_body": text})
            if (e.code == 429 or e.code >= 500) and i + 1 < tries:
                retry_after = e.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after
                           else delay)
                delay *= 2
                continue
            raise _HTTPFailure(e.code, text, log)
    raise _HTTPFailure(log[-1]["status"], log[-1]["error_body"], log)


# planner-client-1.1 — Amendment 1 (2026-11-08), for OpenAI models:
# probed on api:openai:gpt-6.1-sol after two failed attempts
# (runs/second_planner_failed/).
_OPENAI_MAX_COMPLETION_TOKENS = 2048  # hidden reasoning must not
                                     # starve the visible answer
_REASONING_EFFORT_ORDER = ("none", "minimal", "low")


class PlannerClient:
    spec: str
    backend: str
    model: str

    def chat(self, messages: list[dict], sampling: Sampling,
             replay_key: tuple | None = None) -> ChatResult:
        raise NotImplementedError

    def describe(self) -> dict:
        """Static description for the run manifest (no secrets)."""
        return {"spec": self.spec, "backend": self.backend,
                "model": self.model, "client": PLANNER_CLIENT_VERSION}


class OllamaPlanner(PlannerClient):
    """Same request shape as the frozen runners' ``call_planner`` /
    ``call_turn``: /api/chat, stream=false, think, options
    {temperature, num_predict, seed}."""
    backend = "ollama"

    def __init__(self, model: str, host: str | None = None):
        self.spec = f"ollama:{model}"
        self.model = model
        self.host = host or os.environ.get("OLLAMA_HOST",
                                           "http://localhost:11434")
        self._digest = None
        self._version = None

    def _probe(self) -> None:
        if self._digest is not None:
            return
        self._digest, self._version = "not available", "not available"
        try:
            with urllib.request.urlopen(f"{self.host}/api/version",
                                        timeout=10) as r:
                self._version = json.loads(r.read()).get("version",
                                                         "not available")
        except Exception:  # noqa: BLE001
            pass
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags",
                                        timeout=10) as r:
                for m in json.loads(r.read()).get("models", []):
                    if m.get("name") == self.model or \
                            m.get("model") == self.model:
                        self._digest = m.get("digest", "not available")
                        self._details = m.get("details", {})
        except Exception:  # noqa: BLE001
            pass

    def describe(self) -> dict:
        self._probe()
        return {**super().describe(), "host": self.host,
                "ollama_version": self._version,
                "model_digest": self._digest,
                "model_details": getattr(self, "_details", {})}

    def chat(self, messages, sampling, replay_key=None) -> ChatResult:
        self._probe()
        options = {"temperature": sampling.temperature,
                   "num_predict": sampling.max_tokens}
        if sampling.seed is not None:
            options["seed"] = sampling.seed
        body = {"model": self.model, "messages": messages,
                "stream": False, "think": sampling.think,
                "options": options}
        rec = {"backend": "ollama", "model_id": self.model,
               "model_digest": self._digest,
               "ollama_version": self._version,
               "params_sent": {**options, "think": sampling.think},
               "timestamp_utc": _now()}
        t0 = time.time()
        try:
            resp = _post_json(f"{self.host}/api/chat", body, {})
        except Exception as e:  # noqa: BLE001
            rec["latency_ms"] = int((time.time() - t0) * 1000)
            return ChatResult(False, error=str(e), call_record=rec)
        rec.update({"latency_ms": int((time.time() - t0) * 1000),
                    "model_returned": resp.get("model"),
                    "eval_count": resp.get("eval_count"),
                    "prompt_eval_count": resp.get("prompt_eval_count"),
                    "done_reason": resp.get("done_reason")})
        return ChatResult(True, raw=resp["message"]["content"],
                          call_record=rec)


class OpenAICompatPlanner(PlannerClient):
    backend = "api"

    def __init__(self, provider: str, model: str):
        env, base = _OPENAI_COMPAT[provider]
        self.spec = f"api:{provider}:{model}"
        self.provider, self.model, self.env = provider, model, env
        self.base = base or os.environ.get("OPENAI_COMPAT_BASE_URL")
        if not self.base:
            raise ValueError("compat provider needs OPENAI_COMPAT_BASE_URL")
        if not os.environ.get(env):
            raise ValueError(f"missing API key env var {env}")
        self._effort = None       # str once probed, False if all failed
        self._effort_probe = None

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {os.environ[self.env]}"}

    def _probe_effort(self) -> None:
        """planner-client-1.1: one startup probe for the lowest
        reasoning_effort the model accepts, trying the parameter in
        order none -> minimal -> low (closest to qwen's think=false).
        Non-400 failures (network/auth) abort the probe rather than
        burn quota."""
        if self._effort_probe is not None:
            return
        self._effort_probe = []
        for cand in _REASONING_EFFORT_ORDER:
            try:
                _post_json_retry(
                    f"{self.base}/chat/completions",
                    {"model": self.model,
                     "messages": [{"role": "user", "content": "ping"}],
                     "max_completion_tokens": 16,
                     "reasoning_effort": cand},
                    self._headers())
                self._effort = cand
                self._effort_probe.append({"reasoning_effort": cand,
                                           "status": "accepted"})
                return
            except _HTTPFailure as e:
                self._effort_probe.append(
                    {"reasoning_effort": cand, "status": e.code,
                     "error_body": e.body[:2000]})
                if not (400 <= e.code < 500):
                    self._effort = False
                    return
            except Exception as e:  # noqa: BLE001
                self._effort_probe.append(
                    {"reasoning_effort": cand,
                     "error": type(e).__name__})
                self._effort = False
                return
        self._effort = False  # all candidates rejected -> omit param

    def describe(self) -> dict:
        d = {**super().describe(), "provider": self.provider,
             "base_url": self.base, "api_key_env": self.env}
        if self.provider == "openai":
            d.update({"client_params": "planner-client-1.1: "
                      "temperature omitted (default 1); "
                      f"max_completion_tokens="
                      f"{_OPENAI_MAX_COMPLETION_TOKENS}; seed kept; "
                      "reasoning_effort probed none->minimal->low",
                      "reasoning_effort_sent":
                          self._effort if self._effort else
                          "not sent (probe pending or all rejected)",
                      "reasoning_effort_probe": self._effort_probe})
        return d

    def _params(self, sampling: Sampling) -> tuple[dict, list]:
        """(params actually sent, deviation notes)."""
        if self.provider == "openai":
            self._probe_effort()
            p = {"max_completion_tokens": _OPENAI_MAX_COMPLETION_TOKENS}
            if sampling.seed is not None:
                p["seed"] = sampling.seed
            if self._effort:
                p["reasoning_effort"] = self._effort
            dev = ["temperature omitted — provider accepts only the "
                   "default 1 (0.7 rejected; forced by API)",
                   "token budget 2048 via max_completion_tokens "
                   "(requested 512; max_tokens rejected; 2048 covers "
                   "hidden reasoning + visible answer)",
                   f"reasoning_effort="
                   f"{self._effort if self._effort else 'not sent'}"
                   " (startup probe: lowest accepted of none/minimal/"
                   "low — closest to think=false)"]
        else:
            p = {"temperature": sampling.temperature,
                 "max_tokens": sampling.max_tokens}
            if sampling.seed is not None:
                p["seed"] = sampling.seed  # best-effort on compat
            dev = ["non-OpenAI compat provider — planner-client-1.0 "
                   "params retained (temperature, max_tokens)"]
        return p, dev

    def chat(self, messages, sampling, replay_key=None) -> ChatResult:
        params, dev = self._params(sampling)
        body = {"model": self.model, "messages": messages, **params}
        rec = {"backend": "api", "provider": self.provider,
               "model_id": self.model, "api_key_env": self.env,
               "params_sent": dict(params),
               "deviations": dev,
               "timestamp_utc": _now()}
        if self.provider == "openai":
            rec["reasoning_effort_probe"] = self._effort_probe
        t0 = time.time()
        try:
            resp, rec["retries"] = _post_json_retry(
                f"{self.base}/chat/completions", body, self._headers())
        except _HTTPFailure as e:
            rec.update({"latency_ms": int((time.time() - t0) * 1000),
                        "retries": e.attempts,
                        "error_body": e.body})
            return ChatResult(False, error=f"HTTP {e.code}",
                              call_record=rec)
        except Exception as e:  # noqa: BLE001
            rec["latency_ms"] = int((time.time() - t0) * 1000)
            return ChatResult(False, error=type(e).__name__,
                              call_record=rec)
        choice = (resp.get("choices") or [{}])[0]
        usage = resp.get("usage") or {}
        fin = choice.get("finish_reason")
        rec.update({"latency_ms": int((time.time() - t0) * 1000),
                    "model_version": resp.get("model"),
                    "system_fingerprint": resp.get("system_fingerprint"),
                    "response_id": resp.get("id"),
                    "usage": usage,
                    "finish_reason": fin,
                    "completion_tokens": usage.get("completion_tokens"),
                    "reasoning_tokens": (usage.get(
                        "completion_tokens_details") or {})
                    .get("reasoning_tokens")})
        msg = choice.get("message", {})
        raw = msg.get("content") or ""
        # a reasoning model can burn the whole budget on hidden tokens:
        # finish_reason=length or empty visible content is
        # budget_exhausted — NEVER counted as a model abstention.
        if fin == "length" or not raw:
            rec["budget_exhausted"] = True
        if not raw:
            if msg.get("reasoning_content"):
                rec["note"] = "content empty; reasoning_content present"
            return ChatResult(
                False, error=f"budget_exhausted: empty content "
                             f"(finish_reason={fin})",
                call_record=rec)
        return ChatResult(True, raw=raw, call_record=rec)


class AnthropicPlanner(PlannerClient):
    backend = "api"

    def __init__(self, model: str):
        self.spec = f"api:anthropic:{model}"
        self.provider, self.model, self.env = "anthropic", model, \
            "ANTHROPIC_API_KEY"
        if not os.environ.get(self.env):
            raise ValueError("missing API key env var ANTHROPIC_API_KEY")

    def describe(self) -> dict:
        return {**super().describe(), "provider": "anthropic",
                "api_key_env": self.env,
                "seed_support": "unsupported by provider"}

    def chat(self, messages, sampling, replay_key=None) -> ChatResult:
        system = [m["content"] for m in messages if m["role"] == "system"]
        body = {"model": self.model,
                "messages": [m for m in messages if m["role"] != "system"],
                "temperature": sampling.temperature,
                "max_tokens": sampling.max_tokens}
        if system:
            body["system"] = "\n".join(system)
        rec = {"backend": "api", "provider": "anthropic",
               "model_id": self.model, "api_key_env": self.env,
               "params_sent": {"temperature": sampling.temperature,
                               "max_tokens": sampling.max_tokens},
               "seed_requested": sampling.seed,
               "seed_note": "seed unsupported by provider; not sent",
               "timestamp_utc": _now()}
        t0 = time.time()
        try:
            resp, rec["retries"] = _post_json_retry(
                "https://api.anthropic.com/v1/messages", body,
                {"x-api-key": os.environ[self.env],
                 "anthropic-version": "2023-06-01"})
        except _HTTPFailure as e:
            rec.update({"latency_ms": int((time.time() - t0) * 1000),
                        "retries": e.attempts,
                        "error_body": e.body})
            return ChatResult(False, error=f"HTTP {e.code}",
                              call_record=rec)
        except Exception as e:  # noqa: BLE001
            rec["latency_ms"] = int((time.time() - t0) * 1000)
            return ChatResult(False, error=type(e).__name__,
                              call_record=rec)
        rec.update({"latency_ms": int((time.time() - t0) * 1000),
                    "model_version": resp.get("model"),
                    "response_id": resp.get("id"),
                    "usage": resp.get("usage"),
                    "stop_reason": resp.get("stop_reason")})
        raw = "".join(b.get("text", "") for b in resp.get("content", [])
                      if b.get("type") == "text")
        return ChatResult(True, raw=raw, call_record=rec)


class MockPlanner(PlannerClient):
    """Replays saved outputs. ``replay_key`` is harness-defined:
    pilot -> (case_id, attempt); multistep -> (case_id, arm, turn).
    Loads pilot-v2 style ({cells:[...]}) and multistep style
    ({episodes:[...]}) trace files."""
    backend = "mock"

    def __init__(self, path: str):
        self.spec = f"mock:{path}"
        self.path = Path(path)
        data = json.loads(self.path.read_text())
        self.model = f"replay of {data.get('planner_config', {}).get('model') or 'saved outputs'}"
        self.table: dict[tuple, str] = {}
        if "cells" in data:
            for c in data["cells"]:
                if "raw_output" in c:
                    self.table[(c["case"], int(c["attempt"]))] = c["raw_output"]
        if "episodes" in data:
            for e in data["episodes"]:
                for a in e["attempts"]:
                    if "raw" in a:
                        self.table[(e["case"], e["arm"], int(a["turn"]))] = a["raw"]
        self.source_meta = {k: v for k, v in data.items()
                            if k not in ("cells", "episodes")}

    def describe(self) -> dict:
        return {**super().describe(), "replay_source": str(self.path),
                "replay_entries": len(self.table),
                "source_meta": self.source_meta}

    def chat(self, messages, sampling, replay_key=None) -> ChatResult:
        rec = {"backend": "mock", "model_id": self.model,
               "replay_key": list(replay_key) if replay_key else None,
               "params_requested": {"temperature": sampling.temperature,
                                    "max_tokens": sampling.max_tokens,
                                    "seed": sampling.seed,
                                    "think": sampling.think},
               "params_sent": {}, "timestamp_utc": _now(),
               "latency_ms": 0}
        if replay_key is None or tuple(replay_key) not in self.table:
            return ChatResult(False, error=f"no saved output for "
                              f"{replay_key}", call_record=rec)
        return ChatResult(True, raw=self.table[tuple(replay_key)],
                          call_record=rec)


def make_planner(spec: str) -> PlannerClient:
    kind, _, rest = spec.partition(":")
    if kind == "ollama" and rest:
        return OllamaPlanner(rest)
    if kind == "mock" and rest:
        return MockPlanner(rest)
    if kind == "api":
        provider, _, model = rest.partition(":")
        if not model:
            raise ValueError("api spec must be api:<provider>:<model>")
        if provider == "anthropic":
            return AnthropicPlanner(model)
        if provider in _OPENAI_COMPAT:
            return OpenAICompatPlanner(provider, model)
        raise ValueError(f"unknown provider {provider!r}; known: "
                         f"{sorted(_OPENAI_COMPAT) + ['anthropic']}")
    raise ValueError(f"bad planner spec {spec!r}; use ollama:<model>, "
                     "api:<provider>:<model>, or mock:<traces.json>")
