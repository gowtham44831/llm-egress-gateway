# Run configuration — url_fetch egress-gateway evaluation runs

Every value below is copied from a frozen artifact (`results/<run>/traces.json`,
`results/<run>/FREEZE.md`, `results/<run>/manifest.json`, or the fixture the run
loaded). Where a value is not present in any artifact it is written
**not recorded** — nothing here is inferred.

Hashes are sha256 of file contents. "current tree" = the hash of the file as it
exists in this checkout at package time (so a reviewer can detect drift).

## 0. Version identifiers (shared)

| component | id | where defined | hash (frozen) | hash (current tree) |
|---|---|---|---|---|
| gateway url-gw-1.0 | `url-gw-1.0` | `src/tool_routing/argverify/url_fetch_gateway.py` (F5 call-level accounting; the version every evaluation run executed) | `87598dfb53222f9dedef7be375c92ee6c622128c1a8e60e1ab19150ca94dfbb6` (every FREEZE.md) | superseded — see next row |
| gateway url-gw-1.1 | `url-gw-1.1` (`URL_GW_VERSION`), `f5_mode="strict"` default, `f5_mode="legacy"` reproduces 1.0 | same file | — | `f3dd7f8a6e203e3dd0d10919ff394dbaba462f392d6cbfcd03856b9fc9d1e27a` |
| planner-adapter | `planner-adapter-1.0` / `1.1` / `1.3` (`ADAPTER_VERSION`) | `src/tool_routing/argverify/planner_adapter.py` | 1.0 `ab702a19…`, 1.1 `e0b5496f…`, 1.3 `435e932b…` | `435e932b59fda0de6a2c2a1b6dd960a2eb01bfb11756d644e6d0acc67df6e48e` (1.3) |
| block feedback | `block-feedback-1.0` (`FEEDBACK_VERSION`) | `src/tool_routing/argverify/block_feedback.py` | `3bb0b741145f9b7178fde738baf5273e3c33765783de36b4957c81a05a7ac6e7` | same |
| receiver-side detector | `receiver_observe()` — own URL parse + base64 + JSON flatten, independent of the gateway matcher; **no version string** — identified by file hash | `scripts/run_url_eval_v2.py` | `3c3c75114e810298f0e6334f6265074e2f6b60e277dc8ae778874dfd3c8162f4` | same |
| M0–M3 arm definitions | `ARMS` dict | `scripts/run_url_eval_v2.py` | same file as above | same |
| CaMeL policy component | upstream commit `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8`, vendored at `src/third_party/camel_policy/` (import-path rewrite only); arm wrapper `camel-arms-1.0`; dep `pydantic==2.11.5` | `results/camel_component_eval/FREEZE.md`, `manifest.json` | per-file hashes in `manifest.json` | — |

Full lineage and the F5 defect narrative: `docs/version_notes.md`.

## 1. Model-in-the-loop runs

Common to all four: runtime `ollama` at `http://localhost:11434/api/chat`
(`stream=false`); prompt = one user-role message, **no system prompt** (see
`prompts/INDEX.md`). The runners sent only `temperature`, `num_predict`,
`seed`, `think`; every other sampling parameter came from the model's
Modelfile defaults. Hardware / OS: **not recorded**.

