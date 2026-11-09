# mnd-pol-1.1 freeze (methods + eval protocol, pre-evaluation)

Frozen before any mnd-eval case generation or run. Prior freezes stand:
`results/disclosure_mnd_dev/FREEZE.md`, `results/disclosure_cmp_FREEZE.md`.

## Frozen artifacts (sha256)

- `src/tool_routing/argverify/min_disclosure.py` — `96881599ec2ff655f21c603041f36b63b012372b427aaf0282bd6aee45aefae0` (mnd-pol-1.1)
- `src/tool_routing/argverify/disclosure.py` — `3009615105e92d4878cd45c3c14c1333475fbdd48c12a69a9387f4bf52e0cf17` (unchanged)
- `scripts/run_disclosure_mnd.py` — `6d1f20821953843482a2e0d0337493bb816bba7026fe3264bf61a3179b7e8aa4`
- `scripts/build_disclosure_mnd_v1_1.py` — `7bf3365fb84422969f4db06e440732084ec42320e2d1c58d564fccf49f423bcb`
- `src/tool_routing/argverify/fixtures/disclosure_cases_mnd_v1_1.json` — `c8ba144639e7b4c2ed067e87343e67f34770da837d67c9a25dafedd0acaf5845`
- `docs/security_mnd_eval_spec.md` — `c940feb065146685497aacf3a1b3186a2461323cfa881fdcfbe14236de6bea79`
- `tests/test_min_disclosure.py` — `ca49bac3116ad08a5d6cce00f46b34d0e1168383fd9a54013e362bed74db92e1`

## Method versions frozen

- `mnd` = mnd-pol-1.1 (records + expiry on ref fields)
- `ref_conservative` = same checks, verified-acceptance only, no
  destination clarification
- `ref_optimistic` = acceptance-check ablation (assumes unknown
  acceptance; intentionally weaker, not a proposed method)
- `recovery`/`block_only` = frozen as before

## Protocol frozen

- Predictions-hidden review; prior exposure + AI assistance recorded;
  reviewer answers verbatim before comparison; expected answers kept
  out of the review packet.
- Eval spec `mnd-eval-1.0` decisions fixed: new identities + records,
  verified-constraint selection only, "reference only" = disclosure
  restriction (no unauthorized fallback — stop is a valid outcome),
  valid counterparts + stop cases included.
- No eval run until expected-behavior review approves the spec.
