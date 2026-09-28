# Dashboard browser QA

Attempted 2026-09-28 against `analysis/dashboard.html` after the package refactor.

## Automated checks

`node dashboard/check.cjs` passes. The DOM harness covers startup, KPI values against generated summaries, retention selection, empty populations, external coverage, hire-year filtering, relationship scope, annual CPI and supplementary vacancies. This executes dashboard JavaScript against a simulated DOM; it does not establish browser rendering, native control behavior or accessibility.

## Browser verification blocked

Update: Chrome subsequently connected and exposed the dashboard tab, but the browser URL policy rejected access to its local file URL and prohibited alternate access routes. No browser interaction was performed after that rejection.

## User-provided desktop screenshot review

Reviewed screenshots supplied in the conversation on 2026-09-28. The header, cleaning notice, three KPI cards, default cohort selectors, hire-year trend, country comparison and unemployment relationship plot are visible. The repeated relationship screenshots show the same selection, not separate filter tests.

- Visible text and controls are legible; no obvious overlap appears in the shown desktop regions. Some lower content is outside the screenshots, so full-page clipping cannot be assessed.
- KPI values match the conservative results: 87.15% (1,580/1,813), 78.57% (209/266), and 5.10% (82 exits with average headcount 1,607.52). The turnover upper scenario is 5.23%.
- The default cohort selection matches 1,580/1,813. The unemployment view shows 72 cohorts, 1,092 matched mature hires and 13 cohorts below ten hires, consistent with generated analysis.
- Presentation improvements identified: add an explicit retention label to the scatterplot vertical axis and name the selected indicator on the horizontal axis; label 2025 retention as a partial mature cohort near the trend. These are findings, not implemented changes.
- Screenshots do not verify selector changes, hover behavior, disclosure tables, keyboard focus, mobile layout or lower coverage/source panels. Those checks remain outstanding. Images remain conversation attachments; no saved screenshot files are claimed.

The connected computer-use inventory returned no apps and no browsers. Attempts to open Chrome and the integrated browser both returned browser unavailable. No browser screenshots were captured and no visual, keyboard or mobile-layout checks are claimed.

## Checks to complete once a browser is connected

1. Open the generated dashboard and compare all three KPI cards with current metric summaries.
2. Exercise country, hire year, retention objective, business unit, economic signal and coverage selectors; verify the documented filter scope.
3. Select senior retention for 2025 and confirm pending cohorts produce unavailable rates rather than zero, broken plots or NaN.
4. Navigate controls and the methodology disclosure using only the keyboard; confirm visible focus, labels and usable selection behavior.
5. Inspect charts, axis labels, legends, source-age text and tables at desktop and narrow mobile widths; check clipping, overlap and horizontal scrolling.
6. Check hover descriptions and table alternatives, then capture representative screenshots of the default, filtered, empty and narrow layouts.

Any fixes require rerunning the automated checks and repeating affected browser checks. This attempt does not close the browser QA item in the acceptance checklist.
