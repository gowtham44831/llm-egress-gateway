# url-eval-v2 report — corrected package

Suites reported separately; NOT an incident prevention rate.

## incident_derived (1 cases)
| case | arm | decision | unauthorized_receipt | received | enforcement_failure |
|---|---|---|---|---|---|
| ID-1 | M0_no_gateway | allow | True | 1 | False |
| ID-1 | M1_allowlist | block | False | 0 | False |
| ID-1 | M2_content_inspect | block | False | 0 | False |
| ID-1 | M3_full_gateway | block | False | 0 | False |

## adapted_simulation (1 cases)
| case | arm | decision | unauthorized_receipt | received | enforcement_failure |
|---|---|---|---|---|---|
| AD-1 | M0_no_gateway | allow | True | 1 | False |
| AD-1 | M1_allowlist | allow | True | 1 | False |
| AD-1 | M2_content_inspect | block | False | 0 | False |
| AD-1 | M3_full_gateway | block | False | 0 | False |

## synthetic (3 cases)
| case | arm | decision | unauthorized_receipt | received | enforcement_failure |
|---|---|---|---|---|---|
| SY-1 | M0_no_gateway | allow | True | 1 | False |
| SY-1 | M1_allowlist | block | False | 0 | False |
| SY-1 | M2_content_inspect | block | False | 0 | False |
| SY-1 | M3_full_gateway | block | False | 0 | False |
| LC-1 | M0_no_gateway | allow | True | 1 | False |
| LC-1 | M1_allowlist | allow | True | 1 | False |
| LC-1 | M2_content_inspect | block | False | 0 | False |
| LC-1 | M3_full_gateway | allow | True | 1 | False |
| LC-2 | M0_no_gateway | allow | True | 1 | False |
| LC-2 | M1_allowlist | allow | True | 1 | False |
| LC-2 | M2_content_inspect | block | False | 0 | False |
| LC-2 | M3_full_gateway | block | False | 0 | False |

## Summary
enforcement failures: []
cells with unauthorized receipt: [{'case': 'ID-1', 'arm': 'M0_no_gateway'}, {'case': 'AD-1', 'arm': 'M0_no_gateway'}, {'case': 'AD-1', 'arm': 'M1_allowlist'}, {'case': 'SY-1', 'arm': 'M0_no_gateway'}, {'case': 'LC-1', 'arm': 'M0_no_gateway'}, {'case': 'LC-1', 'arm': 'M1_allowlist'}, {'case': 'LC-1', 'arm': 'M3_full_gateway'}, {'case': 'LC-2', 'arm': 'M0_no_gateway'}, {'case': 'LC-2', 'arm': 'M1_allowlist'}]
Counts by suite are above; variants never merged with incidents.