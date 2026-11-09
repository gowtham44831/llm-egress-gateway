# disclosure_mnd_eval_v12 — mnd-pol-1.2 dev run manifest

Same frozen fixture + labels as eval-v1 (see
`results/disclosure_mnd_eval_v1/EVAL_MANIFEST.md`). This run adds the
post-eval development arm `mnd_v1_2` and uses the corrected scoring.

Code at run time (sha256):
- src/tool_routing/argverify/min_disclosure.py (mnd-pol-1.2):
  `505a0e11114e958ac2a62f0cd7a204b1bfa65df0ca6a5fc0a7f6d0aca861cbb7`
- scripts/run_disclosure_mnd_eval.py (corrected metrics):
  `e38446ecb70b2f609a4c5f857b01c06be7c344e3ce530af4f6d4ea250e527398`
- src/tool_routing/argverify/disclosure.py (frozen):
  `3009615105e92d4878cd45c3c14c1333475fbdd48c12a69a9387f4bf52e0cf17`

Disclosures: post-evaluation development version — v1_2 was designed
AFTER seeing eval-v1 results and targets measured gaps (restriction
enforcement, record selection). Eval fixture unchanged; results here
are development feedback, not a re-evaluation under a frozen protocol.
