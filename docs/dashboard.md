# Workforce dashboard

Open `analysis/dashboard.html` directly in a modern browser. It is self-contained and works offline. Rebuild with the pipeline or `python scripts/build_dashboard.py` after the SQL stage.

Graph choices:

- KPI cards and target markers communicate the current rate and objective. Retention uses 0-100%; turnover uses a clearly labelled 0-10% scale. The classification upper scenario is labelled separately, not presented as a confidence interval.
- A line chart compares retention across hire-year cohorts, with a target line and an accessible data table. This is a cohort comparison, not monthly company retention. Years without mature eligible hires are shown as unavailable and break the line.
- Horizontal country bars share a 0-100% scale, include numerator/denominator counts and target markers. Small samples remain visible rather than implying equal confidence.
- Stacked coverage bars show matched, missing and stale evidence. Exact counts are printed below each bar so color and hover are not required.

Filters: measure, country and business unit affect the retention cohort view; the country comparison intentionally shows all countries for the selected measure/unit. KPI cards remain company-wide. External coverage has a separate metric selector and remains full-population. Audit-status counts follow the selected retention measure, not country/unit filters; labels state this scope.

The dashboard contains aggregate data only. It does not expose employee audit rows. Rates are recomputed from retained/eligible counts, never averaged across groups. Turnover is a snapshot trailing-year rate with no invented historical series. External data coverage is shown; no economic association or causal finding is claimed.

Validation: SQL reconciliation underpins all values. `node dashboard/check.cjs` checks startup, key totals, cohort filtering, empty populations, and coverage calculations with a minimal DOM harness. No browser surface was available for visual QA in this session; the harness does not establish rendering or browser accessibility correctness. Responsive CSS, labelled controls, SVG descriptions and table alternatives are provided but require a final browser review.

## 2026-09-27 continuation

Hire-year filtering now applies to retention and country-comparison views. A selected-signal relationship view shows the existing association cohorts, exposure means, retention rates, sample sizes and source-age ranges. It follows measure/country/year; business unit remains explicitly outside association scope. Full-population sensitivity results are labelled independently of filters. Annual CPI is not interpolated, B?N remains unavailable, and turnover relationship analysis remains deferred. Native source-period timelines and release/retrieval dates are still outstanding.

The dashboard builder now also requires analysis/association_analysis.json. On this host, the preview was rebuilt from the previously embedded SQL payload plus saved association output using Node because Python was unavailable. The expanded Node harness passed. This does not validate the Python builder or full pipeline. No connected browser was available for visual QA. Existing pipeline manifests predate this preview; rerun the full pipeline before submission.

## Vacancy display decision

Following user review, B-N is omitted from the economic-signal selector and external-coverage bars because the current historical pipeline has no verified matches. The underlying evidence, pipeline fields and gap documentation remain available. The displayed vacancy series is explicitly labelled industry and construction (B-F), supplementary. Workforce KPI calculations are unchanged.

Following user review, the full-population sensitivity disclosure was removed from the dashboard. Sensitivity calculations remain in the repository association outputs for analytical review.
