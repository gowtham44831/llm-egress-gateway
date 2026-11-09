# Argument-verification development results (20 paired dev cases)

Counts are numerator/denominator; percentages are on n=20 development cases, not a benchmark.

| method | status | next-action | unsup. allowed | sup. blocked | unnec. clarify | arg findings | pairs both correct | lat mean/median/p95/max (s) | parse err | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| schema | ok | 11/20 (55%) | 9/11 (82%) | 0/9 (0%) | 0/20 (0%) | 150/164 (91%) | 1/10 | 0.0000/0.0000/0.0000/0.0000 | 0 | — |
| rule | ok | 20/20 (100%) | 0/11 (0%) | 0/9 (0%) | 0/20 (0%) | 163/164 (99%) | 10/10 | 0.0000/0.0000/0.0000/0.0001 | 0 | — |
| crossrule | ok | 20/20 (100%) | 0/11 (0%) | 0/9 (0%) | 0/20 (0%) | 164/164 (100%) | 10/10 | 0.0001/0.0000/0.0001/0.0001 | 0 | — |
| ai | ok | 8/20 (40%) | 9/11 (82%) | 2/9 (22%) | 2/20 (10%) | 120/164 (73%) | 0/10 | 2.3287/2.1978/2.9558/4.2005 | 1 | completion_tokens=9241, prompt_tokens_details=0, total_tokens=46830, prompt_tokens=37589 |

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
- supported: 119/148
- unresolved: 0/7
- wrong_entity: 0/2