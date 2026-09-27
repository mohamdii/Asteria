# Exploratory external-signal analysis

Exploratory descriptive associations; no hypothesis tests, p-values, prediction or causal estimates.
Country x hire quarter for unemployment/B-F; country x hire year for CPI.
Mean of employee-specific as-of values among matched mature hires; a cohort exposure summary, not a newly measured economic period value. Source frequency/period/vintage remain in joined audit.
Each cohort receives equal weight in correlations; exposure means within cohorts are employee-weighted.
Cohorts can reuse source periods/vintages. Neither employee count nor cohort count is an independent economic sample size.
No inferential intervals because repeated observations and only six countries make naive independence assumptions inappropriate. Report leave-one-country-out and minimum-size sensitivity, not confidence intervals.
Within-country centering removes country mean differences only; calendar trends, composition, selection, and omitted factors remain. Breakdown tables expose country/year/business-unit selection.
All three preselected available indicators and both required retention populations are reported, including weak/unstable patterns. No significance-based selection.
Deferred relationship estimation: one annual window and six country contexts do not support a credible repeated-period analysis. Snapshot KPI/coverage remain valid.
Minimum 10 mature matched hires is an exploratory stability check, not a guarantee of reliability.
B-F supplementary sector measure only. Preferred B-N has no verified historical matches.

| Population | Indicator | Matched | Unmatched | Cohorts | Cohorts <10 | Pooled r | Within-country r | Min-10 r |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| new_hire_6m | unemployment | 1092 | 721 | 72 | 13 | -0.123 | -0.170 | -0.071 |
| new_hire_6m | inflation | 1808 | 5 | 30 | 0 | 0.162 | 0.176 | 0.162 |
| new_hire_6m | vacancies_bf_supplementary | 1408 | 405 | 94 | 14 | -0.009 | -0.028 | 0.054 |
| senior_hire_12m | unemployment | 150 | 116 | 56 | 56 | -0.023 | -0.170 | unavailable |
| senior_hire_12m | inflation | 266 | 0 | 24 | 6 | 0.094 | 0.175 | 0.087 |
| senior_hire_12m | vacancies_bf_supplementary | 211 | 55 | 75 | 75 | 0.092 | 0.004 | unavailable |

## Interpretation guardrails

A correlation describes co-movement in this synthetic matched subset. Compare pooled, centered and sensitivity results before describing a pattern. Small or sign-changing results are not stable evidence. Higher correlation does not establish practical importance or causality. Inspect the JSON breakdowns before generalizing beyond matched hires.