**Captured post hoc on 2026-11-07; assumed unchanged since the runs**
(the same machine and Ollama install; `ollama list` shows the model pulled
2026-10-19 22:34 local, i.e. before the first run on 2026-10-20, and the
short digest matches the fixture's `bdbd181c33f2`):

| item | value |
|---|---|
| `ollama --version` | `0.40.11` |
| model tag | `qwen3:14b` |
| manifest digest (the `ollama list` ID) | `sha256:bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8` |
| weights blob | `sha256:a8cc1361f3145dc01f6d77c6c82c9116b9ffe3c97b34716fe20418455876c40e` (9,276,184,896 bytes) |
| template / params / config layers | `ae370d88…` / `cff3f395…` / `78b3b822…` |
| architecture / size / quant | qwen3, 14.8B, Q4_K_M, GGUF, context length 40960 |
| Modelfile defaults inherited by the runs | `top_k 20`, `top_p 0.95`, `repeat_penalty 1`, stop `<|im_start|>` `<|im_end|>`; Modelfile `temperature 0.6` was **overridden** to 0.7 by the runners |

Whether the Ollama *server* binary at run time was 0.40.11 is **not
recorded** in any artifact; the value above is the binary present now.

### planner_pilot_v1 — `results/planner_pilot_v1/`

| item | value | source |
|---|---|---|
| planner model | `qwen3:14b` | `traces.json → planner_config.model` |
| model build | digest `bdbd181c33f2` (12-char short digest, recorded in the fixture **before** the run; the per-call `model_digest` field returned by ollama was not populated in traces). Full digest captured post hoc — see §1 header | `fixtures/planner_pilot_cases_v1.json → planner_config.digest` |
| temperature | 0.7 | `planner_config.options.temperature` |
| max tokens | `num_predict` 512 | `planner_config.options.num_predict` |
| seeds | 42, 43, 44 (attempt *i* → `seed_base`+*i*−1; 3 attempts/case) | `planner_config.seed_base`, `cells[].seed` |
| thinking | `think=false` | `planner_config.think` |
| cases | P-ID1, P-AD1, P-ID1-clean, P-AD1-clean, P-LC1 (+ DEV-0 smoke) | fixture |
| tool schema given to model | `url_fetch(url: string)` — model computes the URL (incl. base64) itself | `planner_config.tool_schema_given_to_model` |
| adapter version | **none** (no adapter in v1 — raw model URL checked directly) | `docs/version_notes.md §1` |
| runner version | `scripts/run_planner_pilot_v1.py` sha256 `e88fad0d8df55b707878e3b0c23636069da4fe351987e4703d952990e6347f47` (no version string) | `FREEZE.md`; matches current tree |
| gateway version | `url-gw-1.0`, `87598dfb…` | `FREEZE.md` |
| receiver/detector | `receiver_observe` from `run_url_eval_v2.py` `3c3c7511…` | `FREEZE.md` |
| fixture hash | `89e166a329de924e51c3c1f4877a2682b2e68c5af737e2f7d455bf8968711be7` | `FREEZE.md`; matches current tree |
| traces hash | `ac6aa6a34b966f6910ae53701b39d8469f3e8fa9584053e6962b7f6ee27be119` | `FREEZE.md`; matches current tree |

### planner_pilot_v2 — `results/planner_pilot_v2/`

| item | value | source |
|---|---|---|
| planner model / build | `qwen3:14b`, digest `bdbd181c33f2` (same caveat as v1) | `traces.json → planner_config` |
| temperature / max tokens / seeds / think | 0.7 / `num_predict` 512 / 42, 43, 44 / `false` | `planner_config`, `cells[].seed` |
| cases | P2-ID1, P2-AD1, P2-ID1-clean, P2-AD1-clean, P2-LC1 (+ DEV-1 smoke) | fixture |
| tool schema given to model | `url_fetch_struct(base_url, params)` — structured call, adapter serializes | `planner_config.tool_schema_given_to_model` |
| adapter version | `planner-adapter-1.0` (`ab702a19b33c7477d6584674b986627d0065c19eed45ceb1789eeb4b970447e6`) | `traces.json → adapter`, `FREEZE.md` |
| stated_purpose binding | hard-coded `"research_summary"` by the runner (`build_view`), not from a TaskContext — the cause of the P2-LC1 missing-purpose blocks | `scripts/run_planner_pilot_v1.py build_view` (imported by v2) |
| runner version | `scripts/run_planner_pilot_v2.py` `66acb1423eef8e8583e36887c9698f9959ffe95747058e5752f93d020299cb75` | `FREEZE.md`; matches current tree |
| gateway version | `url-gw-1.0`, `87598dfb…` | `FREEZE.md` (via `run_url_eval_v2.py` ARMS) |
| receiver/detector | `receiver_observe`, `3c3c7511…` | — |
| fixture hash | `3fb88c61caee7840c1dc2db1253f0e479778993e1113f3b0d5834bd6dfc87e22` | `FREEZE.md`; matches current tree |
| traces hash | `b32b5d9b1b8d18b82d7e55b24a47067ad3904cc473f22478e5a206eb83bbc74f` | `FREEZE.md`; matches current tree |

### planner_pilot_v2_adapter11 — `results/planner_pilot_v2_adapter11/` (replay, no model calls)

| item | value | source |
|---|---|---|
| planner model | **n/a** — replays the saved v2 model outputs (`results/planner_pilot_v2/traces.json`) | `FREEZE.md` |
| adapter version | `planner-adapter-1.1` (`e0b5496f3a5e8a254658f456b8741c424311a7056006060076df79081264d7d8`); `stated_purpose` from application `TaskContext` (`purpose_source=task_context`) | `traces.json[].adapter`, `FREEZE.md` |
| URL identity check | `url_unchanged_vs_v2 = true` on every cell | `traces.json` |
| runner version | `scripts/replay_planner_pilot_v2_adapter11.py` `493f1c9eb42c273e171aacd05a88facac2c540cebfc91856618206703868bd1b` | `FREEZE.md`; matches current tree |
| gateway version | `url-gw-1.0` | `docs/version_notes.md` |
| traces hash | `48053942410b2bc77773381266ce543cab73389b439f61936c343538f77dde64` | `FREEZE.md`; matches current tree |

### multistep_pilot (v1) — `results/multistep_pilot/`

| item | value | source |
|---|---|---|
| planner model / build | `qwen3:14b` (`model_returned` confirmed per episode); digest `bdbd181c33f2` from fixture (full digest: post hoc, §1 header) | `episodes[].model_settings_effective`, fixture `planner_config.digest` |
| temperature / max tokens | 0.7 / `num_predict` 512 | `model_settings_effective.options_sent` |
| seeds | one seed per episode, same seed across the 4 arms: MS-ID1 42, MS-AD1 43, MS-ID1-clean 44, MS-LC1 45, MS-LC2 46, MS-LC3 47 | `episodes[].seed` |
| thinking | `think=false` | `model_settings_effective.think_sent` |
| turn budget | 4 | fixture `planner_config.turn_budget` |
| arms | M0_no_gateway, M1_allowlist, M2_content_inspect, M3_full_gateway; 24 episodes | fixture, traces |
| tool schema | contract A (`multistep-cases-1.0`) | fixture `planner_config.tool_schema_given_to_model` |
| adapter version | `planner-adapter-1.3` (`435e932b…`), `ContextIssuer` binding | `traces.json → adapter`, `FREEZE.md` |
| feedback version | `block-feedback-1.0` | `traces.json → feedback` |
| runner version | `scripts/run_multistep_pilot.py` `2cf636b29f7a8e39c0cc5805591b90de7733d9cf6e929466423be5af30b868bf` — **this is the pre-v1.1 runner; the current tree holds the v1.1 runner `088fa6b1…` used for multistep_pilot_v2**. Known trace gap: `binding_reject` turns lack raw model output | `FREEZE.md` |
| gateway version | `url-gw-1.0`, `87598dfb…` | `FREEZE.md` |
| fixture hash | `5bd9b0f55156184f9110b050bbdb993bf8b1aa0f2ca9b46bb9a63f63d368e486` | `FREEZE.md`; matches current tree |
| traces hash | `dce0556287781ac2920bb3e84f87725a4d6da615e14652454901b2666b07c98e` | `FREEZE.md` (prefix); matches current tree |

### multistep_pilot_v2 — `results/multistep_pilot_v2/`

| item | value | source |
|---|---|---|
| planner model / build | `qwen3:14b`; digest `bdbd181c33f2` from fixture (full digest: post hoc, §1 header) | as v1 |
| temperature / max tokens / think | 0.7 / 512 / `false` | `model_settings_effective` |
| seeds | 42–47, same mapping as v1 | `episodes[].seed` |
| turn budget / arms | 4 / M0–M3, 24 episodes | fixture |
| tool schema | contract B (example-based), `multistep-cases-2.0` — development-informed change validated on `interface_dev` (7/7 vs 4/7) | fixture, `FREEZE.md` |
| adapter / feedback | `planner-adapter-1.3` / `block-feedback-1.0` | `traces.json` |
| runner version | `scripts/run_multistep_pilot.py` v1.1 `088fa6b13079a0d99de713928bf57e01eab51b9a689de6da141b9e9f448b6de5` (raw output saved before parse/bind on every turn) | `FREEZE.md`; matches current tree |
| gateway version | `url-gw-1.0`, `87598dfb…` | `FREEZE.md` |
| fixture hash | `b9fe54a006643a979007f2060ebfa3e703492809852e1c5a4af85b47e40a967b` | `FREEZE.md`; matches current tree |
| traces hash | `c8ed8fec10d2c0bc7e77522d66a0c4123375e1dd2efe0fa7fc1a86510774df04` | `FREEZE.md`; matches current tree |

### second_planner runs — `runs/second_planner/*/` (configurable planner)

Produced by `scripts/run_second_planner.py` under the frozen
`docs/second_planner_protocol.md`. Every turn records a `call` object:
model id as sent, model build (Ollama digest via `/api/tags`, or API
model version + system_fingerprint), `params_sent`, UTC timestamp,
latency, usage — plus the full `raw` output on every turn (including
adapter/binding/malformed rejects).

| run dir | harness | planner spec | backend | model identity / version | sampling actually sent | seeds | f5 | notes |
|---|---|---|---|---|---|---|---|---|
| `pilot_dryrun` | pilot | `mock:results/planner_pilot_v2/traces.json` | mock | replay of `qwen3:14b` (saved outputs; no live model, no digest) | none sent — replay only; requested `temperature 0.7`, `num_predict 512`, `think false` | 42,43,44 (as frozen) | legacy (`url-gw-1.0`) | mandatory pre-run dry run; 967/967 checks matched frozen decisions |
| `multistep_dryrun` | multistep | `mock:results/multistep_pilot_v2/traces.json` | mock | replay of `qwen3:14b` (saved outputs) | none sent — replay only; requested `temperature 0.7`, `num_predict 512`, `think false` | 42–47 (as frozen) | legacy (`url-gw-1.0`) | same dry-run verification |
| `pilot_api_openai_gpt-6.1-sol` | pilot | `api:openai:gpt-6.1-sol` | api | `gpt-6.1-sol`; `model_version` in responses = `gpt-6.1-sol`; `system_fingerprint` = null (not returned) | `max_completion_tokens` 2048, `seed`, `reasoning_effort=low` (probe: none/minimal rejected); **no temperature** (default 1) | 42,43,44 (as frozen) | legacy (`url-gw-1.0`) | Amendment 1 deviations; calls 2026-11-09 UTC; 0 retries, 0 errors, `reasoning_tokens`=0 reported |
| `multistep_api_openai_gpt-6.1-sol` | multistep | `api:openai:gpt-6.1-sol` | api | `gpt-6.1-sol`; `model_version` in responses = `gpt-6.1-sol`; `system_fingerprint` = null | `max_completion_tokens` 2048, `seed`, `reasoning_effort=low`; **no temperature** | 42–47 (as frozen) | legacy (`url-gw-1.0`) | Amendment 1 deviations; calls 2026-11-09 UTC |

The first real second-planner runs are the two `api:openai:gpt-6.1-sol`
rows above (2026-11-09 UTC, planner-client-1.1 under Amendment 1).
Every call's `params_sent`, `model_version`, `system_fingerprint`,
`finish_reason`, `reasoning_tokens`, `completion_tokens`, `retries`,
and full error body (if any) are recorded in the traces' `call`
objects. Any further live run belongs in this table, read from the
run's `manifest.json`/`traces.json` call records — never retyped.

#### Failed attempts — `runs/second_planner_failed/` (preserved, read-only)

| run dir | planner spec | date | failure |
|---|---|---|---|
| `pilot_gpt-6.1-sol_http429_2026-11-08` | `api:openai:gpt-6.1-sol` | 2026-11-08 | every call HTTP 429 (no quota); error records only, no model output |
| `pilot_gpt-6.1-sol_http400_2026-11-08` | `api:openai:gpt-6.1-sol` | 2026-11-08 | every call HTTP 400 (`max_tokens` unsupported); error records only |

**planner-client-1.1 (Amendment 1, 2026-11-08)** applies to
`api:openai` only — provider-forced deviations from the qwen settings,
all fixed before any model output: `max_completion_tokens=2048`
(max_tokens rejected; covers hidden reasoning + visible answer),
temperature omitted (only default 1 accepted; qwen used 0.7), seed
kept, `reasoning_effort` = lowest accepted of none/minimal/low probed
once at startup. Per call also records `finish_reason`,
`reasoning_tokens`, `completion_tokens`, full error body, and a
`retries` log (429/5xx, backoff, max 5). `finish_reason=length`/empty
content is flagged `budget_exhausted`, never an abstention. See
`docs/second_planner_protocol.md` Amendment 1.

## 2. Scripted (no-model) runs

| run | script (hash) | fixture / input | gateway | adapter | detector | traces hash |
|---|---|---|---|---|---|---|
| `url_eval_v2` | `scripts/run_url_eval_v2.py` `3c3c7511…` | `fixtures/url_eval_cases_v2.json` `e5b5abf4de72e92be914d3872b74492204faf3e3aa41e1b7908af56707650f67` | `url-gw-1.0` `87598dfb…` | none (scripted URLs) | `receiver_observe` (same file) | `6fc298a95c6340f4eeba8792008b49ac183924ffbcba2d0d173c2bf933b38144` |
| `eval_v4` | `scripts/run_eval_v4.py` `75361cd56b0835ba6fdb8272f8e813db97517af10fcb849159e3d8d5aa62db92` | cases inline in script (`CASES`), protocol `docs/security_eval_v4_protocol.md` `cbc0307b…` | `url-gw-1.0` | `planner-adapter-1.3` `435e932b…` | `receiver_observe` | `9f6f626f88a3cc59c55a9f98c8ce6e0ff237fbe643e9bdcafcc6c4a37efef0b3` |
| `camel_component_eval` | `scripts/run_camel_component_eval.py` `14eb6109…` | `results/eval_v4/traces.json` (saved serialized requests) | M3 rerun `url-gw-1.0` | — | — | `2218d7f2ad6de176403603f34057f02854b82731e6ea77a7820aa5d402f4d36e` |
| `url_gw_isolation` | `scripts/run_url_fetch_isolation.py` `88896471…` | controls inline (U1–U3, preserved_*) | `url-gw-1.0` (`manifest.json → module`) | none | script-local receiver | `85d0ba211601cab9b243a1834260798b3242cf49a32a0ff575117dd7bc855145` |
| `f5_coverage_repro` (legacy / strict) | `scripts/repro_f5_coverage.py` (hash **not recorded** — no FREEZE.md) | `TRACES` inline (T1, T2, T3a, T3b) | `url-gw-1.1` module, `f5_mode="legacy"` / `"strict"` | — | script-local `_Sink` + reconstruction | **not recorded** |
| `demo_showcase` | `scripts/demo_showcase.py` (hash **not recorded**) | scenes inline (S1, S2, S3 legacy/strict) | `url-gw-1.1` (`traces.json → note`) | — | script-local | **not recorded** |

Clock used by all scripted runs and replays: `CLOCK = "2026-10-21T09:00:00"`
(fixed; permission `not_after` = `2027-01-01`).

## 3. Derived artifacts (deterministic, read-only on the above)

| artifact | script | inputs |
|---|---|---|
| `results/attribution_table.csv`, `attribution_table_other.csv`, `case_inventory.csv`, `scenario_matrix.csv`, `docs/attribution_notes.md` | `scripts/attribution_table.py` | all `results/**/*.json*`, fixtures, `run_eval_v4.py`/`run_url_fetch_isolation.py` case defs, gateway module (deterministic replay for unrecorded rules; strict-F5 replay of allows) |
| `docs/paper_counts.md` | `scripts/paper_counts.py` | `results/attribution_table.csv` |
| `labels/*.csv`, `labels/excluded.md` | `scripts/make_labeling_packet.py` | same as attribution_table + fixtures |
| `prompts/` | `scripts/export_prompts.py` | fixtures + runner templates + multistep `feedback_sent` |
