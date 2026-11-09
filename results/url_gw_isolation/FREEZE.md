# FREEZE — milestone tag `url-gw-1.0-isolation`

Frozen at close of the url-fetch interception milestone. Git has no
commit containing this work (repo convention: hash-manifest freezes,
results/ git-ignored); the tag is a version label, not a git tag.

## Hashes (sha256)

### New this milestone
| file | sha256 |
|---|---|
| src/tool_routing/argverify/url_fetch_gateway.py | 87598dfb53222f9dedef7be375c92ee6c622128c1a8e60e1ab19150ca94dfbb6 |
| tests/test_url_fetch_gateway.py | 8af94e815d88ee21e42b67f2d092f4dee1a7dab4f1b347aeb90b21c34a0925a6 |
| scripts/run_shadowleak_mechanism_demo.py | a32f304e260f02ceeed873075a6a85be17834579804ee7acfeaa200155b57152 |
| scripts/run_url_fetch_isolation.py | 88896471f1d20801aaf70b6d5286cc3188a6e6930b89a63d30080bbf99fb7460 |
| results/url_gw_isolation/manifest.json | ed8fe510ce945bc552ac234af64aef4870228d71972f1c507ecc9a9576384019 |
| results/url_gw_isolation/traces.json | 85d0ba211601cab9b243a1834260798b3242cf49a32a0ff575117dd7bc855145 |
| results/url_gw_isolation/REPORT.md | aab76a570827a476ec2a3542e2d439049d24d1f8e153b69a6b8fcba6b9797042 |
| docs/security_clar_shadowleak_plan.md | 690f86f10484819f7c8ba74de8370a680f39db29b145dc532a8f3cf17cb9c2f7 |
| docs/security_clar_eval_source_mapping.md | 15d1d9bd5ae42aec3f90dd3f1c669f4b7de47c33fe9b43cc05da3107f4f908f1 |

### Prior milestones — verified UNCHANGED
| file | sha256 | expected |
|---|---|---|
| src/tool_routing/argverify/disclosure.py | 3009615105e92d4878cd45c3c14c1333475fbdd48c12a69a9387f4bf52e0cf17 | matches clar_arms_freeze |
| src/tool_routing/argverify/min_disclosure.py | 505a0e11114e958ac2a62f0cd7a204b1bfa65df0ca6a5fc0a7f6d0aca861cbb7 | matches |
| src/tool_routing/argverify/clar_arms.py | e299ce51e59b6a77b9a3273431a8a25761e0a1fa1c53f71148ffabec4f1e8908 | matches |
| scripts/run_disclosure_mnd_eval.py | f9de7bd3080ddef7240bf1c58bb9569868148df8e1ccc27f38220e7afd3004a2 | matches |

Earlier failures and versions preserved: all mnd-eval-1.0/2.0 runs,
the `_r2` bugfix rerun, clar_arms_freeze, and every source-review
document remain untouched under results/ and docs/.

## Reproduce

    .venv/bin/python scripts/run_url_fetch_isolation.py   # isolation controls
    .venv/bin/python scripts/run_shadowleak_mechanism_demo.py  # mechanism demo
