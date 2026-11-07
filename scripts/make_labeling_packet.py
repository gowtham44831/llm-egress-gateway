"""Build blinded labeling packets from frozen trace artifacts.

Outputs (deterministic, no model calls):

- labels/packet.csv — blinded items for labeling.
    * question=A_planner_output: one row per distinct turn-0 model
      output (planner_pilot_v1/v2/adapter11 cells and multistep_pilot
      v1/v2 turn-0 attempts; arm replays deduplicated).
    * question=B_receipt: one row per distinct receiver receipt
      (delivered content) across non-diagnostic in-scope runs.
    Columns: item_id, question, task_prompt, permission_context,
    retrieved_summary, model_output, receiver_observed. No arm, gateway
    decision, deciding rule, case_id, or expected outcome.
- labels/recovery_packet.csv — turn>=1 model outputs (post-feedback
  turns). Unblinded: carries run/case/arm/outcome columns.
- labels/diagnostic_packet.csv — receiver receipts from the
  f5_coverage_repro and demo_showcase diagnostic runs (blinded format).
- labels/key.csv — unblinded mapping item_id -> all source rows.
- labels/excluded.md — items dropped from the packets and why
  (e.g., binding_reject rows whose raw model output was not stored).

Development items (traces_smoke runs, DEV-* cases) are removed from
all packets. Loopback receiver hosts (127.0.0.1:port, localhost:port)
are rewritten to the case's logical destination host. A blinding scan
for gateway-reason phrasing is run on every emitted output.

Read-only on inputs. Reuses scripts/attribution_table.py parsing and
its deterministic replay helpers so deciding_rule / receiver_receipt
match the generated attribution table.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIXTURES = ROOT / "src/tool_routing/argverify/fixtures"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

import attribution_table as AT  # noqa: E402
from tool_routing.argverify.url_fetch_gateway import (  # noqa: E402
    decode_url_payload)

MODEL_RUNS = ("planner_pilot_v1", "planner_pilot_v2",
              "planner_pilot_v2_adapter11",
              "multistep_pilot", "multistep_pilot_v2")

REASON_PHRASES = re.compile(
    r"not accounted for|not allowlisted|blocked|not valid", re.I)


# ---------------------------------------------------------------------
# case context: task + retrieved summary + permission inputs (defs)
# ---------------------------------------------------------------------

def _summary(retrieved) -> str:
    return "; ".join(
        f"{t.get('tool', '?')}: {json.dumps(t.get('output'), sort_keys=True)}"
        for t in retrieved or [])


def _permctx(records, allowlist) -> str:
    parts = []
    for r in records or []:
        fields = (r.get("permitted_fields")
                  or r.get("prohibited_fields") or [])
        parts.append(
            f"{r.get('effect', '?')} {r.get('auth_id', '?')}: "
            f"{', '.join(fields) or 'all'} "
            f"-> {r.get('destination_principal', '?')} "
            f"for {r.get('purpose', '?')}")
    if not parts:
        parts.append("permission records: none")
    return f"fetch allowlist: {sorted(allowlist or [])} | " + \
        "; ".join(parts)


def _dirs(directory, cid) -> dict:
    """display_host -> service principal. Loopback directory keys are
    presented under the case's logical destination name."""
    out = {}
    for h, v in (directory or {}).items():
        dh = (_LOGICAL.get(cid, "receiver.internal")
              if h in ("127.0.0.1", "localhost") else h)
        out[dh] = (v or {}).get("principal", "?")
    return out


