# ARTIFACTS — reproducibility package for the url_fetch egress-gateway paper

Paper: `docs/journal_draft.md` (frozen; not modified by this package).
Run configuration (model build, sampling, versions, hashes): `docs/run_config.md`.
Prompts: `prompts/` + `prompts/INDEX.md`. Version lineage: `docs/version_notes.md`.

**One command checks everything derivable:**

```bash
make reproduce-tables        # = bash scripts/reproduce_tables.sh
```

It regenerates every derived artifact below from frozen traces into a scratch
dir, diffs each against the on-disk version, verifies frozen inputs against
`results/*/FREEZE.md` hashes, and exits non-zero on any difference. No model
calls, no network, nothing written under `results/`.

All commands run from the repo root. `PYTHONPATH=src` is required for anything
that imports `tool_routing`. Unless stated, inputs are **read-only frozen traces**.

Legend — *Regen class*:
- **D** deterministic from frozen traces (what `make reproduce-tables` checks)
- **S** scripted, deterministic, re-runnable (no model) but *would rewrite* `results/<run>/` — not run by the target
- **M** requires the live model (ollama qwen3:14b) — **not regenerable**; frozen trace shipped

---

## 1. Figure 1 — scenario × harness matrix

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/attribution_table.py` |
| script | `scripts/attribution_table.py` (`main()` → matrix block) |
| inputs | every `results/**/*.json*`; case definitions from `src/tool_routing/argverify/fixtures/{url_eval_cases_v2,planner_pilot_cases_v1,planner_pilot_cases_v2,multistep_cases_v1,multistep_cases_v2,interface_dev_cases_v1}.json`, `scripts/run_eval_v4.py::CASES`, `scripts/run_url_fetch_isolation.py::controls()` |
| output | `results/scenario_matrix.csv` — rows = `scenario_family`, cols = harness (plus `pilot_v2_<planner>` / `multistep_v2_<planner>` when real second-planner runs exist), cells = case IDs |
| regen | **D** |
| note | The draft contains **no rendered figure**; this CSV is the figure data. No plotting script exists for it. |

## 2. Live-call attribution counts (host 5 / auth 3 / F5 2; 3 prohibited proposals; 3 missing-purpose blocks)

| | |
|---|---|
| command | `python scripts/paper_counts.py` |
| script | `scripts/paper_counts.py` — counting rule in the docstring; one column per `planner` identity, never pooled across models |
| inputs | `results/attribution_table.csv` (incl. `runs/second_planner/*` rows) |
| output | `docs/paper_counts.md` |
| regen | **D** — reproduces exactly: host 5, auth 3, F5 2, other 0; prohibited 3; missing-purpose 3 (+3 corrected by adapter-1.1) |
| rule | model-generated, evaluation-run, M3 rows, turn 0, one unit per `(run, case, attempt)`; `planner_pilot_v2_adapter11` excluded from call counts (replays the same saved calls). host = `fetch_host_offlist*`, auth = `no_authorization*`, F5 = `unaccounted_payload*`. Prohibited proposals = blocked MS-LC1/2/3 calls. Missing-purpose = `planner_pilot_v2` P2-LC1 M3 `no_authorization` blocks. |
| caveat | These strings do not appear verbatim in `docs/journal_draft.md`; the script pins the rule so the numbers are not hand-counted. A different unit (per case rather than per attempt) gives host 3, not 5. |

## 3. R1–R6 result tables

The markdown tables in the draft were **transcribed by hand** from the run
REPORTs; no script renders them. Every cell is traceable as follows (checked
in `docs/draft_consistency_report.md`).

| table | draft lines | frozen source (numbers as printed) | producing script / command | inputs | regen |
|---|---|---|---|---|---|
| R1 synthetic controls (20 cells) | L87–100 | `results/url_eval_v2/REPORT.md`, `REPORT_v2.md` (authorized/unauthorized rescore), `traces.json` | `PYTHONPATH=src python scripts/run_url_eval_v2.py` | `fixtures/url_eval_cases_v2.json` | **S** — rows also in `results/attribution_table.csv` (`run=url_eval_v2`). The rescore is hard-coded in `attribution_table.py` (`V2_UNAUTHORIZED`/`V2_AUTHORIZED`); raw trace flags conflate receipt with unauthorized. |
| R2 planner pilot v1 (15 attempts) | L102–116 | `results/planner_pilot_v1/REPORT.md`, `traces.json` | `PYTHONPATH=src python scripts/run_planner_pilot_v1.py` | `fixtures/planner_pilot_cases_v1.json`, live ollama | **M** — counts derivable from `attribution_table.csv` (`run=planner_pilot_v1`) |
| R3 structured pilot v2 + adapter-1.1 | L118–163 | `results/planner_pilot_v2/REPORT.md`, `results/planner_pilot_v2_adapter11/REPORT.md`, both `traces.json` | gen: `PYTHONPATH=src python scripts/run_planner_pilot_v2.py`; replay: `PYTHONPATH=src python scripts/replay_planner_pilot_v2_adapter11.py` | `fixtures/planner_pilot_cases_v2.json`; replay reads `results/planner_pilot_v2/traces.json` | gen **M**; replay **S**. Grid cells in `attribution_table.csv` (`run=planner_pilot_v2*`). |
| R4 eval-v4 (8 cases × 4 arms, CB1–CB6) | L165–189 | `results/eval_v4/REPORT.md`, `traces.json` (`cb_checks` has 7 records incl. `CB3_context_purpose_wins`) | `PYTHONPATH=src python scripts/run_eval_v4.py` | cases inline in script | **S** — rows in `attribution_table.csv` (`run=eval_v4`) |
| R5 multi-step v1 (24 episodes) | L202–224 | `results/multistep_pilot/REPORT.md`, `ANALYSIS.md`, `traces.json` | `PYTHONPATH=src python scripts/run_multistep_pilot.py` | `fixtures/multistep_cases_v1.json`, live ollama | **M** — episode rows in `attribution_table.csv` (`run=multistep_pilot`). Trace gap: `binding_reject` turns lack raw output (listed in `labels/excluded.md`). |
| R6 multi-step v2 (contract B) | L226–257 | `results/multistep_pilot_v2/REPORT.md`, `ANALYSIS.md`, `traces.json` | `PYTHONPATH=src python scripts/run_multistep_pilot.py --v2` | `fixtures/multistep_cases_v2.json`, live ollama | **M** — rows in `attribution_table.csv` (`run=multistep_pilot_v2`) |

## 4. CaMeL component comparison (R4 second table, L191–200; "8/8 agree")

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/run_camel_component_eval.py` |
| script | `scripts/run_camel_component_eval.py` + `src/tool_routing/argverify/camel_policy_arm.py` (`camel-arms-1.0`) |
| inputs | `results/eval_v4/traces.json` (saved serialized requests); vendored CaMeL `src/third_party/camel_policy/` @ upstream `f083b6b3…`; `pydantic==2.11.5` |
| output | `results/camel_component_eval/{traces.json,REPORT.md,manifest.json}` |
| regen | **S** (rewrites `results/camel_component_eval/`); rows also in `results/attribution_table.csv` (`run=camel_component_eval`). Excluded from the labeling packet by design (policy re-evaluation, no new deliveries). |

## 5. F5 strict replay of the full-gateway allows

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/attribution_table.py` |
| script | `scripts/attribution_table.py::_strict_check` (and `_legacy_check` for the reverse direction) |
| inputs | every frozen-run `M3_full_gateway` / `full_gateway` / `M3_full_gateway_rerun` **allow** row; reconstructs the serialized call and re-runs `check_fetch_call(..., f5_mode="strict")` through the current `url_fetch_gateway.py` (url-gw-1.1) |
| output | `docs/attribution_notes.md` §5 — 10 allow rows, **0 flagged** (none blocks under strict; no unauthorized receipt) |
| regen | **D** |
| related | F5 defect reproduction itself: `results/f5_coverage_repro/REPORT.md`, `traces_{legacy,strict}.json` from `PYTHONPATH=src python scripts/repro_f5_coverage.py [--strict]` (**S**; no FREEZE.md — script hash *not recorded*). |

## 6. attribution_table.csv and case_inventory.csv

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/attribution_table.py` |
| script | `scripts/attribution_table.py` |
| inputs | as §1 **plus** real (non-mock) `runs/second_planner/*/traces.json` (read-only; §9) — same columns, plus a `planner` column (`qwen3:14b` for frozen model runs, the recorded planner identity for second-planner runs); deterministic gateway replay for rows whose deciding rule is not in the trace (`rule_source=replay` vs `trace`). `mock:`-backend dry runs are **excluded** unless `--include-mock` is passed (scratch-only output — see §9) |
| outputs | `results/attribution_table.csv` (348 rows, in-scope harnesses), `results/attribution_table_other.csv` (3,904 rows), `results/case_inventory.csv` (52 cases), `results/scenario_matrix.csv` (harness columns **plus** `pilot_v2_<planner>` / `multistep_v2_<planner>` when real second-planner runs exist), `docs/attribution_notes.md` |
| regen | **D** |
| note | `results/` is git-ignored (`.gitignore:17`), so these CSVs are **not committed**; `make reproduce-tables` diffs against the on-disk copies and prints a note. To make them a committed reference: `git add -f results/attribution_table.csv results/attribution_table_other.csv results/case_inventory.csv results/scenario_matrix.csv` (or relocate). |

## 7. Labeling packet

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/make_labeling_packet.py` |
| script | `scripts/make_labeling_packet.py` (imports `attribution_table.py`) |
| inputs | frozen traces for planner_pilot_v1/v2(+adapter11), multistep_pilot(+v2), url_eval_v2, eval_v4, url_gw_isolation, f5_coverage_repro, demo_showcase; fixtures and `run_eval_v4.py` / `run_url_eval_v2.build_concrete` for permission context; seeded shuffle `Random(20260215)` |
| outputs | `labels/packet.csv` (blinded, 49 items: 22 A_planner_output + 27 B_receipt), `labels/key.csv` (unblinded mapping), `labels/diagnostic_packet.csv` (6, `LBL-D01–D06`), `labels/recovery_packet.csv` (20 turn≥1 rows, unblinded), `labels/excluded.md` (60 binding-reject trace-gap rows + camel drop note) |
| regen | **D** |

