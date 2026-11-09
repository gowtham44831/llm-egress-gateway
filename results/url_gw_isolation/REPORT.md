# url-fetch isolation — content inspection vs host filtering

Synthetic engineering controls (fictional data, loopback receivers). NOT public incidents, NOT independent evaluation cases.

| case | allowlist_only | full_gateway | expected(full) | received (AO / FG) | enforcement ok |
|---|---|---|---|---|---|
| preserved_offlist | block | block | yes | 0 / 0 | yes |
| preserved_benign | allow | allow | yes | 1 / 1 | yes |
| U1 | allow | block | yes | 1 / 0 | yes |
| U2 | allow | allow | yes | 1 / 1 | yes |
| U3 | allow | block | yes | 1 / 0 | yes |

Cases where the methods differ: ['U1', 'U3']

Conclusion: on these controls, content inspection ADDS enforcement beyond host filtering (see findings per case in traces.json).

Disclosed limits: application-supplied field_metadata is an assumption; decoding is bounded URL + strict base64 only; exact matching; loopback-only destinations; redirects off.