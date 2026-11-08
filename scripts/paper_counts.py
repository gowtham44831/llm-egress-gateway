#!/usr/bin/env python3
"""Live-call attribution counts for the url_fetch egress paper,
per planner model (never pooled across planners).

Reads results/attribution_table.csv (read-only) and emits
docs/paper_counts.md. One column per ``planner`` value — frozen runs
are qwen3:14b; runs/second_planner/* carry their own recorded planner
identity. The counting rule is identical for every column.

Counting rule (deciding-mechanism attribution of model-generated calls):
  * universe: rows with call_origin=model-generated, run_tag=evaluation,
    arm in {M3_full_gateway}, outcome in {allow, block}, turn=0
  * unit: one generated call = (run, case_id, attempt_id, turn).
    planner_pilot_v2_adapter11 replays the SAME saved v2 calls through
    adapter-1.1 and is therefore excluded from call counts (it is
    reported under the qwen planner only in the corrected-allow row).
  * attack calls (scenario families ID / AD) are attributed to the
    M3-recorded deciding rule family:
      host  = deciding_rule starts with fetch_host_offlist
      auth  = deciding_rule starts with no_authorization
      F5    = deciding_rule starts with unaccounted_payload
  * prohibited proposals = legitimate-task cases (MS-LC*) whose
    generated call was blocked (any rule)
  * missing-purpose blocks = P2-LC1 M3 blocks with no_authorization
    (planner_pilot_v2 for qwen; the equivalent cells for a
    second-planner pilot run)
  * corrected allows = P2-LC1 M3 allows (adapter-1.1 replay for qwen;
    adapter-1.3 context binding for second-planner pilot runs)
  * not exercised = turn-0 planner-run rows where no fetch decision
    exists: pilot cells with emitted:none / planner_error outcomes, or
    multistep turn-0 attempts whose outcome is not a fetch allow/block
    (respond / request_permission / malformed / rejects). Counted per
    (run, case, attempt/episode-arm) — a planner that never proposes a
    fetch gives the gateway nothing to decide.

Usage: python scripts/paper_counts.py [--out PATH] [--include-mock]

--include-mock admits mock:-backend (dry-run replay) second-planner
runs as planner columns; those artifacts are smoke-test material only
and must go to a scratch --out, never the committed doc. Without the
flag, mock planners are excluded even if present in the table.

Output format: the original single-column table when exactly one
planner is counted (byte-identical to the pre-second-planner doc);
one column per planner once a real second-planner run exists.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = Path(os.environ.get("ATTRIB_TABLE")
             or ROOT / "results/attribution_table.csv")
DEFAULT_OUT = ROOT / "docs/paper_counts.md"

ATTACK_PREFIX = ("P-ID", "P2-ID", "P-AD", "P2-AD", "MS-ID", "MS-AD")
LEGIT_PREFIX = ("MS-LC",)
PLANNER_ORDER = ("qwen3:14b",)  # frozen planner first, then sorted


def _fam(rule: str) -> str:
    for k, pre in (("host", "fetch_host_offlist"),
                   ("auth", "no_authorization"),
                   ("F5", "unaccounted_payload")):
        if rule.startswith(pre):
            return k
    return "other"


def _is_pilot_run(run: str) -> bool:
    base = run.split("/")[0]
    return (base.startswith("planner_pilot")
            or run in _PILOT_SP_RUNS)


_PILOT_SP_RUNS: set[str] = set()   # filled from the table's planner col


def counts_for(planner: str, rows: list[dict]) -> dict:
    own = [r for r in rows if r["planner"] == planner]
    live = [r for r in own
            if r["call_origin"] == "model-generated"
            and r["run_tag"] == "evaluation"
            and r["arm"] == "M3_full_gateway"
            and r["outcome"] in ("allow", "block")
            and r["turn"] == "0"
            and r["run"] != "planner_pilot_v2_adapter11"]

    def clean(cid: str) -> bool:
        return cid.endswith("-clean")

    attack = [r for r in live if r["case_id"].startswith(ATTACK_PREFIX)
              and not clean(r["case_id"]) and r["outcome"] == "block"]
    fam: dict[str, list] = {"host": [], "auth": [], "F5": [], "other": []}
    for r in attack:
        fam[_fam(r["deciding_rule"])].append(r)
    prohibited = [r for r in live
                  if r["case_id"].startswith(LEGIT_PREFIX)
                  and r["outcome"] == "block"]
    missing_purpose = [r for r in live
                       if r["case_id"] == "P2-LC1"
                       and r["outcome"] == "block"
                       and r["deciding_rule"].startswith(
                           "no_authorization")]
    corrected = [r for r in own
                 if r["case_id"] == "P2-LC1"
                 and r["arm"] == "M3_full_gateway"
                 and r["outcome"] == "allow"
                 and r["call_origin"] == "model-generated"
                 and r["run_tag"] == "evaluation"
                 and r["turn"] == "0"]
    not_exercised = [r for r in own
                     if r["call_origin"] == "model-generated"
                     and r["run_tag"] == "evaluation"
                     and r["turn"] == "0"
                     and r["outcome"] not in ("allow", "block")
                     and r["run"] != "planner_pilot_v2_adapter11"
                     and (_is_pilot_run(r["run"])
                          or r["arm"] != "UNRECORDED")]
    return {"host": fam["host"], "auth": fam["auth"], "F5": fam["F5"],
            "other": fam["other"], "attack_total": attack,
            "prohibited": prohibited, "missing_purpose": missing_purpose,
            "corrected": corrected, "not_exercised": not_exercised}


def _lst(rs) -> str:
    return ", ".join(f"{r['run']}:{r['case_id']}#a{r['attempt_id']}"
                     f"t{r['turn']}"
                     for r in sorted(rs, key=lambda x: (
                         x["run"], x["case_id"], x["attempt_id"],
                         x["turn"])))


def _calls(rs, with_turn: bool) -> str:
    return ", ".join(f"{r['run']}:{r['case_id']}#a{r['attempt_id']}"
                     + (f"t{r['turn']}" if with_turn else "")
                     for r in sorted(rs, key=lambda x: (
                         x["run"], x["case_id"], x["attempt_id"],
                         x["turn"])))


def main() -> None:
    include_mock = "--include-mock" in sys.argv
    table = Path(sys.argv[sys.argv.index("--table") + 1]) \
        if "--table" in sys.argv else TABLE
    out = DEFAULT_OUT
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    if include_mock and out.resolve() == DEFAULT_OUT.resolve():
        sys.exit("--include-mock output is smoke-test material only — "
                 "pass --out pointing at a scratch path")
    rows = list(csv.DictReader(table.open()))
    if not include_mock:
        rows = [r for r in rows
                if not r["planner"].startswith("mock(")]
    _PILOT_SP_RUNS.update(
        r["run"] for r in rows
        if r["planner"] not in ("", "n/a", "qwen3:14b")
        and r["harness"] == "url_fetch_gateway")
    planners = sorted({r["planner"] for r in rows} -
                      {"", "n/a"},
                      key=lambda p: (p not in PLANNER_ORDER, p))
    per = {p: counts_for(p, rows) for p in planners}

    QUANT = [("blocked attack calls decided by host filter", "host"),
             ("blocked attack calls decided by authorization", "auth"),
             ("blocked attack calls decided by F5 content coverage",
              "F5"),
             ("blocked attack calls, other rule", "other"),
             ("prohibited proposals on legitimate tasks (blocked)",
              "prohibited"),
             ("missing-purpose blocks (P2-LC1 M3, no_authorization)",
              "missing_purpose"),
             ("P2-LC1 M3 allows (purpose-bound correction)",
              "corrected"),
             ("planner calls not exercised (no fetch decision)",
              "not_exercised")]

    if len(planners) == 1:
        # original single-planner format — byte-identical to the doc
        # frozen before the second-planner harness work
        p = planners[0]
        c = per[p]
        md = ["# Live-call attribution counts (generated)", "",
              "Source: `results/attribution_table.csv` via "
              "`scripts/paper_counts.py` (counting rule in the script "
              "docstring). Regenerate: `python scripts/paper_counts.py`.",
              "",
              "| quantity | count | calls |",
              "|---|---|---|",
              f"| blocked attack calls decided by host filter | "
              f"{len(c['host'])} | {_calls(c['host'], False)} |",
              f"| blocked attack calls decided by authorization | "
              f"{len(c['auth'])} | {_calls(c['auth'], False)} |",
              f"| blocked attack calls decided by F5 content coverage"
              f" | {len(c['F5'])} | {_calls(c['F5'], False)} |",
              f"| blocked attack calls, other rule | "
              f"{len(c['other'])} | {_calls(c['other'], False)} |",
              f"| prohibited proposals on legitimate tasks (blocked)"
              f" | {len(c['prohibited'])} | "
              f"{_calls(c['prohibited'], False)} |",
              f"| missing-purpose blocks (planner_pilot_v2 P2-LC1 M3)"
              f" | {len(c['missing_purpose'])} | "
              f"{_calls(c['missing_purpose'], False)} |",
              f"| ... corrected to allow by adapter-1.1 replay | "
              f"{len(c['corrected'])} | "
              f"{_calls(c['corrected'], False)} |",
              "",
              f"Total model-generated M3-gated attack calls counted: "
              f"{len(c['attack_total'])}. Note: the host-filter "
              "decision is also the `minimal_blocking_arm` (M1) for "
              "every host-decided call; the auth-decided P2-AD1 calls "
              "have minimal_blocking_arm = M2 (protected_match) — see "
              "docs/attribution_notes.md §4."]
    else:
        md = ["# Live-call attribution counts (generated)", "",
              "Source: `results/attribution_table.csv` via "
              "`scripts/paper_counts.py` (counting rule in the script "
              "docstring). Regenerate: `python scripts/paper_counts.py`.",
              "",
              "One column per planner identity; counts are never "
              "pooled across planners. qwen3:14b covers the frozen "
              "model-in-loop runs (planner_pilot_v1/v2, "
              "multistep_pilot v1/v2); second-planner runs get their "
              "own column(s).",
              "",
              "| quantity | " + " | ".join(planners) + " |",
              "|---|" + "---|" * len(planners)]
        for label, key in QUANT:
            md.append(f"| {label} | " +
                      " | ".join(str(len(per[p][key]))
                                for p in planners) + " |")
        md += ["",
               "Model-generated M3-gated attack calls counted per "
               "planner: " + "; ".join(
                   f"`{p}` {len(per[p]['attack_total'])}"
                   for p in planners) + ".",
               "",
               "Note: the host-filter decision is also the "
               "`minimal_blocking_arm` (M1) for every host-decided "
               "call; the auth-decided P2-AD1 calls have "
               "minimal_blocking_arm = M2 (protected_match) — see "
               "docs/attribution_notes.md §4.",
               ""]
        for p in planners:
            md.append(f"## {p}")
            md.append("")
            for label, key in QUANT:
                rs = per[p][key]
                if rs:
                    md.append(f"- {label} ({len(rs)}): {_lst(rs)}")
            md.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n")
    q = planners[0]
    print(" / ".join(f"{k} {len(per[q][k])}"
                    for k in ("host", "auth", "F5", "other")) +
          f"; prohibited {len(per[q]['prohibited'])}; missing-purpose "
          f"{len(per[q]['missing_purpose'])}"
          + "".join(f" | {p}: host {len(per[p]['host'])} / auth "
                    f"{len(per[p]['auth'])} / F5 {len(per[p]['F5'])} / "
                    f"other {len(per[p]['other'])}; prohibited "
                    f"{len(per[p]['prohibited'])}; missing-purpose "
                    f"{len(per[p]['missing_purpose'])}; not-exercised "
                    f"{len(per[p]['not_exercised'])}"
                    for p in planners[1:])
          + f" -> {out}")


if __name__ == "__main__":
    main()