## 8. Prompts

| | |
|---|---|
| command | `PYTHONPATH=src python scripts/export_prompts.py` |
| inputs | `run_planner_pilot_v1.PROMPT_TEMPLATE`, fixture `prompt_template` / `planner_config.tool_schema_given_to_model`, case `task` + `retrieved_content`; multistep `feedback_sent` from traces |
| outputs | `prompts/<run>/<CASE>.prompt.txt`, `.injection.txt` / `.email_body.txt`, `<CASE>.<arm>.feedback.json`; `prompts/INDEX.md` |
| regen | **D** — traces did not store prompt text; reconstruction is byte-identical because runner scripts and fixtures hash-match FREEZE.md (caveats in `prompts/INDEX.md`) |

## 9. Second-planner replication harness (mock-verified; no real planner run yet)

| | |
|---|---|
| protocol | `docs/second_planner_protocol.md` (**FROZEN**; sha256 pinned in `docs/second_planner_FREEZE.md`, re-checked by the runner at startup) |
| runner | `scripts/run_second_planner.py` — `--harness pilot\|multistep`, `--planner ollama:<m>\|api:<provider>:<m>\|mock:<traces>`, `--f5 legacy\|strict` (default legacy = url-gw-1.0 as evaluated) |
| planner client | `src/tool_routing/argverify/planner_client.py` — per-call record: model id, digest/version string, every sampling param sent, UTC timestamp, latency; API keys come from `*_API_KEY` env vars and only the env-var NAME is ever recorded |
| dry run | `… --planner mock:results/planner_pilot_v2/traces.json` (pilot), `… mock:results/multistep_pilot_v2/traces.json` (multistep); outputs under `runs/second_planner/` (git-ignored, never under `results/`) |
| verify | `python scripts/verify_second_planner_dryrun.py --pilot runs/second_planner/pilot_dryrun --multistep runs/second_planner/multistep_dryrun` — 967 checks: per-cell/per-turn decisions vs frozen references + counts + `paper_counts.md` regeneration |
| last verify | `ALL 967 CHECKS PASS` (pilot vs adapter-1.1 cells; multistep vs v2 episodes; new-run counts equal frozen-reference counts) |
| attribution | `scripts/attribution_table.py` ingests real (non-mock) `runs/second_planner/*/traces.json` as `pilot_v2_<planner>` / `multistep_v2_<planner>` harness_runs — same columns (`deciding_rule`, `minimal_blocking_arm`, `receiver_receipt`, `call_origin`, `attempt_id`, `turn`, `gateway_version`) + `planner`. `mock:` dry runs are excluded from the default outputs; `--include-mock --out <scratch>` reruns the pipeline on them for verification only (never writes `results/` or `docs/`) |
| counts | `scripts/paper_counts.py` → `docs/paper_counts.md`: identical counting rule per planner model, separate columns once a real second-planner run exists, never pooled across models; single-column legacy format while only qwen3:14b exists |
| report | `scripts/second_planner_report.py` → `docs/second_planner_report.md` (default: no real runs → "none found"): unauthorized M3 receipts, deciding-check diffs vs qwen3:14b (same-scenario, split planner vs interface/mechanism), abstain/malformed/refusal rates; `--include-mock` for the dry-run smoke version |
| smoke | `make reproduce-tables` step 2c reruns all three generators with `--include-mock` into scratch and checks the mock rows flow through — exercised every run, never diffed against paper outputs |

