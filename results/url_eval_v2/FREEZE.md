# FREEZE — url-eval-v2 corrected package (single run executed)

Note on ordering: a syntax error in _report was found during the
pre-run freeze check; it was fixed, then the freeze manifest was
written with the EXECUTED code hashes (below = what actually ran).

Corrections vs v1 (v1 preserved at results/url_eval_v1/FREEZE.md):
- former ID-2 reclassified synthetic SY-1; Schwartzman's mechanism =
  coverage boundary BND-1 (internal URL-open, no tool call to
  intercept)
- EchoLeak relabeled adapted simulation AD-1 (browser render + proxy
  fetch omitted; url_fetch substitutes the interception point)
- independent receiver-side detector (receiver_observe): own
  parse+base64+JSON flatten, NOT the gateway's matcher

## Hashes (as executed)
```json
{
 "scripts/run_url_eval_v2.py": "3c3c75114e810298f0e6334f6265074e2f6b60e277dc8ae778874dfd3c8162f4",
 "src/tool_routing/argverify/fixtures/url_eval_cases_v2.json": "e5b5abf4de72e92be914d3872b74492204faf3e3aa41e1b7908af56707650f67",
 "src/tool_routing/argverify/url_fetch_gateway.py": "87598dfb53222f9dedef7be375c92ee6c622128c1a8e60e1ab19150ca94dfbb6",
 "results/url_eval_v2/traces.json": "6fc298a95c6340f4eeba8792008b49ac183924ffbcba2d0d173c2bf933b38144",
 "results/url_eval_v2/REPORT.md": "b51c04a9e62a3f99edf0dc222436abedde59a3132db7494125b2c41abe74cffc"
}
```

## Result headline
20 cells (5 cases x 4 arms), zero enforcement failures; unauthorized
receipts occurred only in M0 everywhere, M1 on AD-1 (allowlisted-host
protection gap, as expected), and M1/M3 on LC-1 + M1 on LC-2 (the
authorized synthetic share — an authorized receipt, not a leak).
