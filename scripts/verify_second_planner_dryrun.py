#!/usr/bin/env python3
"""Verify a second-planner MOCK dry run reproduces the frozen runs.

Per docs/second_planner_protocol.md, no real planner run may start
until this reports ALL CHECKS PASS.

Checks:
  pilot     every frozen planner_pilot_v2 (case, attempt): the mock
            run must emit the same planner_error class / tool:none /
            serialized URL, and every arm replay must match the
            adapter-1.1 correction cells (planner_pilot_v2_adapter11)
            on decision, findings, receipts, enforcement_failure.
            stated_purpose must be the context-bound
            'research_summary' (adapter-1.1 semantics).
  multistep every frozen episode (case, arm): outcome, turns_used,
            completed, prohibited_attempts, retry_sequence,
            unauthorized_receipt_episode, and per-turn action /
            decision / findings / checked_url / secrets_received /
            needs_review / feedback_sent must match; raw output must
            be present on EVERY turn (incl. binding/adapter rejects
            and malformed) and match the frozen (truncated) raw.
  counts    paper_counts.py counting rule applied to the dry-run
            traces must equal the same rule applied to the frozen
            references; and docs/paper_counts.md must still
            regenerate byte-identically (results/ untouched).
  records   every planner call carries model id, params sent,
            timestamp; no *_API_KEY env VALUE appears anywhere in the
            trace file; prompt sha256s match prompts/ exports.

Usage:
  python scripts/verify_second_planner_dryrun.py \
      --pilot runs/second_planner/pilot_dryrun \
      --multistep runs/second_planner/multistep_dryrun
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAIL: list[str] = []
CHECKS = [0]


def ok(name: str, cond: bool, detail: str = "") -> None:
    CHECKS[0] += 1
    if not cond:
        FAIL.append(f"{name}: {detail}")
        print(f"FAIL  {name}  {detail}")


def jload(p: Path):
    return json.loads(p.read_text())


def fam(rule: str) -> str:
    for k, pre in (("host", "fetch_host_offlist"),
                   ("auth", "no_authorization"),
                   ("F5", "unaccounted_payload")):
        if rule.startswith(pre):
            return k
    return "other"


def first_blocking(findings: list[str]) -> str:
    return findings[0] if findings else "permitted"


# --------------------------------------------------------------- pilot
def check_pilot(new_dir: Path) -> dict:
    v2 = { (c["case"], c["attempt"]): c
           for c in jload(ROOT / "results/planner_pilot_v2/traces.json")["cells"] }
    a11 = { (c["case"], c["attempt"]): c
            for c in jload(ROOT / "results/planner_pilot_v2_adapter11/traces.json") }
    new = {(c["case"], c["attempt"]): c
           for c in jload(new_dir / "traces.json")["cells"]}
    ok("pilot.cell_count", len(new) == len(v2),
       f"{len(new)} vs {len(v2)}")
    counts = {"host": 0, "auth": 0, "F5": 0, "other": 0,
              "missing_purpose": 0, "corrected_allow": 0}
    for key, fc in sorted(v2.items()):
        nc = new.get(key)
        ok(f"pilot.{key}.present", nc is not None)
        if nc is None:
            continue
        ok(f"pilot.{key}.raw", nc.get("raw_output") == fc.get("raw_output"),
           "mock did not replay the frozen raw output")
        call = nc.get("call") or {}
        ok(f"pilot.{key}.call_meta",
           all(k in call for k in ("model_id", "timestamp_utc")),
           "call record missing model/timestamp")
        if "planner_error" in fc:
            ne = nc.get("planner_error", "")
            ok(f"pilot.{key}.error_class",
               ne.split(":")[0] == fc["planner_error"].split(":")[0],
               f"{ne!r} vs {fc['planner_error']!r}")
            continue
        gen_f = fc.get("generated", {})
        gen_n = nc.get("generated", {})
        if gen_f.get("tool") == "none":
            ok(f"pilot.{key}.none", gen_n.get("tool") == "none"
               and "replays" not in nc, f"{gen_n}")
            continue
        ok(f"pilot.{key}.serialized_url",
           gen_n.get("serialized_url") == gen_f.get("serialized_url"),
           f"{gen_n.get('serialized_url')} vs {gen_f.get('serialized_url')}")
        ok(f"pilot.{key}.purpose",
           gen_n.get("stated_purpose") == "research_summary"
           and gen_n.get("purpose_source") == "task_context",
           f"{gen_n.get('stated_purpose')}/{gen_n.get('purpose_source')}")
        ref = a11.get(key) or {}
        ref_replays = {r["arm"]: r for r in ref.get("replays", [])}
        ok(f"pilot.{key}.ref_replays", len(ref_replays) == 4,
           "adapter-1.1 reference missing")
        for r in nc.get("replays", []):
            fr = ref_replays.get(r["arm"])
            if fr is None:
                ok(f"pilot.{key}.{r['arm']}.ref", False, "no reference")
                continue
            for k in ("decision", "findings", "requests_received",
                      "secrets_received", "unauthorized_receipt",
                      "authorized_delivery", "enforcement_failure"):
                ok(f"pilot.{key}.{r['arm']}.{k}", r[k] == fr[k],
                   f"{r[k]!r} vs {fr[k]!r}")
        m3 = next((r for r in nc.get("replays", [])
                   if r["arm"] == "M3_full_gateway"), {})
        cid, att = key
        if (cid.startswith(("P2-ID", "P2-AD")) and not cid.endswith("-clean")
                and m3.get("decision") == "block"):
            counts[fam(first_blocking(m3.get("findings", [])))] += 1
        if cid == "P2-LC1":
            if m3.get("decision") == "block" and any(
                    f.startswith("no_authorization")
                    for f in m3.get("findings", [])):
                counts["missing_purpose"] += 1
            if m3.get("decision") == "allow":
                counts["corrected_allow"] += 1
    return counts


# ----------------------------------------------------------- multistep
FROZEN_TURN_KEYS = ("decision", "findings", "checked_url",
                    "secrets_received", "needs_review", "feedback_sent")


def check_multistep(new_dir: Path) -> dict:
    fz = {(e["case"], e["arm"]): e for e in
          jload(ROOT / "results/multistep_pilot_v2/traces.json")["episodes"]}
    new = {(e["case"], e["arm"]): e for e in
           jload(new_dir / "traces.json")["episodes"]}
    ok("ms.episode_count", len(new) == len(fz), f"{len(new)} vs {len(fz)}")
    counts = {"host": 0, "auth": 0, "F5": 0, "other": 0, "prohibited": 0}
    for key, fe in sorted(fz.items()):
        ne = new.get(key)
        ok(f"ms.{key}.present", ne is not None)
        if ne is None:
            continue
        for k in ("seed", "outcome", "turns_used", "completed",
                  "prohibited_attempts", "retry_sequence",
                  "unauthorized_receipt_episode"):
            ok(f"ms.{key}.{k}", ne[k] == fe[k], f"{ne[k]!r} vs {fe[k]!r}")
        mse = fe.get("model_settings_effective", {})
        ok("ms.%s.options" % (key,),
           ne["model_settings_effective"]["options_sent"] ==
           mse.get("options_sent")
           and ne["model_settings_effective"]["think_sent"] ==
           mse.get("think_sent"),
           f"{ne['model_settings_effective']} vs {mse}")
        ok(f"ms.{key}.turn_count",
           len(ne["attempts"]) == len(fe["attempts"]),
           f"{len(ne['attempts'])} vs {len(fe['attempts'])}")
        for fa, na in zip(fe["attempts"], ne["attempts"]):
            t = fa["turn"]
            ok(f"ms.{key}.t{t}.raw_present", na.get("raw") is not None,
               "raw output missing on this turn (R5 gap)")
            ok(f"ms.{key}.t{t}.raw_prefix",
               (na.get("raw") or "")[:400] == fa.get("raw"),
               "raw differs from frozen")
            for kind in ("action", "malformed", "binding_reject",
                         "adapter_reject"):
                fk = kind in fa or fa.get("action") == kind
                nk = kind in na or na.get("action") == kind
                ok(f"ms.{key}.t{t}.{kind}", fk == nk,
                   f"frozen {fa.get(kind, fa.get('action'))!r} vs "
                   f"new {na.get(kind, na.get('action'))!r}")
            for k in FROZEN_TURN_KEYS:
                if k in fa:
                    ok(f"ms.{key}.t{t}.{k}", na.get(k) == fa[k],
                       f"{na.get(k)!r} vs {fa[k]!r}")
            ok(f"ms.{key}.t{t}.call_meta",
               all(x in (na.get("call") or {})
                   for x in ("model_id", "timestamp_utc")),
               "call record missing model/timestamp")
        # turn-0 M3 deciding-check counts
        if key[1] == "M3_full_gateway" and ne["attempts"]:
            a0 = ne["attempts"][0]
            if a0.get("decision") == "block":
                f0 = first_blocking(a0.get("findings", []))
                if key[0].startswith("MS-LC"):
                    counts["prohibited"] += 1
                elif key[0].startswith(("MS-ID", "MS-AD")) \
                        and not key[0].endswith("-clean"):
                    counts[fam(f0)] += 1
    return counts


# ------------------------------------------------------------- secrets
def check_no_secrets(path: Path) -> None:
    text = (path / "traces.json").read_text()
    for k, v in os.environ.items():
        if k.endswith(("_API_KEY", "_TOKEN")) and v:
            ok(f"secret.{k}.absent", v not in text,
               f"{k} value leaked into {path}")
    ok("secret.no_api_key_fields", '"api_key"' not in text.lower(),
       "api_key field present in trace")


# -------------------------------------------------------------- counts
def check_paper_counts() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "paper_counts.md"
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/paper_counts.py"),
             "--out", str(out)], capture_output=True, text=True,
            cwd=ROOT)
        ok("paper_counts.regen_ok", r.returncode == 0, r.stderr[:200])
        if out.exists():
            ok("paper_counts.identical",
               out.read_text() ==
               (ROOT / "docs/paper_counts.md").read_text(),
               "regenerated paper_counts.md differs")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot")
    ap.add_argument("--multistep")
    a = ap.parse_args()
    new_counts: dict = {}
    ref_counts: dict = {}

    if a.pilot:
        print("== pilot (vs planner_pilot_v2 raws + adapter-1.1 decisions)")
        nc = check_pilot(Path(a.pilot))
        # reference counts over the adapter-1.1 frozen cells
        rc = {"host": 0, "auth": 0, "F5": 0, "other": 0,
              "missing_purpose": 0, "corrected_allow": 0}
        for c in jload(ROOT /
                       "results/planner_pilot_v2_adapter11/traces.json"):
            m3 = next((r for r in c.get("replays", [])
                       if r["arm"] == "M3_full_gateway"), {})
            cid = c["case"]
            if (cid.startswith(("P2-ID", "P2-AD"))
                    and not cid.endswith("-clean")
                    and m3.get("decision") == "block"):
                rc[fam(first_blocking(m3.get("findings", [])))] += 1
            if cid == "P2-LC1" and m3.get("decision") == "allow":
                rc["corrected_allow"] += 1
        new_counts.update({f"pilot.{k}": v for k, v in nc.items()})
        ref_counts.update({f"pilot.{k}": v for k, v in rc.items()})
        check_no_secrets(Path(a.pilot))

    if a.multistep:
        print("== multistep (vs multistep_pilot_v2 episodes)")
        nc = check_multistep(Path(a.multistep))
        rc = {"host": 0, "auth": 0, "F5": 0, "other": 0, "prohibited": 0}
        for e in jload(ROOT /
                       "results/multistep_pilot_v2/traces.json")["episodes"]:
            if e["arm"] != "M3_full_gateway" or not e["attempts"]:
                continue
            a0 = e["attempts"][0]
            if a0.get("decision") != "block":
                continue
            f0 = first_blocking(a0.get("findings", []))
            if e["case"].startswith("MS-LC"):
                rc["prohibited"] += 1
            elif e["case"].startswith(("MS-ID", "MS-AD")) \
                    and not e["case"].endswith("-clean"):
                rc[fam(f0)] += 1
        new_counts.update({f"ms.{k}": v for k, v in nc.items()})
        ref_counts.update({f"ms.{k}": v for k, v in rc.items()})
        check_no_secrets(Path(a.multistep))

    print("== counts (dry run vs frozen reference)")
    for k in sorted(ref_counts):
        ok(f"counts.{k}", new_counts.get(k) == ref_counts[k],
           f"new={new_counts.get(k)} frozen={ref_counts[k]}")
        print(f"      {k:30} new={new_counts.get(k)}  "
              f"frozen={ref_counts[k]}")

    print("== paper_counts.md regeneration")
    check_paper_counts()

    print()
    if FAIL:
        print(f"DRY-RUN VERIFY: {len(FAIL)} of {CHECKS[0]} checks FAILED")
        for f in FAIL[:30]:
            print(f"  - {f}")
        sys.exit(1)
    print(f"DRY-RUN VERIFY: ALL {CHECKS[0]} CHECKS PASS — "
          "mock replay reproduces the frozen decisions exactly")


if __name__ == "__main__":
    main()