Deliberate differences from the frozen v1-trace format: **full** raw
planner output on every turn (incl. binding/adapter/malformed rejects —
closes the R5 gap), per-call provenance, `deciding_check`,
`receiver_receipt`, and `legitimate_delivery_episode` fields.
Everything else is byte-identical (prompts hash-verified against
`prompts/`, same arms/receiver/CLOCK, block-feedback-1.0, seeds,
temperature 0.7, num_predict 512).

---

## What cannot be reproduced from this repo, and why

| item | reason |
|---|---|
| Model outputs in `planner_pilot_v1`, `planner_pilot_v2`, `multistep_pilot`, `multistep_pilot_v2` (and `interface_dev`) | Need live ollama `qwen3:14b` digest `bdbd181c33f2`; sampling at temperature 0.7 is not bit-reproducible across builds/hardware even with the recorded seeds. Frozen `traces.json` shipped and hash-pinned. |
| Full model digest / ollama server version / hardware | **Not recorded** in any artifact (only the 12-char short digest, written pre-run in the fixture; per-call `model_digest` field is `null` in traces). |
| Raw model output on `binding_reject` turns (multistep_pilot v1: MS-ID1, MS-LC1/2/3 — 60 rows) | Pre-1.1 runner did not store it. Listed in `labels/excluded.md`; cannot be recovered. |
| Follow-up feedback messages after binding/adapter/malformed rejects | Generated at run time but not stored (`feedback_sent` recorded only after gateway blocks). |
| Intermediate assistant turns in multistep traces | Stored truncated to 400 chars. |
| The multistep_pilot (v1) runner as executed (`2cf636b2…`) | Overwritten in-tree by runner v1.1 (`088fa6b1…`); FREEZE.md records the hash only. Turn-0 prompt is fixture-templated so still reconstructible. |
| `f5_coverage_repro`, `demo_showcase` script/trace hashes | No FREEZE.md was written for these diagnostic runs. |
| The url-gw-1.0 gateway source as executed | Current tree is url-gw-1.1 (`f3dd7f8a…`); 1.0 behavior is available only via `f5_mode="legacy"`, which `attribution_table.py` uses for legacy replays. The frozen 1.0 file (`87598dfb…`) is not in the tree. |
| Rendered Figure 1 and the R1–R6 markdown tables | No plotting/table-rendering script exists; data is in `results/scenario_matrix.csv` and `results/attribution_table.csv`. |
| `docs/security_eval_v4_protocol.md` at freeze hash `cbc0307b…`; `docs/journal_research_plan.md` at `a1215d79…` | Current files differ (`5e6faf50…`, `fbb092b2…`). The frozen versions are **not recoverable** — see next section. Reported by `make reproduce-tables` as `PROTOCOL-DRIFT`. |

