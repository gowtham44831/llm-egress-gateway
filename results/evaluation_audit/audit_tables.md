# Evaluation audit -- generated tables

Source run: `results/toolret_pilot` (read-only). Labels are known-incomplete; 'correct' = top-1 in annotated labels.

## Frozen global policy, split = dev

| method | policy | threshold | scenario | n | accepted | correct | incorrect | coverage [95% Wilson] | selective risk [95% Wilson] |
|---|---|---|---|---|---|---|---|---|---|
| bm25 | always_top1 | n/a | distractors_added | 300 | 300 | 78 | 222 | 300/300 = 1.000 [0.987, 1.000] | 222/300 = 0.740 [0.688, 0.786] |
| bm25 | always_top1 | n/a | known_removed | 300 | 300 | 0 | 300 | 300/300 = 1.000 [0.987, 1.000] | 300/300 = 1.000 [0.987, 1.000] |
| bm25 | always_top1 | n/a | original | 300 | 300 | 136 | 164 | 300/300 = 1.000 [0.987, 1.000] | 164/300 = 0.547 [0.490, 0.602] |
| bm25 | always_top1 | n/a | ALL (mixed) | 900 | 900 | 214 | 686 | 900/900 = 1.000 [1.000, 1.000] | 686/900 = 0.762 [0.730, 0.792] |
| bm25 | score_threshold | 113.3 | distractors_added | 300 | 6 | 2 | 4 | 6/300 = 0.020 [0.009, 0.043] | 4/6 = 0.667 [0.300, 0.903] |
| bm25 | score_threshold | 113.3 | known_removed | 300 | 3 | 0 | 3 | 3/300 = 0.010 [0.003, 0.029] | 3/3 = 1.000 [0.439, 1.000] |
| bm25 | score_threshold | 113.3 | original | 300 | 6 | 4 | 2 | 6/300 = 0.020 [0.009, 0.043] | 2/6 = 0.333 [0.097, 0.700] |
| bm25 | score_threshold | 113.3 | ALL (mixed) | 900 | 15 | 6 | 9 | 15/900 = 0.017 [0.004, 0.032] | 9/15 = 0.600 [0.125, 0.909] |
| bm25 | margin_threshold | 43.57 | distractors_added | 300 | 1 | 1 | 0 | 1/300 = 0.003 [0.001, 0.019] | 0/1 = 0.000 [0.000, 0.793] |
| bm25 | margin_threshold | 43.57 | known_removed | 300 | 4 | 0 | 4 | 4/300 = 0.013 [0.005, 0.034] | 4/4 = 1.000 [0.510, 1.000] |
| bm25 | margin_threshold | 43.57 | original | 300 | 8 | 6 | 2 | 8/300 = 0.027 [0.014, 0.052] | 2/8 = 0.250 [0.071, 0.591] |
| bm25 | margin_threshold | 43.57 | ALL (mixed) | 900 | 13 | 7 | 6 | 13/900 = 0.014 [0.006, 0.026] | 6/13 = 0.462 [0.100, 0.818] |
| embedding | always_top1 | n/a | distractors_added | 300 | 300 | 114 | 186 | 300/300 = 1.000 [0.987, 1.000] | 186/300 = 0.620 [0.564, 0.673] |
| embedding | always_top1 | n/a | known_removed | 300 | 300 | 0 | 300 | 300/300 = 1.000 [0.987, 1.000] | 300/300 = 1.000 [0.987, 1.000] |
| embedding | always_top1 | n/a | original | 300 | 300 | 154 | 146 | 300/300 = 1.000 [0.987, 1.000] | 146/300 = 0.487 [0.431, 0.543] |
| embedding | always_top1 | n/a | ALL (mixed) | 900 | 900 | 268 | 632 | 900/900 = 1.000 [1.000, 1.000] | 632/900 = 0.702 [0.666, 0.737] |
| embedding | score_threshold | 0.8324 | distractors_added | 300 | 2 | 2 | 0 | 2/300 = 0.007 [0.002, 0.024] | 0/2 = 0.000 [0.000, 0.658] |
| embedding | score_threshold | 0.8324 | known_removed | 300 | 0 | 0 | 0 | 0/300 = 0.000 [0.000, 0.013] | 0/0 = undef undef |
| embedding | score_threshold | 0.8324 | original | 300 | 2 | 2 | 0 | 2/300 = 0.007 [0.002, 0.024] | 0/2 = 0.000 [0.000, 0.658] |
| embedding | score_threshold | 0.8324 | ALL (mixed) | 900 | 4 | 4 | 0 | 4/900 = 0.004 [0.000, 0.013] | 0/4 = 0.000 [0.000, 0.000] |
| embedding | margin_threshold | 0.3401 | distractors_added | 300 | 1 | 1 | 0 | 1/300 = 0.003 [0.001, 0.019] | 0/1 = 0.000 [0.000, 0.793] |
| embedding | margin_threshold | 0.3401 | known_removed | 300 | 0 | 0 | 0 | 0/300 = 0.000 [0.000, 0.013] | 0/0 = undef undef |
| embedding | margin_threshold | 0.3401 | original | 300 | 4 | 4 | 0 | 4/300 = 0.013 [0.005, 0.034] | 0/4 = 0.000 [0.000, 0.490] |
| embedding | margin_threshold | 0.3401 | ALL (mixed) | 900 | 5 | 5 | 0 | 5/900 = 0.006 [0.001, 0.012] | 0/5 = 0.000 [0.000, 0.000] |