def _load_context() -> dict:
    """case_id -> {'task','retr','perm','dirs','purpose'} from def files."""
    ctx: dict[str, dict] = {}

    def put(cid, task, retr, records, allowlist, directory, purpose):
        if cid and cid not in ctx:
            ctx[cid] = {"task": task or "", "retr": _summary(retr),
                        "perm": _permctx(records, allowlist),
                        "dirs": _dirs(directory, cid),
                        "purpose": purpose or "(none bound)"}

    for name in ("planner_pilot_cases_v1.json",
                 "planner_pilot_cases_v2.json",
                 "multistep_cases_v1.json", "multistep_cases_v2.json"):
        d = json.loads((FIXTURES / name).read_text())
        pool = [c for grp in ("attack_cases", "clean_counterparts",
                              "legitimate_cases", "episodes")
                for c in (d.get(grp) or [])]
        for k in ("dev_case", "dev_episode"):
            if isinstance(d.get(k), dict):
                pool.append(d[k])
        for c in pool:
            pv = c.get("policy_view") or c.get("policy") or {}
            # pilots' serializer binds stated_purpose=research_summary
            # (runner hardcodes it); multistep binds context_purpose.
            purpose = (c.get("context_purpose")
                       or "research_summary")
            put(c.get("case_id"), c.get("task"),
                c.get("retrieved_content"), pv.get("records"),
                pv.get("allowlist"), pv.get("directory"), purpose)

    rev2 = AT._mod("run_url_eval_v2")
    for cid in ("ID-1", "AD-1", "SY-1", "LC-1", "LC-2"):
        v = rev2.build_concrete(cid, 0)
        # loopback allowlist entry -> the logical destination host,
        # consistent with the deloop'd URLs
        al = [_LOGICAL.get(cid, h) if h in ("127.0.0.1", "localhost")
              else h for h in v["policy"]["fetch_allowlist"]]
        put(cid, "", v["retrieved_content"], v["permission_records"],
            al, v["directory"],
            v["planner_call"].get("stated_purpose"))
    rv4 = AT._mod("run_eval_v4")
    for cid, cfg in rv4.CASES.items():
        put(cid, "", rv4.RETRIEVED, cfg.get("records"),
            cfg.get("allowlist"), cfg.get("directory"),
            cfg.get("purpose"))
    iso = AT._mod("run_url_fetch_isolation")
    for cid, cd in iso.controls().items():
        v = cd["make_view"](80)
        al = [v["directory"].get(h, {}).get("principal", h)
              for h in v["policy"]["fetch_allowlist"]]
        put(cid, "", v["retrieved_content"],
            v["permission_records"], al, v["directory"],
            v["planner_call"].get("stated_purpose"))
        _EXP[cid] = cd.get("expected_full", "")
    f5 = AT._mod("repro_f5_coverage")
    for name, _url in f5.TRACES:
        put(name, "", f5.RETRIEVED, [f5.REC_A2],
            ["billing.example"],
            {"billing.example": {"principal": "billing.svc"}},
            "invoice_lookup")
    dm = AT._mod("demo_showcase")
    for s, cfg in (
            ("S1_shadowleak_shape",
             {"records": [], "allowlist": ["platform.example"],
              "directory": dm.ATTACK_DIR}),
            ("S2_authorized_delivery",
             {"records": [dm.ALLOW_ALL],
              "allowlist": ["docs.example"],
              "directory": dm.DOCS_DIR}),
            ("S3_sibling_carrier_legacy",
             {"records": [dm.ALLOW_ALL],
              "allowlist": ["docs.example"],
              "directory": dm.DOCS_DIR}),
            ("S3_sibling_carrier_strict",
             {"records": [dm.ALLOW_ALL],
              "allowlist": ["docs.example"],
              "directory": dm.DOCS_DIR})):
        put(s, "", dm.RETRIEVED, cfg["records"], cfg["allowlist"],
            cfg["directory"], "research_summary")
    return ctx


_EXP: dict[str, str] = {}


# ---------------------------------------------------------------------
# field extraction
# ---------------------------------------------------------------------

_LOOPBACK = re.compile(r"https?://(127\.0\.0\.1|localhost)(:\d+)?")