## Protocol-document drift (unresolved)

Two documents pinned by FREEZE manifests no longer match their frozen hash:

| document | frozen in | frozen sha256 | current sha256 |
|---|---|---|---|
| `docs/security_eval_v4_protocol.md` | `results/eval_v4/FREEZE.md` | `cbc0307bb8df…` | `5e6faf505b5d…` |
| `docs/journal_research_plan.md` | `results/url_eval_v1/FREEZE.md` | `a1215d79b300…` | `fbb092b251aa…` |

**The diff cannot be produced.** Each file has exactly one commit in git
history (`cba34e3`, 2026-10-21 18:24 −04:00, "Milestones 2+ …"), and that
commit's blob *is* the current content. The pre-edit version was never
committed; there are no stashes and no dangling blobs matching either
frozen hash (`git fsck --lost-found` scanned). Consequently the changes
**cannot be classified** as editorial vs substantive from repository
evidence, and no commit date for the edit exists — only filesystem
mtimes:

| file | mtime | related freeze / run mtime | gap |
|---|---|---|---|
| `docs/security_eval_v4_protocol.md` | 2026-10-20 19:03 | `results/eval_v4/{FREEZE.md,traces.json}` 2026-10-20 19:03 | same minute as the run — consistent with a post-run touch (e.g. appending a status line), but unverifiable |
| `docs/journal_research_plan.md` | 2026-10-20 18:28 | `results/url_eval_v1/FREEZE.md` 2026-10-20 18:17 | 11 min after the (unrun) v1 freeze; v1 was then superseded by url_eval_v2 |