## Frozen global policy, split = val

| method | policy | threshold | scenario | n | accepted | correct | incorrect | coverage [95% Wilson] | selective risk [95% Wilson] |
|---|---|---|---|---|---|---|---|---|---|
| bm25 | always_top1 | n/a | distractors_added | 100 | 100 | 27 | 73 | 100/100 = 1.000 [0.963, 1.000] | 73/100 = 0.730 [0.636, 0.807] |
| bm25 | always_top1 | n/a | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | always_top1 | n/a | original | 100 | 100 | 47 | 53 | 100/100 = 1.000 [0.963, 1.000] | 53/100 = 0.530 [0.433, 0.625] |
| bm25 | always_top1 | n/a | ALL (mixed) | 300 | 300 | 74 | 226 | 300/300 = 1.000 [1.000, 1.000] | 226/300 = 0.753 [0.697, 0.810] |
| bm25 | score_threshold | 113.3 | distractors_added | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| bm25 | score_threshold | 113.3 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | score_threshold | 113.3 | original | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| bm25 | score_threshold | 113.3 | ALL (mixed) | 300 | 2 | 2 | 0 | 2/300 = 0.007 [0.000, 0.020] | 0/2 = 0.000 [0.000, 0.000] |
| bm25 | margin_threshold | 43.57 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | original | 100 | 2 | 2 | 0 | 2/100 = 0.020 [0.006, 0.070] | 0/2 = 0.000 [0.000, 0.658] |
| bm25 | margin_threshold | 43.57 | ALL (mixed) | 300 | 2 | 2 | 0 | 2/300 = 0.007 [0.000, 0.017] | 0/2 = 0.000 [0.000, 0.000] |
| embedding | always_top1 | n/a | distractors_added | 100 | 100 | 37 | 63 | 100/100 = 1.000 [0.963, 1.000] | 63/100 = 0.630 [0.532, 0.718] |
| embedding | always_top1 | n/a | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | always_top1 | n/a | original | 100 | 100 | 54 | 46 | 100/100 = 1.000 [0.963, 1.000] | 46/100 = 0.460 [0.366, 0.557] |
| embedding | always_top1 | n/a | ALL (mixed) | 300 | 300 | 91 | 209 | 300/300 = 1.000 [1.000, 1.000] | 209/300 = 0.697 [0.643, 0.757] |
| embedding | score_threshold | 0.8324 | distractors_added | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| embedding | score_threshold | 0.8324 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | score_threshold | 0.8324 | original | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| embedding | score_threshold | 0.8324 | ALL (mixed) | 300 | 2 | 2 | 0 | 2/300 = 0.007 [0.000, 0.020] | 0/2 = 0.000 [0.000, 0.000] |
| embedding | margin_threshold | 0.3401 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | margin_threshold | 0.3401 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | margin_threshold | 0.3401 | original | 100 | 3 | 3 | 0 | 3/100 = 0.030 [0.010, 0.085] | 0/3 = 0.000 [0.000, 0.561] |
| embedding | margin_threshold | 0.3401 | ALL (mixed) | 300 | 3 | 3 | 0 | 3/300 = 0.010 [0.000, 0.023] | 0/3 = 0.000 [0.000, 0.000] |