# logical destination host per case when the recorded URL used a
# loopback receiver (isolation harness maps localhost -> docs.svc;
# url_eval_v2 dispatches the loopback but the case's intended host is
# the eval_v4 naming: attacker.example / trusted-upload.example /
# docs.example).
_LOGICAL = {"U1": "docs.svc", "U2": "docs.svc", "U3": "docs.svc",
            "preserved_benign": "docs.svc",
            "preserved_offlist": "unknown-host.example",
            "ID-1": "attacker.example", "SY-1": "attacker.example",
            "AD-1": "trusted-upload.example",
            "LC-1": "docs.example", "LC-2": "docs.example"}


def _deloop(text: str, case_id: str) -> str:
    host = _LOGICAL.get(case_id, "receiver.internal")
    return _LOOPBACK.sub(f"http://{host}", text)


def _observed_from_url(url: str) -> str:
    """Decoded candidate values a receiver would observe — same bounded
    decode as the gateway."""
    if not url:
        return ""
    dec = decode_url_payload(url)
    return "; ".join(str(c.get("decoded") or c.get("raw"))
                     for c in dec.get("candidates", []))


def _observed_from_path(path: str) -> str:
    return _observed_from_url("http://x" + path)


_V2URL: dict | None = None


def _v2_url(case_id: str, attempt) -> str:
    global _V2URL
    if _V2URL is None:
        d = json.loads(
            (RESULTS / "planner_pilot_v2/traces.json").read_text())
        _V2URL = {}
        for c in d["cells"]:
            for r in c.get("replays", []):
                _V2URL[(c["case"], str(c["attempt"]))] = \
                    r.get("checked_url", "")
    return _V2URL.get((case_id, str(attempt)), "")


def _model_output(rec: dict, run: str) -> str:
    """The model's emitted content for this row's source cell/attempt.
    "" when the trace did not store it."""
    base = run.split("/")[0]
    if base == "planner_pilot_v2_adapter11":
        u = _v2_url(rec.get("case"), rec.get("attempt"))
        return u or "(no tool call)"
    if base.startswith("planner_pilot"):
        gen = rec.get("generated")
        if isinstance(gen, dict):
            if gen.get("tool") == "none":
                return "(no tool call)"
            return (gen.get("serialized_url") or gen.get("url")
                    or json.dumps(gen, sort_keys=True))
        return str(rec.get("raw_output") or "")
    # multistep attempt
    if rec.get("checked_url"):
        return rec["checked_url"]
    if rec.get("action") in ("respond", "request_permission"):
        return f"{rec['action']}: {rec.get('detail', '')}"
    if rec.get("binding_reject") or rec.get("adapter_reject"):
        raw = rec.get("raw") or rec.get("structured")
        if not raw:
            return ""  # trace gap: raw output not stored
        return json.dumps(raw, sort_keys=True) \
            if isinstance(raw, dict) else str(raw)
    return str(rec.get("raw") or rec.get("planner_error") or "")


def _receipt_content(run: str, rec: dict) -> str:
    base = run.split("/")[0]
    if base == "url_gw_isolation":
        vals = [str(v) for r in rec.get("receiver_decoded_values") or []
                for v in r.get("values", [])]
        return "; ".join(vals)
    if base == "f5_coverage_repro":
        return "; ".join(_observed_from_path(p)
                         for p in rec.get("receiver_got") or [])
    if base == "demo_showcase":
        return "; ".join(_observed_from_path(p)
                         for p in rec.get("receiver_receipt") or [])
    if rec.get("arm") == "M3_full_gateway_rerun":
        return ""  # check-only rerun — no receiver
    url = rec.get("checked_url")
    if not url and base == "camel_component_eval":
        v = AT._view_for(run, rec.get("_case") or rec.get("case"), rec)
        url = (v or {}).get("planner_call", {}).get(
            "arguments", {}).get("url", "")
    if (rec.get("decision") == "allow"
            or rec.get("dispatched_url")
            or rec.get("requests_received")):
        if rec.get("requests_received", 1):
            return _observed_from_url(url)
    return ""


