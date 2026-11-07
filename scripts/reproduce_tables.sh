#!/usr/bin/env bash
# Regenerate every derived table/figure-data/labeling artifact for the
# url_fetch egress paper from FROZEN traces only, into a scratch dir, and
# diff each against the committed/on-disk version. Exit non-zero on any
# difference. Never writes under results/; never calls a model.
#
# Usage: scripts/reproduce_tables.sh            (or: make reproduce-tables)
#        KEEP=1 scripts/reproduce_tables.sh     keep the scratch dir
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
PY="${PYTHON:-python3}"

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/repro_tables.XXXXXX")"
[ -n "${KEEP:-}" ] || trap 'rm -rf "$SCRATCH"' EXIT
mkdir -p "$SCRATCH/attrib" "$SCRATCH/labels" "$SCRATCH/prompts" "$SCRATCH/docs"
fail=0

step() { printf '\n== %s\n' "$*"; }
cmp_file() {  # cmp_file <regenerated> <reference>
  if [ ! -f "$2" ]; then
    echo "MISSING reference: $2"; fail=1; return
  fi
  if diff -q "$1" "$2" >/dev/null; then
    echo "ok       $2"
  else
    echo "DIFFERS  $2"; fail=1
    diff -u "$2" "$1" | head -40
  fi
  if git check-ignore -q "$2" 2>/dev/null; then
    echo "   note: $2 is git-ignored — reference is the on-disk copy, not a committed file"
  fi
}

step "1. attribution_table.py -> attribution_table.csv, attribution_table_other.csv, case_inventory.csv, scenario_matrix.csv (Figure 1 data), attribution_notes.md (incl. F5 strict replay, minimal blocking arm)"
ATTRIB_OUT="$SCRATCH/attrib" "$PY" scripts/attribution_table.py >"$SCRATCH/attrib.log" 2>&1 \
  || { echo "attribution_table.py FAILED"; cat "$SCRATCH/attrib.log"; fail=1; }
for f in attribution_table.csv attribution_table_other.csv case_inventory.csv scenario_matrix.csv; do
  cmp_file "$SCRATCH/attrib/$f" "results/$f"
done
cmp_file "$SCRATCH/attrib/attribution_notes.md" "docs/attribution_notes.md"

step "2. paper_counts.py -> docs/paper_counts.md (live-call attribution counts)"
# computed from the freshly regenerated table so step 1 and 2 are coupled
"$PY" - "$SCRATCH" <<'EOF' || fail=1
import sys, runpy, pathlib
scratch = pathlib.Path(sys.argv[1])
import importlib.util
spec = importlib.util.spec_from_file_location("pc", "scripts/paper_counts.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
pc.TABLE = scratch / "attrib/attribution_table.csv"
sys.argv = ["paper_counts.py", "--out", str(scratch / "docs/paper_counts.md")]
pc.main()
EOF
cmp_file "$SCRATCH/docs/paper_counts.md" "docs/paper_counts.md"

step "3. make_labeling_packet.py -> labels/{packet,key,diagnostic_packet,recovery_packet}.csv, excluded.md"
LABELS_OUT="$SCRATCH/labels" "$PY" scripts/make_labeling_packet.py >"$SCRATCH/labels.log" 2>&1 \
  || { echo "make_labeling_packet.py FAILED"; cat "$SCRATCH/labels.log"; fail=1; }
for f in packet.csv key.csv diagnostic_packet.csv recovery_packet.csv excluded.md; do
  cmp_file "$SCRATCH/labels/$f" "labels/$f"
done

step "4. export_prompts.py -> prompts/ (byte-identical turn-0 prompts + multistep feedback)"
"$PY" scripts/export_prompts.py --out "$SCRATCH/prompts" >"$SCRATCH/prompts.log" 2>&1 \
  || { echo "export_prompts.py FAILED"; cat "$SCRATCH/prompts.log"; fail=1; }
if diff -rq "$SCRATCH/prompts" prompts >/dev/null; then
  echo "ok       prompts/ ($(find prompts -type f | wc -l | tr -d ' ') files)"
else
  echo "DIFFERS  prompts/"; diff -rq "$SCRATCH/prompts" prompts | head -20; fail=1
fi

step "5. frozen-input integrity (sha256 vs results/*/FREEZE.md)"
"$PY" - <<'EOF' || fail=1
import hashlib, re, sys, pathlib
root = pathlib.Path(".")
# runs the paper draws on (url_eval_v1 is superseded; disclosure_* / mnd
# runs are a different project line)
# url_eval_v1 is superseded by v2 but its FREEZE pins journal_research_plan.md,
# so it is included for protocol/plan-drift visibility
RUNS = ("url_eval_v1", "url_eval_v2", "eval_v4", "camel_component_eval", "url_gw_isolation",
        "planner_pilot_v1", "planner_pilot_v2", "planner_pilot_v2_adapter11",
        "multistep_pilot", "multistep_pilot_v2")
# versioned code whose drift is documented in docs/version_notes.md
VERSIONED = ("url_fetch_gateway.py", "planner_adapter.py")
bad = 0
proto: list = []
for run in RUNS:
    fz = root / "results" / run / "FREEZE.md"
    if not fz.exists():
        print(f"no FREEZE.md     results/{run}"); continue
    txt = fz.read_text()
    pairs = [(m.group(1), m.group(2)) for m in re.finditer(
        r'"?([\w./-]+\.(?:py|json|md))"?[`:| ]+\s*"?([0-9a-f]{64})"?', txt)]
    pairs += [(m.group(2), m.group(1)) for m in re.finditer(   # `hash`  path
        r'`([0-9a-f]{64})`\s+([\w./-]+\.(?:py|json|md))', txt)]
    for p, h in pairs:
        f = root / p
        if not f.exists() or "REPORT" in p or "FREEZE" in p:
            continue
        cur = hashlib.sha256(f.read_bytes()).hexdigest()
        if cur == h:
            continue
        if p.endswith(VERSIONED):
            tag = "versioned-drift"       # see docs/version_notes.md
        elif run == "multistep_pilot" and p.endswith("run_multistep_pilot.py"):
            tag = "versioned-drift"       # v1 ran pre-1.1 runner; tree holds v1.1 (docs/run_config.md)
        elif p.startswith("docs/") and ("protocol" in p or "plan" in p):
            tag = "PROTOCOL-DRIFT"        # protocol/plan doc changed since freeze — always visible
            proto.append(p)
        elif p.startswith(("tests/", "docs/")):
            tag = "info-drift"            # tests/docs, not run inputs
        else:
            tag = "DRIFT"; bad += 1       # runner/fixture/trace changed
        print(f"{tag:15} {p}  frozen={h[:12]} current={cur[:12]}  ({run})")
print("frozen-input check:", "ok (runner scripts, fixtures, traces all match FREEZE.md)"
      if not bad else f"{bad} unexpected drift(s)")
if proto:
    print(f"PROTOCOL-DRIFT: {len(proto)} protocol/plan document(s) differ from their "
          f"freeze hash: {', '.join(sorted(set(proto)))} — see ARTIFACTS.md "
          "'Protocol-document drift' (does not fail the target)")
sys.exit(1 if bad else 0)
EOF

echo
if [ "$fail" -eq 0 ]; then
  echo "reproduce-tables: ALL OUTPUTS MATCH"
else
  echo "reproduce-tables: FAILED (see DIFFERS/MISSING/DRIFT above)"
fi
[ -n "${KEEP:-}" ] && echo "scratch kept at $SCRATCH"
exit "$fail"