## Frozen global policy, split = test

| method | policy | threshold | scenario | n | accepted | correct | incorrect | coverage [95% Wilson] | selective risk [95% Wilson] |
|---|---|---|---|---|---|---|---|---|---|
| bm25 | always_top1 | n/a | distractors_added | 100 | 100 | 26 | 74 | 100/100 = 1.000 [0.963, 1.000] | 74/100 = 0.740 [0.646, 0.816] |
| bm25 | always_top1 | n/a | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | always_top1 | n/a | original | 100 | 100 | 48 | 52 | 100/100 = 1.000 [0.963, 1.000] | 52/100 = 0.520 [0.423, 0.615] |
| bm25 | always_top1 | n/a | ALL (mixed) | 300 | 300 | 74 | 226 | 300/300 = 1.000 [1.000, 1.000] | 226/300 = 0.753 [0.697, 0.803] |
| bm25 | score_threshold | 113.3 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | score_threshold | 113.3 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | score_threshold | 113.3 | original | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | score_threshold | 113.3 | ALL (mixed) | 300 | 0 | 0 | 0 | 0/300 = 0.000 [0.000, 0.000] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | original | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 43.57 | ALL (mixed) | 300 | 0 | 0 | 0 | 0/300 = 0.000 [0.000, 0.000] | 0/0 = undef undef |
| embedding | always_top1 | n/a | distractors_added | 100 | 100 | 32 | 68 | 100/100 = 1.000 [0.963, 1.000] | 68/100 = 0.680 [0.583, 0.763] |
| embedding | always_top1 | n/a | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | always_top1 | n/a | original | 100 | 100 | 43 | 57 | 100/100 = 1.000 [0.963, 1.000] | 57/100 = 0.570 [0.472, 0.663] |
| embedding | always_top1 | n/a | ALL (mixed) | 300 | 300 | 75 | 225 | 300/300 = 1.000 [1.000, 1.000] | 225/300 = 0.750 [0.690, 0.807] |
| embedding | score_threshold | 0.8324 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | score_threshold | 0.8324 | known_removed | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | score_threshold | 0.8324 | original | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | score_threshold | 0.8324 | ALL (mixed) | 300 | 0 | 0 | 0 | 0/300 = 0.000 [0.000, 0.000] | 0/0 = undef undef |
| embedding | margin_threshold | 0.3401 | distractors_added | 100 | 2 | 2 | 0 | 2/100 = 0.020 [0.006, 0.070] | 0/2 = 0.000 [0.000, 0.658] |
| embedding | margin_threshold | 0.3401 | known_removed | 100 | 1 | 0 | 1 | 1/100 = 0.010 [0.002, 0.054] | 1/1 = 1.000 [0.207, 1.000] |
| embedding | margin_threshold | 0.3401 | original | 100 | 4 | 4 | 0 | 4/100 = 0.040 [0.016, 0.098] | 0/4 = 0.000 [0.000, 0.490] |
| embedding | margin_threshold | 0.3401 | ALL (mixed) | 300 | 7 | 6 | 1 | 7/300 = 0.023 [0.007, 0.047] | 1/7 = 0.143 [0.000, 0.500] |

## Scenario-specific thresholds (DIAGNOSTIC ONLY, not deployable)

### split = val

