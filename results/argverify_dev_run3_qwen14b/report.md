# Argument-verification development results (20 paired dev cases)

Counts are numerator/denominator; percentages are on n=20 development cases, not a benchmark.

| method | status | next-action | unsup. allowed | sup. blocked | unnec. clarify | arg findings | pairs both correct | lat mean/median/p95/max (s) | parse err | tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| ai | ok | 16/20 (80%) | 3/11 (27%) | 0/9 (0%) | 1/20 (5%) | 157/164 (96%) | 6/10 | 43.3923/41.8677/65.7781/77.7382 | 0 | completion_tokens=18282, total_tokens=55871, prompt_tokens=37589, prompt_tokens_details=0 |

### ai: argument findings by expected category
- contradicted: 3/3
- missing: 3/4
- supported: 148/148
- unresolved: 1/7
- wrong_entity: 2/2