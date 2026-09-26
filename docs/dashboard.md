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