| method | policy | threshold | scenario | n | accepted | correct | incorrect | coverage [95% Wilson] | selective risk [95% Wilson] |
|---|---|---|---|---|---|---|---|---|---|
| bm25 | score_threshold | 113.3 | distractors_added | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| bm25 | score_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | score_threshold | 83.96 | original | 100 | 4 | 4 | 0 | 4/100 = 0.040 [0.016, 0.098] | 0/4 = 0.000 [0.000, 0.490] |
| bm25 | margin_threshold | 33.6 | distractors_added | 100 | 2 | 2 | 0 | 2/100 = 0.020 [0.006, 0.070] | 0/2 = 0.000 [0.000, 0.658] |
| bm25 | margin_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | margin_threshold | 11.13 | original | 100 | 22 | 20 | 2 | 22/100 = 0.220 [0.150, 0.311] | 2/22 = 0.091 [0.025, 0.278] |
| embedding | score_threshold | 0.8324 | distractors_added | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| embedding | score_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | score_threshold | 0.8324 | original | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| embedding | margin_threshold | 0.2129 | distractors_added | 100 | 3 | 3 | 0 | 3/100 = 0.030 [0.010, 0.085] | 0/3 = 0.000 [0.000, 0.561] |
| embedding | margin_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | margin_threshold | 0.08765 | original | 100 | 24 | 22 | 2 | 24/100 = 0.240 [0.167, 0.332] | 2/24 = 0.083 [0.023, 0.258] |

### split = test

| method | policy | threshold | scenario | n | accepted | correct | incorrect | coverage [95% Wilson] | selective risk [95% Wilson] |
|---|---|---|---|---|---|---|---|---|---|
| bm25 | score_threshold | 113.3 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | score_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | score_threshold | 83.96 | original | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| bm25 | margin_threshold | 33.6 | distractors_added | 100 | 1 | 1 | 0 | 1/100 = 0.010 [0.002, 0.054] | 0/1 = 0.000 [0.000, 0.793] |
| bm25 | margin_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| bm25 | margin_threshold | 11.13 | original | 100 | 23 | 20 | 3 | 23/100 = 0.230 [0.158, 0.322] | 3/23 = 0.130 [0.045, 0.321] |
| embedding | score_threshold | 0.8324 | distractors_added | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | score_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | score_threshold | 0.8324 | original | 100 | 0 | 0 | 0 | 0/100 = 0.000 [0.000, 0.037] | 0/0 = undef undef |
| embedding | margin_threshold | 0.2129 | distractors_added | 100 | 6 | 5 | 1 | 6/100 = 0.060 [0.028, 0.125] | 1/6 = 0.167 [0.030, 0.564] |
| embedding | margin_threshold | -inf | known_removed | 100 | 100 | 0 | 100 | 100/100 = 1.000 [0.963, 1.000] | 100/100 = 1.000 [0.963, 1.000] |
| embedding | margin_threshold | 0.08765 | original | 100 | 30 | 24 | 6 | 30/100 = 0.300 [0.219, 0.396] | 6/30 = 0.200 [0.095, 0.373] |

## Paired comparisons (always_top1 label agreement, query-grouped bootstrap, 2000 resamples)

| comparison | n paired | A correct | B correct | A-only | B-only | diff | 95% CI |
|---|---|---|---|---|---|---|---|
| val::bm25::original_minus_distractors_added | 100 | 47 | 27 | 20 | 0 | +0.200 | [+0.120, +0.280] |
| val::embedding::original_minus_distractors_added | 100 | 54 | 37 | 17 | 0 | +0.170 | [+0.100, +0.250] |
| val::original::bm25_minus_embedding | 100 | 47 | 54 | 9 | 16 | -0.070 | [-0.160, +0.030] |
| val::distractors_added::bm25_minus_embedding | 100 | 27 | 37 | 9 | 19 | -0.100 | [-0.200, +0.010] |
| test::bm25::original_minus_distractors_added | 100 | 48 | 26 | 22 | 0 | +0.220 | [+0.140, +0.310] |
| test::embedding::original_minus_distractors_added | 100 | 43 | 32 | 11 | 0 | +0.110 | [+0.050, +0.180] |
| test::original::bm25_minus_embedding | 100 | 48 | 43 | 15 | 10 | +0.050 | [-0.050, +0.140] |
| test::distractors_added::bm25_minus_embedding | 100 | 26 | 32 | 9 | 15 | -0.060 | [-0.150, +0.030] |

