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
| new_hire_6m | unemployment | 1102 | 720 | 72 | 12 | -0.161 | -0.166 | -0.104 |
| new_hire_6m | inflation | 1822 | 0 | 30 | 0 | 0.220 | 0.224 | 0.220 |
| new_hire_6m | vacancies_bf_supplementary | 1419 | 403 | 94 | 14 | -0.050 | -0.110 | 0.002 |
| senior_hire_12m | unemployment | 146 | 114 | 56 | 56 | 0.021 | -0.149 | unavailable |
| senior_hire_12m | inflation | 260 | 0 | 24 | 7 | 0.096 | 0.218 | 0.098 |
| senior_hire_12m | vacancies_bf_supplementary | 207 | 53 | 75 | 75 | 0.128 | -0.010 | unavailable |

## Interpretation guardrails

A correlation describes co-movement in this synthetic matched subset. Compare pooled, centered and sensitivity results before describing a pattern. Small or sign-changing results are not stable evidence. Higher correlation does not establish practical importance or causality. Inspect the JSON breakdowns before generalizing beyond matched hires.
