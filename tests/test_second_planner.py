"""Second-planner harness tests — no model calls, no network.

Covers planner spec parsing, mock replay keying, API-key handling
(only the env-var NAME is ever recorded), per-call provenance fields,
raw-output persistence on adapter/binding rejects (the R5 gap), and
f5_mode arm selection (legacy == url-gw-1.0 evaluated behavior).
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from tool_routing.argverify import planner_client as pc  # noqa: E402
from tool_routing.argverify.planner_client import (  # noqa: E402
    MockPlanner, OpenAICompatPlanner, Sampling, make_planner)


def _runner():
    spec = importlib.util.spec_from_file_location(
        "run_second_planner", ROOT / "scripts/run_second_planner.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------ spec parse

def test_spec_parsing():
    assert make_planner("ollama:qwen3:14b").backend == "ollama"
    assert make_planner("ollama:qwen3:14b").model == "qwen3:14b"
    with pytest.raises(ValueError):
        make_planner("bogus")
    with pytest.raises(ValueError):
        make_planner("api:openai")           # missing model
    with pytest.raises(ValueError):
        make_planner("api:nosuchprovider:m")  # unknown provider


def test_api_requires_key_env(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        make_planner("api:openai:gpt-4o")


def test_api_record_has_env_name_not_key(monkeypatch):
    secret = "sk-test-SECRET-value-12345"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    monkeypatch.setattr(pc, "_post_json", lambda *a, **k: {
        "model": "gpt-4o-2026-01-01", "id": "chatcmpl-x",
        "system_fingerprint": "fp_abc",
        "usage": {"total_tokens": 9},
        "choices": [{"message": {"content": "{\"tool\":\"none\"}"},
                     "finish_reason": "stop"}]})
    cl = make_planner("api:openai:gpt-4o")
    res = cl.chat([{"role": "user", "content": "hi"}],
                  Sampling(seed=42))
    assert res.ok and res.raw == '{"tool":"none"}'
    rec = res.call_record
    blob = json.dumps(rec) + json.dumps(cl.describe())
    assert secret not in blob
    assert rec["api_key_env"] == "OPENAI_API_KEY"
    assert rec["model_version"] == "gpt-4o-2026-01-01"
    assert rec["params_sent"]["seed"] == 42
    assert "timestamp_utc" in rec


# ------------------------------------------------ planner-client-1.1
# (Amendment 1, api:openai only)

import io  # noqa: E402
import urllib.error  # noqa: E402


def _http_err(code, body=b'{"error": {"message": "bad"}}'):
    return urllib.error.HTTPError("u", code, "m", {}, io.BytesIO(body))


def _ok_resp(content="resp", finish="stop"):
    return {"model": "m-v1", "id": "r1",
            "usage": {"completion_tokens": 7,
                      "completion_tokens_details":
                          {"reasoning_tokens": 3}},
            "choices": [{"message": {"content": content},
                         "finish_reason": finish}]}


def test_openai_params_and_effort_probe(monkeypatch):
    """1.1: max_completion_tokens=2048, no temperature, seed kept,
    reasoning_effort = first accepted of none/minimal/low."""
    probe_seen, chat_seen = [], []
    monkeypatch.setenv("OPENAI_API_KEY", "k")

    def fake(url, body, headers, timeout=180):
        if body.get("max_completion_tokens") == 16:
            probe_seen.append(body.get("reasoning_effort"))
        else:
            chat_seen.append(dict(body))
        return _ok_resp()

    monkeypatch.setattr(pc, "_post_json", fake)
    cl = make_planner("api:openai:gpt-x")
    res = cl.chat([{"role": "user", "content": "hi"}], Sampling(seed=7))
    assert res.ok
    rec = res.call_record
    p = rec["params_sent"]
    assert "temperature" not in p
    assert p["max_completion_tokens"] == 2048
    assert p["seed"] == 7
    assert p["reasoning_effort"] == "none"
    assert probe_seen == ["none"]          # probed once, cached
    assert rec["reasoning_tokens"] == 3
    assert rec["completion_tokens"] == 7
    cl.chat([{"role": "user", "content": "again"}], Sampling(seed=8))
    assert probe_seen == ["none"]          # no second probe


def test_openai_effort_probe_fallback(monkeypatch):
    """none/minimal rejected -> low sent; probe results recorded."""
    monkeypatch.setenv("OPENAI_API_KEY", "k")

    def fake(url, body, headers, timeout=180):
        if body.get("max_completion_tokens") == 16:
            eff = body["reasoning_effort"]
            if eff in ("none", "minimal"):
                raise _http_err(400)
        return _ok_resp()

    monkeypatch.setattr(pc, "_post_json", fake)
    cl = make_planner("api:openai:gpt-x")
    rec = cl.chat([], Sampling(seed=1)).call_record
    assert rec["params_sent"]["reasoning_effort"] == "low"
    statuses = [p.get("status") for p in rec["reasoning_effort_probe"]]
    assert statuses == [400, 400, "accepted"]
    assert rec["reasoning_effort_probe"][0]["error_body"]


def test_openai_retry_429_then_ok(monkeypatch):
    """HTTP 429 retried with exponential backoff; every try recorded."""
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    sleeps, calls = [], []
    monkeypatch.setattr(pc.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(pc, "_post_json", lambda *a, **k: _ok_resp())

    def fake(url, body, headers, timeout=180):
        if body.get("max_completion_tokens") == 16:
            return _ok_resp()          # probe accepted immediately
        calls.append(1)
        if len(calls) <= 2:
            raise _http_err(429)
        return _ok_resp()

    monkeypatch.setattr(pc, "_post_json", fake)
    cl = make_planner("api:openai:gpt-x")
    rec = cl.chat([], Sampling(seed=1)).call_record
    assert [t["status"] for t in rec["retries"]] == [429, 429]
    assert rec["retries"][0]["error_body"]
    assert sleeps == [1.0, 2.0]


def test_openai_error_body_and_no_retry_on_400(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setattr(pc.time, "sleep", lambda s: None)
    calls = []
    monkeypatch.setattr(pc, "_post_json",
                        lambda *a, **k: calls.append(1)
                        or _ok_resp())

    def fake(url, body, headers, timeout=180):
        if body.get("max_completion_tokens") == 16:
            return _ok_resp()          # probe accepts
        calls.append(1)
        raise _http_err(400, b'{"error":{"param":"max_tokens"}}')

    monkeypatch.setattr(pc, "_post_json", fake)
    cl = make_planner("api:openai:gpt-x")
    res = cl.chat([], Sampling(seed=1))
    assert not res.ok and res.error == "HTTP 400"
    assert res.call_record["error_body"] == \
        '{"error":{"param":"max_tokens"}}'
    assert len(calls) == 1             # 400 is not retried


def test_openai_budget_exhausted(monkeypatch):
    """finish_reason=length or empty content -> budget_exhausted,
    never an abstention (flagged on the call record)."""
    monkeypatch.setenv("OPENAI_API_KEY", "k")

    def stub(resp):
        def fake(url, body, headers, timeout=180):
            return resp
        monkeypatch.setattr(pc, "_post_json", fake)

    cl = make_planner("api:openai:gpt-x")
    stub(_ok_resp("partial", "length"))
    rec = cl.chat([], Sampling(seed=1)).call_record
    assert rec["budget_exhausted"] is True
    stub(_ok_resp("", "length"))
    res = cl.chat([], Sampling(seed=1))
    assert not res.ok and "budget_exhausted" in res.error
    assert res.call_record["budget_exhausted"] is True


# ---------------------------------------------------------------- mock

def test_mock_replay_keying(tmp_path):
    f = tmp_path / "t.json"
    f.write_text(json.dumps({"cells": [
        {"case": "C1", "attempt": 1, "raw_output": "OUT1"},
        {"case": "C1", "attempt": 2, "raw_output": "OUT2"}],
        "episodes": [{"case": "E1", "arm": "M0", "attempts": [
            {"turn": 0, "raw": "T0"}, {"turn": 1, "raw": "T1"}]}]}))
    m = MockPlanner(str(f))
    assert m.chat([], Sampling(), replay_key=("C1", 1)).raw == "OUT1"
    assert m.chat([], Sampling(), replay_key=("C1", 2)).raw == "OUT2"
    assert m.chat([], Sampling(), replay_key=("E1", "M0", 1)).raw == "T1"
    miss = m.chat([], Sampling(), replay_key=("E1", "M0", 9))
    assert not miss.ok and "no saved output" in miss.error


# -------------------------------------------------------- reject records

class _FixedPlanner:
    """Stand-in that returns a fixed raw string per turn."""
    def __init__(self, raws):
        self.raws, self.calls = raws, 0

    def chat(self, messages, sampling, replay_key=None):
        raw = self.raws[min(self.calls, len(self.raws) - 1)]
        self.calls += 1
        return pc.ChatResult(True, raw=raw, call_record={
            "backend": "mock", "model_id": "toy",
            "params_sent": {}, "timestamp_utc": "2026-01-01T00:00:00"})


def _toy_case():
    return {"case_id": "TOY-1", "task": "t",
            "retrieved_content": [],
            "context_purpose": "research_summary",
            "policy": {"allowlist": ["docs.example"],
                       "directory": {}, "records": []}}


def _toy_cfg():
    return {"prompt_template": "{tool_schema} {task} {material}",
            "tool_schema_given_to_model": "schema",
            "options": {"temperature": 0.7, "num_predict": 512},
            "think": False, "turn_budget": 2, "arms": ["M3_full_gateway"],
            "seed_base": 42}


def test_raw_saved_on_adapter_reject():
    rs = _runner()
    # base_url not http -> adapter (schema) reject; planner then responds
    planner = _FixedPlanner([
        json.dumps({"tool": "url_fetch_struct", "base_url": "notaurl",
                    "params": {"a": "b"}}),
        json.dumps({"tool": "respond", "answer": "ok"})])
    ep = rs.run_episode(_toy_case(), "M3_full_gateway", _toy_cfg(), 42,
                        planner, rs.arms("legacy"), "legacy",
                        verify_prompts=False)
    a0 = ep["attempts"][0]
    assert a0["reject_kind"] == "schema"
    assert a0["raw"] and "notaurl" in a0["raw"]   # R5 gap closed
    assert a0["structured"]["base_url"] == "notaurl"
    assert ep["attempts"][1]["action"] == "respond"


def test_raw_saved_on_malformed_and_fetch():
    rs = _runner()
    planner = _FixedPlanner([
        "this is not json at all",
        json.dumps({"tool": "url_fetch_struct",
                    "base_url": "http://docs.example/x",
                    "params": {"a": "b"}})])
    ep = rs.run_episode(_toy_case(), "M3_full_gateway", _toy_cfg(), 42,
                        planner, rs.arms("legacy"), "legacy",
                        verify_prompts=False)
    a0, a1 = ep["attempts"]
    assert a0["malformed"] == "no_json" and a0["raw"] == \
        "this is not json at all"          # raw kept on malformed turn
    assert a1["action"] == "fetch" and a1["raw"]
    assert a1["decision"] in ("allow", "block")
    # a block on a fetch gets a fixed feedback string, never the values
    if a1["decision"] == "block":
        assert "blocked" in a1["feedback_sent"]


# --------------------------------------------------------------- f5 mode

def _f5_view():
    return {
        "acting_principal": "vic.tim",
        "policy": {"fetch_allowlist": ["docs.example"]},
        "directory": {"docs.example": {"principal": "docs.svc",
                                       "class": "external_known"}},
        "permission_records": [],
        "field_metadata": {
            "doc.title": {"owner": "docs.svc", "class": "public",
                          "provenance": "tool.t1.output.title"}},
        "conversation": [],
        "retrieved_content": [{"call_id": "t1", "tool": "read",
                               "output": {"title": "Quarterly"}}],
        "planner_call": {
            "tool": "url_fetch",
            # one carrier whose atoms are [matched, junk]:
            # strict F5 -> unaccounted_payload; legacy -> suppressed
            "arguments": {"url": "http://docs.example/x?d=" + __import__(
                "base64").b64encode(
                    b'{"t":"Quarterly","junk":"unseen"}').decode()},
            "payload_fields": ["doc.title"],
            "stated_purpose": "research_summary"},
        "planner_claims": {}}


def test_f5_mode_selection():
    rs = _runner()
    v = _f5_view()
    legacy = rs.arms("legacy")["M3_full_gateway"](v)
    strict = rs.arms("strict")["M3_full_gateway"](v)
    assert legacy["execution"] == "allow"     # evaluated url-gw-1.0 defect
    assert strict["execution"] == "block"     # url-gw-1.1 coverage fix
    assert any(f["finding"] == "unaccounted_payload"
               for f in strict["findings"])
    with pytest.raises(KeyError):
        rs.arms("legacy")["M4_bogus"]
