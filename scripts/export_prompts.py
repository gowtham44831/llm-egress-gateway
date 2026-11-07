#!/usr/bin/env python3
"""Export the exact planner prompts used by the model-in-the-loop runs.

Read-only on results/. No model calls.

The runs did not store the prompt text in traces.json; they built it at
call time from a template + the frozen case fixture:

  planner_pilot_v1 / v2 : run_planner_pilot_v1.PROMPT_TEMPLATE.format(
      tool_schema=planner_config["tool_schema_given_to_model"],
      task=case["task"],
      material=json.dumps(case["retrieved_content"], indent=1))
    (run_planner_pilot_v2 imports call_planner from v1 -> same template)
  multistep_pilot / _v2  : manifest["prompt_template"].format(...) same args

Both runner scripts and all four fixtures hash-match their FREEZE.md
records (see docs/run_config.md), so the reconstruction here is
byte-identical to what the runs sent. The whole prompt was sent as ONE
user-role message; no system prompt was used (verified against
call_planner / call_turn in the runner scripts).

Outputs, one file per case ID per run under prompts/<run>/:
  <CASE>.prompt.txt            turn-0 user message (byte-identical)
  <CASE>.injection.txt         injected read_email body (attack cases)
  <CASE>.email_body.txt        benign read_email body (clean/legit cases)
  <CASE>.<arm>.feedback.json   multistep only: recorded follow-up user
                               messages per turn (feedback_sent, verbatim
                               from traces) — assistant turns are stored
                               truncated to 400 chars in the traces and
                               are NOT reproduced here
and prompts/INDEX.md mapping files -> runs.

Usage: PYTHONPATH=src python scripts/export_prompts.py [--out DIR]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "src/tool_routing/argverify/fixtures"
RES = ROOT / "results"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from run_planner_pilot_v1 import PROMPT_TEMPLATE as PILOT_TEMPLATE  # noqa: E402

ATTACK_SUITES = {"incident_derived_adapted", "adapted_simulation",
                 "attack", "incident_derived", "adapted"}


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _email_body(case: dict) -> str | None:
    for rc in case.get("retrieved_content", []):
        if rc.get("tool") == "read_email":
            return rc.get("output", {}).get("body")
    return None


def _is_attack(case: dict) -> bool:
    cid = case["case_id"]
    if cid.endswith("-clean") or "-LC" in cid or cid.startswith("DEV"):
        return False
    return (case.get("suite") in ATTACK_SUITES
            or cid.split("-")[-1][:2] in ("ID", "AD"))


def _emit(out: Path, run: str, case: dict, template: str, schema: str,
          smoke: bool, idx: list, feedback: dict | None = None) -> None:
    d = out / run
    d.mkdir(parents=True, exist_ok=True)
    cid = case["case_id"]
    prompt = template.format(
        tool_schema=schema, task=case["task"],
        material=json.dumps(case["retrieved_content"], indent=1))
    (d / f"{cid}.prompt.txt").write_text(prompt)
    files = [f"{cid}.prompt.txt"]
    body = _email_body(case)
    if body is not None:
        name = (f"{cid}.injection.txt" if _is_attack(case)
                else f"{cid}.email_body.txt")
        (d / name).write_text(body)
        files.append(name)
    for arm, turns in (feedback or {}).items():
        if turns:
            name = f"{cid}.{arm}.feedback.json"
            (d / name).write_text(json.dumps(turns, indent=1))
            files.append(name)
    idx.append({"run": run, "case_id": cid, "smoke": smoke,
                "suite": case.get("suite", ""), "files": files,
                "prompt_sha256_16": _sha(prompt),
                "attack": _is_attack(case)})


def main() -> None:
    out = ROOT / "prompts"
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    idx: list[dict] = []

    # ---- planner pilots (one-step) ----
    for run, fx in (("planner_pilot_v1", "planner_pilot_cases_v1.json"),
                    ("planner_pilot_v2", "planner_pilot_cases_v2.json")):
        m = json.loads((FIX / fx).read_text())
        schema = m["planner_config"]["tool_schema_given_to_model"]
        tr = json.loads((RES / run / "traces.json").read_text())
        assert tr["planner_config"]["tool_schema_given_to_model"] == schema, \
            f"{run}: trace schema != fixture schema"
        for grp in ("attack_cases", "clean_counterparts",
                    "legitimate_cases"):
            for c in m.get(grp, []):
                _emit(out, run, c, PILOT_TEMPLATE, schema, False, idx)
        if (RES / run / "traces_smoke.json").exists():
            _emit(out, run, m["dev_case"], PILOT_TEMPLATE, schema, True, idx)

    # ---- multistep pilots ----
    for run, fx in (("multistep_pilot", "multistep_cases_v1.json"),
                    ("multistep_pilot_v2", "multistep_cases_v2.json")):
        m = json.loads((FIX / fx).read_text())
        schema = m["planner_config"]["tool_schema_given_to_model"]
        template = m["prompt_template"]
        tr = json.loads((RES / run / "traces.json").read_text())
        fb: dict[str, dict[str, list]] = {}
        for ep in tr["episodes"]:
            turns = [{"turn": a["turn"], "user_message": a["feedback_sent"]}
                     for a in ep["attempts"] if "feedback_sent" in a]
            fb.setdefault(ep["case"], {})[ep["arm"]] = turns
        for c in m["episodes"]:
            _emit(out, run, c, template, schema, False, idx,
                  feedback=fb.get(c["case_id"]))
        if (RES / run / "traces_smoke.json").exists():
            _emit(out, run, m["dev_episode"], template, schema, True, idx)

    # ---- INDEX.md ----
    md = ["# Prompt index", "",
          "Generated by `scripts/export_prompts.py` (read-only on "
          "results/; no model calls).", "",
          "**System prompt:** none. Every run sent exactly one user-role "
          "message at turn 0 (`run_planner_pilot_v1.call_planner`, "
          "`run_multistep_pilot.call_turn`); the `tool_schema` text is "
          "embedded in that message.", "",
          "**Byte identity:** prompts are reconstructed from the frozen "
          "template + fixture; traces did not store prompt text. Runner "
          "scripts and fixtures hash-match FREEZE.md (docs/run_config.md "
          "§hashes), so the reconstruction is what the runs sent. "
          "Multistep follow-up `*.feedback.json` files are copied "
          "verbatim from `feedback_sent` in traces.json; the model's own "
          "intermediate replies are stored truncated (400 chars) in the "
          "traces and are not reproduced.", "",
          "`planner_pilot_v2_adapter11` sent no prompts — it replays "
          "saved v2 model outputs through adapter-1.1.", "",
          "**Caveats.** (1) Follow-up messages sent after `binding_reject` "
          "/ `adapter_reject` / malformed turns were generated by "
          "`planner_feedback()` but not stored in traces (`feedback_sent` "
          "is recorded only after gateway blocks), so they are absent "
          "here — this affects all multistep_pilot (v1) MS-ID1 / MS-LC* "
          "episodes. (2) multistep_pilot (v1) ran the pre-1.1 runner "
          "(sha256 `2cf636b2…`, no longer in the tree); the turn-0 "
          "template is taken from the fixture's `prompt_template` "
          "(hash-verified), and the v1.1 runner in the tree formats it "
          "identically, but the v1 runner itself cannot be re-hashed.", "",
          "| run | case | smoke | attack | files | prompt sha256[:16] |",
          "|---|---|---|---|---|---|"]
    for e in idx:
        md.append(f"| {e['run']} | {e['case_id']} | "
                  f"{'yes' if e['smoke'] else ''} | "
                  f"{'yes' if e['attack'] else ''} | "
                  f"{'<br>'.join(e['files'])} | `{e['prompt_sha256_16']}` |")
    md.append("")
    (out / "INDEX.md").write_text("\n".join(md))
    print(f"{len(idx)} case prompts -> {out}")


if __name__ == "__main__":
    main()