What *is* verifiable: the executed inputs for eval_v4 (runner `75361cd5…`,
gateway `87598dfb…` via legacy mode, adapter `435e932b…`, traces
`9f6f626f…`) all match their FREEZE hashes, and the current
`security_eval_v4_protocol.md` states expected outcomes that agree with
`results/eval_v4/REPORT.md` and the R4 table. Whether the *frozen* text
stated the same expectations cannot be shown. Treat the eval_v4
"expectations frozen before execution" claim as **author-asserted, not
hash-verifiable** in the paper's limitations.

## Last run of `make reproduce-tables`

```
== 1. attribution_table.py          ok ×5 (4 CSVs + docs/attribution_notes.md; mock runs excluded by default)
== 2. paper_counts.py               ok   host 5 / auth 3 / F5 2 / other 0; prohibited 3; missing-purpose 3
== 2b. second_planner_report.py     ok   docs/second_planner_report.md (no real runs -> "none found")
== 2c. --include-mock smoke test    ok   all 3 generators -> scratch; mock wiring exercised, never diffed
== 3. make_labeling_packet.py       ok ×5
== 4. export_prompts.py             ok   prompts/ (53 files)
== 5. frozen-input integrity        ok   runner scripts, fixtures, traces all match FREEZE.md
     PROTOCOL-DRIFT  docs/journal_research_plan.md      frozen=a1215d79b300 current=fbb092b251aa  (url_eval_v1)
     PROTOCOL-DRIFT  docs/security_eval_v4_protocol.md  frozen=cbc0307bb8df current=5e6faf505b5d  (eval_v4)
     (versioned-drift: url_fetch_gateway 1.0→1.1, planner_adapter →1.3, run_multistep_pilot v1→v1.1)
== 6. second-planner freeze         ok ×14 (protocol + runner + client + verifier + 10 frozen inputs)
reproduce-tables: ALL OUTPUTS MATCH      exit 0
```
