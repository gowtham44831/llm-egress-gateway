# labelset_v2 — reviewer record, disagreements, adjudication

Fill in as batches are returned. Labels live in
`labelset_v2_batch<N>.csv` (one file per reviewer per batch: suffix
`_<reviewer_id>.csv` if more than one reviewer). This file is the
provenance log; it is hashed into the evaluation manifest.

## Reviewers

| reviewer_id | role | prior exposure to NV cases | AI assistance used |
|---|---|---|---|
| (fill) | | none / seen_in_discussion / authored | none / describe |

Note: the assistant authored all NV cases and must not act as a
reviewer. Its guide (v2.1) encodes policy choices that reviewers apply.

## Disagreements (per case)

| case_id | field (A/A′/B/C/D) | reviewer 1 | reviewer 2 | resolution | resolved by | method predictions consulted? |
|---|---|---|---|---|---|---|
| | | | | | | **no** (must stay "no") |

Rules: resolution by discussion or a third reviewer; never by
consulting verifier predictions. If a disagreement is about the guide
rather than the case, the guide is versioned (2.2…) and the case is
marked `guide_changed_after_label=yes`; such cases are reported
separately.

## Underspecified cases

| case_id | reviewers flagging | reason | kept in denominators? |
|---|---|---|---|

Kept unless ≥2 reviewers flag (guide v2.1).

## Merge

`labelset_v2_LABELS.csv` is produced once from the adjudicated rows,
with columns `case_id, A_grounding, A_citation, B_compliance,
C_execution, D_recovery_actions, underspecified, reviewer_ids,
adjudicated, guide_version`. Its sha256 goes into `MANIFEST.json`. It
is never edited afterward.