## Catalog checks

| check | checked | violations |
|---|---|---|
| all_three_scenarios_present | 500 | 0 |
| original_contains_every_annotated_tool | 500 | 0 |
| known_removed_equals_original_minus_annotated | 500 | 0 |
| known_removed_contains_no_annotated_tool | 500 | 0 |
| distractors_not_in_original_by_id | 500 | 0 |
| distractors_from_held_out_pool | 500 | 0 |
| distractors_resolve_to_known_tools | 500 | 0 |
| distractors_unique_within_catalog | 500 | 0 |
| distractors_added_equals_original_plus_distractors | 500 | 0 |
| distractors_content_distinct_from_original | 500 | 0 |
| distractors_not_annotated_valid | 500 | 0 |
| catalog_tool_ids_unique | 1500 | 0 |

## Catalog sizes

| subset | scenario | n | min | median | mean | max |
|---|---|---|---|---|---|---|
| apibank | distractors_added | 28 | 104 | 104.0 | 104.0 | 104 |
| apibank | known_removed | 28 | 97 | 99.0 | 99.32 | 100 |
| apibank | original | 28 | 101 | 101.0 | 101.0 | 101 |
| apigen | distractors_added | 270 | 3608 | 3608.0 | 3608.0 | 3608 |
| apigen | known_removed | 270 | 3601 | 3604.0 | 3603.64 | 3604 |
| apigen | original | 270 | 3605 | 3605.0 | 3605.0 | 3605 |
| gorilla-huggingface | distractors_added | 128 | 910 | 910.0 | 910.0 | 910 |
| gorilla-huggingface | known_removed | 128 | 906 | 906.0 | 906.0 | 906 |
| gorilla-huggingface | original | 128 | 907 | 907.0 | 907.0 | 907 |
| metatool | distractors_added | 48 | 203 | 203.0 | 203.0 | 203 |
| metatool | known_removed | 48 | 198 | 199.0 | 198.9 | 199 |
| metatool | original | 48 | 200 | 200.0 | 200.0 | 200 |
| toolalpaca | distractors_added | 26 | 1940 | 1940.0 | 1940.0 | 1940 |
| toolalpaca | known_removed | 26 | 1936 | 1936.0 | 1936.0 | 1936 |
| toolalpaca | original | 26 | 1937 | 1937.0 | 1937.0 | 1937 |
| ALL | original | 500 | 101 | 3605.0 | 2304.47 | 3605 |
| ALL | known_removed | 500 | 97 | 3603.0 | 2303.23 | 3604 |
| ALL | distractors_added | 500 | 104 | 3608.0 | 2307.47 | 3608 |

## Review sample strata

| stratum | population | sampled |
|---|---|---|
| apibank|1_label | 48 | 10 |
| apibank|2plus_labels | 53 | 10 |
| apigen|1_label | 712 | 10 |
| apigen|2plus_labels | 288 | 10 |
| gorilla-huggingface|1_label | 500 | 20 |
| metatool|1_label | 179 | 10 |
| metatool|2plus_labels | 21 | 10 |
| toolalpaca|1_label | 94 | 20 |

Bounded-catalog review items: 40 -> {'items': 'results/evaluation_audit/review/bounded_catalog_review_items.csv', 'tools': 'results/evaluation_audit/review/bounded_catalog_review_tools.csv', 'key': 'results/evaluation_audit/review/bounded_catalog_review_KEY_do_not_open_before_review.csv'}

## Pilot REPORT.md cross-check (test, always_top1)

- bm25/original: pilot top1_accuracy=0.48 vs audit 48/100
- bm25/distractors_added: pilot top1_accuracy=0.26 vs audit 26/100
- bm25/known_removed: pilot top1_accuracy=0.0 vs audit 0/100
- embedding/original: pilot top1_accuracy=0.43 vs audit 43/100
- embedding/distractors_added: pilot top1_accuracy=0.32 vs audit 32/100
- embedding/known_removed: pilot top1_accuracy=0.0 vs audit 0/100