def _proposed_url(run: str, rec: dict) -> str:
    return (rec.get("checked_url") or rec.get("proposed_call")
            or rec.get("url") or "")


def _expected(rec: dict, arm: str) -> str:
    exp = rec.get("expected")
    if isinstance(exp, dict):
        short = {"M1_allowlist": "M1", "M2_content_inspect": "M2",
                 "M3_full_gateway": "M3"}.get(arm, arm)
        return str(exp.get(short, exp.get(arm, "")))
    if arm == "full_gateway":
        return str(_EXP.get(rec.get("_case") or rec.get("case"), ""))
    return ""


_URLHOST = re.compile(r"https?://([^/?\s'\"]+)")


def _ctx_line(c: dict, output: str, observed: str) -> str:
    """permission_context column: def inputs (records + allowlist),
    directory host->principal for each URL host present, and the bound
    task purpose."""
    hosts: list[str] = []
    for m in _URLHOST.findall(f"{output} {observed}"):
        h = m.split(":")[0]
        if h not in hosts:
            hosts.append(h)
    ds = ("; ".join(
        f"{h} -> {c['dirs'].get(h, '(no directory entry)')}"
        for h in hosts) if hosts else "(no url hosts)")
    return (f"{c['perm']} | directory: {ds} "
            f"| task purpose: {c['purpose']}")


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main() -> None:
    ctx = _load_context()
    items: dict[str, dict] = {}      # packet items (blinded)
    diag_items: dict[str, dict] = {}
    recovery: list[dict] = []        # unblinded turn>=1 rows
    excluded: list[dict] = []

    def add(store, kind, cid, c, output, observed, source):
        # Dedupe key includes the full permission context (records,
        # directory, task purpose), retrieved summary, and case_id —
        # items with different authorization ground truth never merge.
        sig = hashlib.sha256(
            f"{kind}|{cid}|{c['task']}|{c['perm']}|"
            f"{sorted(c['dirs'].items())}|{c['purpose']}|{c['retr']}|"
            f"{output}|{observed}".encode()).hexdigest()
        it = store.setdefault(sig, {"kind": kind, **c,
                                    "output": output,
                                    "observed": observed, "srcs": []})
        if isinstance(source, list):
            it["srcs"].extend(source)
        else:
            it["srcs"].append(source)

    for path in sorted(RESULTS.rglob("*.json")):
        run = AT._run_id(path)
        if "manifest" in path.stem or path.suffix == ".jsonl":
            continue
        if run.endswith("traces_smoke"):
            continue  # development items removed
        base = run.split("/")[0]
        if not base.startswith(("planner_pilot", "multistep_pilot",
                                "url_eval", "eval_v4",
                                "url_gw_isolation", "f5_coverage",
                                "demo_showcase")):
            continue
        if base == "camel_component_eval":
            continue  # policy-component re-evaluation; no new deliveries
        try:
            rows = AT.parse_file(path)
        except Exception:
            continue

        cells: dict[tuple, list] = {}
        for r in rows:
            rec = r["_rec"]
            if str(r["case_id"]).startswith("DEV-"):
                continue
            r["run_tag"] = AT._run_tag(run)
            r["receiver_receipt"] = AT._receipt(run, rec)
            r["attempt_id"] = str(rec.get("attempt") or 1)
            r["turn"] = int(rec.get("turn", 0))
            r["deciding_rule"] = AT._resolve_rule(run, rec, r["outcome"],
                                                r["arm"])
            if base.startswith("planner_pilot"):
                key = (r["case_id"], r["attempt_id"], r["turn"])
            else:
                key = (r["case_id"], r["attempt_id"], r["turn"],
                       r["arm"])
            cells.setdefault(key, []).append(r)

        for key, grp in cells.items():
            rec0 = grp[0]["_rec"]
            cid = grp[0]["case_id"]
            c = ctx.get(cid, {"task": "", "retr": "", "perm": "",
                              "dirs": {}, "purpose": ""})
            srcs = [{"run": run, "case_id": cid,
                     "attempt_id": g["attempt_id"], "turn": g["turn"],
                     "arm": g["arm"], "outcome": g["outcome"],
                     "deciding_rule": g["deciding_rule"],
                     "call_origin": g["call_origin"],
                     "receiver_receipt": g["receiver_receipt"],
                     "expected": _expected(g["_rec"], g["arm"])}
                    for g in grp]

            # ---- model outputs ----
            if run in MODEL_RUNS:
                output = _model_output(rec0, run)
                turn = grp[0]["turn"]
                if not output:
                    for s in srcs:
                        excluded.append(
                            dict(s, reason="raw model output not "
                                 "stored in trace (binding_reject "
                                 "trace gap)"))
                elif turn >= 1:
                    url = (rec0.get("checked_url") or ""
                           if base.startswith("multistep")
                           else output)
                    observed = (_deloop(_observed_from_url(url), cid)
                                if str(url).startswith("http") else "")
                    for s in srcs:
                        recovery.append(
                            dict(s, task=c["task"],
                                 perm=_ctx_line(c, output, observed),
                                 retr=c["retr"],
                                 output=_deloop(output, cid),
                                 observed=observed))
                else:
                    url = (output if output.startswith("http")
                           else rec0.get("checked_url"))
                    observed = (_deloop(_observed_from_url(url), cid)
                                if url else "")
                    add(items, "A_planner_output", cid, c,
                        _deloop(output, cid), observed, srcs)

            # ---- receiver receipts ----
            for g in grp:
                rec = g["_rec"]
                obs = _receipt_content(run, rec)
                if not obs:
                    continue
                store = (diag_items if base in
                         ("f5_coverage_repro", "demo_showcase")
                         else items)
                add(store, "B_receipt", cid, c,
                    _deloop(_proposed_url(run, rec), cid),
                    _deloop(obs, cid),
                    [{"run": run, "case_id": cid,
                      "attempt_id": g["attempt_id"], "turn": g["turn"],
                      "arm": g["arm"], "outcome": g["outcome"],
                      "deciding_rule": g["deciding_rule"],
                      "call_origin": g["call_origin"],
                      "receiver_receipt": g["receiver_receipt"],
                      "expected": _expected(rec, g["arm"])}])

    # ---- blinding scan: gateway-reason phrasing in outputs ----
    leaked = []
    for store, fname in ((items, "packet"), (diag_items, "diagnostic")):
        for sig, it in list(store.items()):
            m = REASON_PHRASES.search(it["output"])
            if m and it["kind"] == "A_planner_output":
                del store[sig]
                for s in it["srcs"]:
                    leaked.append(dict(s, reason="model output contains"
                                       f" gateway-reason phrasing: "
                                       f"'{m.group(0)}'"))
    for e in leaked:
        excluded.append(e)
    for r in recovery:
        m = REASON_PHRASES.search(r["output"])
        if m:
            r["phrase_note"] = m.group(0)  # unblinded file — keep+note

    # LABELS_OUT: optional output dir override (scripts/reproduce_tables.sh)
    labels = Path(os.environ.get("LABELS_OUT") or ROOT / "labels")
    labels.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20260215)

    def write_packet(store, fname, prefix):
        sigs = list(store)
        rng.shuffle(sigs)  # fresh seeded shuffle; no prior ids kept
        keyrows = []
        with (labels / fname).open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["item_id", "question", "task_prompt",
                        "permission_context", "retrieved_summary",
                        "model_output", "receiver_observed"])
            for i, sig in enumerate(sigs, 1):
                it = store[sig]
                iid = prefix.format(i)
                w.writerow([iid, it["kind"], it["task"],
                            _ctx_line(it, it["output"],
                                      it["observed"]),
                            it["retr"], it["output"], it["observed"]])
                for s in it["srcs"]:
                    keyrows.append((iid, it["kind"], s))
        return keyrows

    keyrows = write_packet(items, "packet.csv", "LBL-{:04d}")
    keyrows += write_packet(diag_items, "diagnostic_packet.csv",
                            "LBL-D{:02d}")

    with (labels / "key.csv").open("w", newline="") as f:
        kw = csv.writer(f)
        kw.writerow(["item_id", "item_kind", "run", "case_id",
                     "attempt_id", "turn", "arm", "outcome",
                     "deciding_rule", "call_origin", "receiver_receipt",
                     "expected"])
        for iid, kind, s in keyrows:
            kw.writerow([iid, kind, s["run"], s["case_id"],
                         s["attempt_id"], s["turn"], s["arm"],
                         s["outcome"], s["deciding_rule"],
                         s["call_origin"], s["receiver_receipt"],
                         s["expected"]])

    with (labels / "recovery_packet.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "case_id", "attempt_id", "turn", "arm",
                    "task_prompt", "permission_context",
                    "retrieved_summary", "model_output",
                    "receiver_observed", "outcome", "deciding_rule",
                    "call_origin", "receiver_receipt", "expected",
                    "phrase_note"])
        for r in recovery:
            w.writerow([r["run"], r["case_id"], r["attempt_id"],
                        r["turn"], r["arm"], r["task"], r["perm"],
                        r["retr"], r["output"], r["observed"],
                        r["outcome"], r["deciding_rule"],
                        r["call_origin"], r["receiver_receipt"],
                        r["expected"], r.get("phrase_note", "")])

    md = ["# Excluded items", "",
          "| run | case | attempt | turn | arm | reason |",
          "|---|---|---|---|---|---|"]
    for e in sorted(excluded, key=lambda x: (x["run"], x["case_id"],
                                             x["arm"], x["turn"])):
        md.append(f"| {e['run']} | {e['case_id']} | {e['attempt_id']} "
                  f"| {e['turn']} | {e['arm']} | {e['reason']} |")
    md.append("")
    md.append("camel_component_eval runs are dropped entirely "
              "(policy-component re-evaluation; no new deliveries).")
    md.append("")
    (labels / "excluded.md").write_text("\n".join(md))

    # integrity check: one item_id must not span different cases or
    # conflicting receiver_receipt values
    by_id: dict[str, list] = {}
    for iid, kind, s in keyrows:
        by_id.setdefault(iid, []).append(s)
    issues = []
    for iid, ss in sorted(by_id.items()):
        cases = {x["case_id"] for x in ss}
        receipts = {x["receiver_receipt"] for x in ss} - {"none"}
        if len(cases) > 1 or len(receipts) > 1:
            issues.append((iid, sorted(cases), sorted(receipts)))

    print(f"packet.csv: {sum(1 for i in items.values() if i['kind']=='A_planner_output')} A + "
          f"{sum(1 for i in items.values() if i['kind']=='B_receipt')} B items")
    print(f"diagnostic_packet.csv: {len(diag_items)} items; "
          f"recovery_packet.csv: {len(recovery)} rows; "
          f"excluded: {len(excluded)}")
    phrase_hits = sum(1 for r in recovery if r.get("phrase_note"))
    print(f"blinding scan: {len(leaked)} packet items removed for "
          f"gateway phrasing; {phrase_hits} recovery rows flagged")
    print(f"key check: {len(issues)} item_ids span multiple cases "
          f"or receiver_receipt values")
    for iid, cases, receipts in issues:
        print(f"  {iid}: cases={cases} receipts={receipts}")
    print("context check (perm | dirs | task purpose):")
    for cid in ("V4-LC1", "V4-LC3", "V4-SY3", "MS-LC1", "MS-LC3"):
        c = ctx.get(cid)
        if c:
            print(f"  {cid}: {c['perm']} | dirs={c['dirs']} "
                  f"| task purpose: {c['purpose']}")


if __name__ == "__main__":
    main()
