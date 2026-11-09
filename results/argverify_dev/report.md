# Argument-verification development results (20 paired dev cases)

Counts are numerator/denominator; percentages are on n=20 development cases, not a benchmark.

| method | status | next-action | unsup. allowed | sup. blocked | unnec. clarify | arg findings | pairs both correct | lat mean/median/p95/max (s) | parse err | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| schema | ok | 11/20 (55%) | 9/11 (82%) | 0/9 (0%) | 0/20 (0%) | 150/164 (91%) | 1/10 | 0.0000/0.0000/0.0000/0.0001 | 0 | — |
| rule | ok | 20/20 (100%) | 0/11 (0%) | 0/9 (0%) | 0/20 (0%) | 163/164 (99%) | 10/10 | 0.0000/0.0000/0.0001/0.0002 | 0 | — |
| crossrule | ok | 20/20 (100%) | 0/11 (0%) | 0/9 (0%) | 0/20 (0%) | 164/164 (100%) | 10/10 | 0.0001/0.0001/0.0001/0.0001 | 0 | — |
| ai | ok | 9/20 (45%) | 10/11 (91%) | 0/9 (0%) | 1/20 (5%) | 137/164 (84%) | 0/10 | 13.0626/2.4729/5.8507/211.1674 | 1 | completion_tokens=51347, prompt_tokens_details=0, prompt_tokens=36260, total_tokens=87607 |

### schema: argument findings by expected category
- contradicted: 0/3
- missing: 2/4
- supported: 148/148
- unresolved: 0/7
- wrong_entity: 0/2

### rule: argument findings by expected category
- contradicted: 2/3
- missing: 4/4
- supported: 148/148
- unresolved: 7/7
- wrong_entity: 2/2

### crossrule: argument findings by expected category
- contradicted: 3/3
- missing: 4/4
- supported: 148/148
- unresolved: 7/7
- wrong_entity: 2/2

### ai: argument findings by expected category
- contradicted: 0/3
- missing: 1/4
- supported: 136/148
- unresolved: 0/7
- wrong_entity: 0/2