# mnd-eval-1.0 evaluation manifest (frozen BEFORE the run)

Frozen inputs — any change requires new fixture/label version + new run ID.

- fixture disclosure_cases_mnd_eval_v1.json: eb0da0d5317f6085fad355d5bf8aa43fd798f06a78b454781b5d83cc5dd364be
- labels disclosure_mnd_eval_labels_v1.json: d334f1313207c19a8bf7850672a6d8ff7d168959de03302c7262ff9acd32859a (agent-generated from adjudicated spec + truth; evaluator-side only)
- builder: df5bcf3757e05d4caa357c746f0e2de971211da69d6ac2dd081d64fb8b006ddb
- runner: 0bb66b39219d69d5b4292ed9b5c6a8cbaf1c614b4cf202214d42801be608ac86
- methods frozen per results/disclosure_mnd_dev3/FREEZE.md (disclosure.py 30096151…, min_disclosure.py mnd-pol-1.1)
- leakage validated: no evaluator-only keys or environment replies in any gateway_view (application_records are gateway-visible by design)

Methods: block_only, recovery, ref_conservative, ref_optimistic (ablation), mnd — identical available information.

## Amendment — mnd-pol-1.1p patch (post-run-1, disclosed)

Run 1 (`results/disclosure_mnd_eval_v1`, preserved) surfaced an
implementation bug: acceptance confirmed by a destination reply was
not persisted into the re-verified view, so clarified substitution
always fell back (ME-06). Patched code is `mnd-pol-1.1p` — a bugfix,
not a method/policy change; regression test added. Patched run:
`results/disclosure_mnd_eval_v1_r2`. Fixture/label hashes unchanged.

## Amendment — corrected metrics + mnd-pol-1.2 dev version

- Runner rescored (run_disclosure_mnd_eval.py, hash below in v12
  MANIFEST): blocked vs correct-stop separated via labels; three-way
  delivery classification (unauthorized / restriction / wrong-app);
  combined policy_violations metric.
- mnd-pol-1.2 added post-eval: restriction enforcement, verified
  status/constraint selection, record-selection clarification. Run:
  results/disclosure_mnd_eval_v12. Prior runs (v1, _r2) preserved.
