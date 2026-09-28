# Dashboard browser QA

## Current status

On 2026-09-28 the user confirmed completion of the requested keyboard-navigation, hover-behavior and error-state checks. Record these as user-reported passes, alongside the earlier mobile-layout confirmation and screenshot evidence. This closes the requested manual browser QA item. The historical outstanding-check statements below describe earlier stages and are superseded by this update. The user did not supply individual error scenarios, device/browser versions or a formal accessibility audit; no agent-operated browser verification or malformed-payload injection test is claimed.

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
- Presentation improvements identified: add an explicit retention label to the scatterplot vertical axis and name the selected indicator on the horizontal axis; label 2025 retention as a partial mature cohort near the trend. Implemented in the template and rebuilt dashboard on 2026-09-28. The vertical label identifies retention at the selected milestone; the horizontal label names the selected indicator and its units. A note explains partial six-month maturity and unavailable senior retention for 2025.
- Additional screenshots show the external coverage panel, expanded relationship table, audit counts and interpretation notes. Coverage reads 1,092/1,813 for unemployment, 1,808/1,813 for CPI and 1,408/1,813 for supplementary vacancies. The audit counts total 2,400. Visible table columns and lower panels are legible without obvious overlap.
- The expanded table disclosure has a visible focus outline; this does not establish keyboard-only navigation. Replace the interpretation phrase "both known-classification scenarios" with wording distinguishing confirmed regretted exits from the scenario including potentially regretted unknown departures. Implemented on 2026-09-28 in the template and rebuilt dashboard.
- Screenshots do not verify selector changes, hover behavior, keyboard-only navigation or the source panel. Images remain conversation attachments; no saved screenshot files are claimed.

## User-reported mobile check

On 2026-09-28 the user confirmed that the dashboard works in the mobile layout. Record this as a user-verified pass, not an automated or agent-operated browser check. Device, browser and viewport dimensions were not supplied. The accompanying image shows two cards side by side and does not independently establish a narrow mobile viewport.

## Presentation screenshots

The supplied KPI overview, retention trend/country comparison, economic signals and evidence coverage screenshots are candidates for presentation use. They remain conversation attachments, not saved project assets. A senior twelve-month retention view filtered to 2025 is still requested to illustrate immature cohorts displaying unavailable rates.

## Remaining browser checks

1. Open the generated dashboard and compare all three KPI cards with current metric summaries.
2. Exercise country, hire year, retention objective, business unit, economic signal and coverage selectors; verify the documented filter scope.
3. Select senior retention for 2025 and confirm pending cohorts produce unavailable rates rather than zero, broken plots or NaN.
4. Navigate controls and the methodology disclosure using only the keyboard; confirm visible focus, labels and usable selection behavior.
5. Mobile layout has a user-reported pass. Capture a representative narrow viewport and record its dimensions if reproducible visual evidence is needed; inspect charts and wide tables for clipping and horizontal scrolling.
6. Check hover descriptions and table alternatives, then capture representative screenshots of the default, filtered, empty and narrow layouts.

Any fixes require rerunning the automated checks and repeating affected browser checks. This attempt does not close the browser QA item in the acceptance checklist.

## Wording update verification

Rebuilt `analysis/dashboard.html` using `python -m asteria.reporting.dashboard` and ran `node dashboard/check.cjs`; all existing dashboard checks passed. Metric calculations were unchanged. The revised wording and labels still require visual review in the browser.

## Senior 2025 screenshot confirmation

On 2026-09-28 the user supplied a screenshot with Senior twelve-month retention and hire year 2025 selected. The selected population displays 0 / 0 mature hires retained and Unavailable. The visible country comparison also shows Unavailable. This confirms the expected displayed empty-population state for that selection. Keyboard-only navigation and hover checks remain unverified.

