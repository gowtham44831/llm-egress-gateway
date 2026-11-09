# Which check stopped it? — artifact repository

Companion artifact for the paper **"Which check stopped it? Evaluating
egress defenses for LLM agents"** (working title; draft at
`docs/paper_draft.md`). A bounded laboratory experience report about an
egress-authorization gateway that sits between an unmodified, untrusted
LLM planner and outbound `url_fetch` calls: serialized-URL inspection,
bounded payload decoding, per-field owner/destination/purpose
authorization, and an independent loopback receiver as ground truth.

What the artifact supports:

- Per-call **deciding-check attribution** — which rule actually decided
  each outbound call, plus the minimal blocking arm — not aggregate
  block rates (`results/attribution_table.csv`, `docs/paper_counts.md`).
- Two live planners: **qwen3:14b** (frozen model-in-loop runs) and
  **gpt-6.1-sol** (second-planner replication under a frozen protocol,
  `runs/second_planner/`), and what changed when the model refused
  instead of probing the gateway (`docs/second_planner_report.md`).
- Two preserved failures: a missing-purpose context-plumbing block on a
  legitimate share, and an F5 sibling-carrier coverage defect found by
  receiver-side ground truth.
- Fictional data, mock receivers, local/API models under frozen
  protocols. **Not** a production system, an efficacy claim, or a
  prevention-rate measurement.

## Install

```bash
git clone https://github.com/gowtham44831/llm-egress-gateway
cd llm-egress-gateway
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .        # core; ".[data]" only needed to download ToolRet
```

Python 3.12. On macOS with a Homebrew Python that predates the OS,
`import xml.parsers.expat` can fail —
`brew install expat && export DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib`
(see `AGENTS.md`). Core deps: numpy, pandas, pydantic, PyYAML, pytest;
the milestone-1 stack (sentence-transformers/torch) is only needed for
the tool-routing pilot work, not the egress pipeline.

## Reproduce

```bash
make reproduce-tables   # regenerates every committed table/doc from the
                        # frozen traces and diffs against the committed
                        # reference outputs — read-only on inputs
python -m pytest -q     # 198 tests, no network, no model calls
```

`make reproduce-tables` runs `scripts/reproduce_tables.sh`: regenerates
`results/attribution_table*.csv`, `results/case_inventory.csv`,
`results/scenario_matrix.csv`, `docs/attribution_notes.md`,
`docs/paper_counts.md`, `docs/second_planner_report.md`, the labeling
packet and `prompts/`, diffs all of them against the committed versions,
verifies frozen-input sha256s, and smoke-tests the mock-replay path
into scratch output. A `PROTOCOL-DRIFT` note on two documents is
expected and documented (`ARTIFACTS.md` — "Protocol-document drift").

Live-model runs additionally need a local Ollama endpoint or a
`SECOND_PLANNER_*_API_KEY` environment variable (never recorded — see
`docs/second_planner_protocol.md`). The frozen traces committed under
`results/` and `runs/` are all that reproduction requires.

## Map: folders → paper sections

The authoritative claim→evidence map is **`ARTIFACTS.md`** (per claim,
per figure cell, with generator commands). Summary:

| Paper section | Primary artifacts |
|---|---|
| §3 gateway, F1–F5, task context | `src/tool_routing/argverify/url_fetch_gateway.py`, `planner_adapter.py`, `block_feedback.py`; `docs/binding_test_report.md` |
| §4 evaluation design (arms, cases, counting) | `scripts/run_*.py` runners; `src/tool_routing/argverify/fixtures/` case definitions; `docs/run_config.md` (sampling, seeds); protocol docs `docs/security_*protocol.md`, `docs/second_planner_protocol.md` + `*_FREEZE.md` |
| §5 Figure 1 + live-call table | `results/attribution_table.csv` (per run:case:arm:attempt deciding rule, minimal blocking arm, receiver receipt), `docs/paper_counts.md` (full + v2-only counts), `results/scenario_matrix.csv`, `results/case_inventory.csv` |
| §6.1 deciding-check lessons | `docs/attribution_notes.md`; `results/*/` per-harness traces |
| §6.2 missing-purpose failure | `results/planner_pilot_v2/` vs `results/planner_pilot_v2_adapter11/`; adapter code |
| §6.3 F5 defect + strict replay | `results/f5_coverage_repro/`, `results/demo_showcase/`; `docs/attribution_notes.md` §§4–5 (13 allows, 0 changed) |
| §7 second planner | `runs/second_planner/` (traces + manifests), `runs/second_planner_failed/` (preserved pre-output failures), `docs/second_planner_report.md`, `docs/second_planner_FREEZE.md` |
| Labels/prompts evidence | `labels/` (packet + unblinded key), `prompts/` (hash-verified prompt reconstruction) |
| Consistency audits | `docs/draft_consistency_report.md`, `docs/draft_consistency_report_v2.md` |

## Folders belonging to sibling projects

This is a lab monorepo; three sibling efforts share it. Their outputs
feed `results/attribution_table_other.csv`, so removing them would
break byte-identical reproduction — recommendation: **keep, clearly
labeled**, rather than strip (see decision below).

| Folder(s) | Project | Recommendation |
|---|---|---|
| `data/`, `configs/pilot_toolret.yaml`, `results/toolret_pilot`, `results/evaluation_audit`, `results/toy_smoke_test`, `src/tool_routing/{cli,data,evaluation,reporting,retrieval,scenarios,audit}`, `docs/toolret*`, `docs/evaluation_audit*`, `docs/review_workflow*` | ToolRet neural tool-routing pilot (milestone 1) | Keep — small tracked portion (`data/` stays git-ignored); feeds the out-of-scope table. Exclude only if shipping a paper-scoped subtree |
| `results/disclosure_*`, `docs/security_disclosure_*`, `docs/disclosure_*`, disclosure fixtures | Email-disclosure gateway evals | Keep — feeds `attribution_table_other.csv` |
| `results/argverify_*`, `docs/argument_verification_*`, `docs/argverify_*` | Argument-verification evals | Keep — same reason. **Note:** `src/tool_routing/argverify/` also hosts the paper's gateway code — never exclude it |
| `archive/` | Exploratory/closed directions | Keep — labeled archive, see `archive/README.md` |
| `artifacts/` | Curated copies of key `results/` dirs (from the earlier release checklist) | Keep as labeled copies; `results/` is now the tracked evidence base and the reproduction source |

## Licensing

- **Code** (`src/`, `scripts/`, `Makefile`): MIT — `LICENSE`.
- **Data, traces, and generated artifacts**: CC BY 4.0 — `DATA_LICENSE.md`.
- Vendored CaMeL policy components (`src/third_party/camel_policy/`):
  Apache-2.0, upstream `f083b6b` — `THIRD_PARTY_NOTICES`,
  `docs/camel_vendor_record.md`. Used for a component comparison only.

## Citation

See `CITATION.cff`. All personal data in this repository is fictional;
no real secrets, credentials, or network traffic are included.

### AI assistance

Developed with AI coding assistance (Devin, Cognition) for
implementation, harness code, and documentation drafting. Every
security-relevant claim traces to a frozen artifact; exploratory and
corrected work is labeled in `docs/STATUS.md` and
`docs/claim_to_evidence.md`.
