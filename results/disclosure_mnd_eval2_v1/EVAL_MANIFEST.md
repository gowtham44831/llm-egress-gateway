# EVAL MANIFEST — mnd-eval-2.0 (frozen before execution)

Author-designed evaluation set (second, separately authored world:
tomas.wei / lena.farouk / omar.haddad; combined factors; varied record
order). NOT an independent benchmark — designed with knowledge of
eval-v1 failures; reviewed before execution.

Hashes at freeze (sha256):
- fixture  disclosure_cases_mnd_eval2_v1.json:
  af70ce2570dbab6c5c2745dad4cde8c4ad8e01b34e85af85bc1a309dc900fef9
- labels   disclosure_mnd_eval2_labels_v1.json:
  033e9c3ab6dee7a2ebd7adf5912349833a6cf281b70487af7aae04fcb85abec3
- builder  build_disclosure_mnd_eval2_v1.py:
  233172e493ce5d0dea0935c0bcffc3a803f579cd43cdcc7daebc3929423ce18b
- runner   run_disclosure_mnd_eval.py:
  9b921f2caadcd5edc4ef530f8f87579e43908f39379272cdaf15c8157ae56d19
- methods  min_disclosure.py (mnd-pol-1.2, frozen):
  505a0e11114e958ac2a62f0cd7a204b1bfa65df0ca6a5fc0a7f6d0aca861cbb7
- methods  disclosure.py (frozen):
  3009615105e92d4878cd45c3c14c1333475fbdd48c12a69a9387f4bf52e0cf17

Leakage validation: no evaluator-only keys, reply text, or reply
structure keys in any gateway_view (checked post-build).

Arms: PRIMARY = {mnd_v1_2, ref_conservative, recovery};
HISTORICAL = {block_only, ref_optimistic(ablation), mnd(1.1p)}.
Single run; failures preserved; no within-run method fixes.
