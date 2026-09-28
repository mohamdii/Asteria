# Submission requirements review

Reviewed 2026-09-28 against the preserved static requirements in `config/assessment_reference.json`, current implementation, generated evidence, README, AI usage log, presentation and browser QA notes. The retired source HTML was not opened or executed. This review supersedes old status statements in the acceptance checklist.

**Conclusion: the core analytical product is implemented and reproducible, but full submission completion is not yet established.**

## Requirements satisfied for the documented scope

- Problem refinement: decision, employment grain, metric semantics, boundary dates, assumptions, rejected scope and consequences appear in `requirements-and-decisions.md`.
- Public evidence: Eurostat and World Bank provide unemployment, annual CPI inflation and supplementary B-F vacancies. Source contracts describe dimensions, cadence, terms, access metadata, timing and limitations. Saved historical evidence spans multiple years, with explicitly incomplete point-in-time matching. Complete historical employee coverage is not a requirement.
- Data layers and lineage: preserved raw evidence, canonical economic records, curated workforce, employee-level metric/join audits, SQL reporting and HTML consumption exist. Source metadata and hashes support tracing selected observations.
- All three metrics: eligible populations, maturity, invalid-date exclusions, seniority sensitivity and unknown-turnover scenarios are implemented and reconciled.
- Temporal integrity: strict prior publication, reference-period checks, stale-value limits and native annual CPI frequency are explicit and tested.
- Analysis and findings: descriptive correlations, sample counts, matched/unmatched comparisons, country-centering and stability checks support multiple findings and non-findings. The project does not claim independent economic samples or causality. Turnover relationship analysis is explicitly deferred for the single-window scope.
- Interactive product: country, hire year, retention measure and business-unit filters, KPI status, retention trends, economic relationship views, tables, coverage and exclusions exist. Economic relationships include all business units, as disclosed. Turnover is a snapshot KPI and coverage population.
- Local stack: Python 3.12.14, SQL/SQLite and self-contained HTML satisfy the portable implementation requirement. Paid infrastructure is not needed.
- Proposed production view: `production-architecture.md` covers ADF, ADLS, Databricks, SQL/Power BI, secrets, scheduling, observability, access and promotion. Deployment is not required and is not claimed.
- Repeatable core: the latest pipeline ran twice successfully, including Python tests. All 34 recorded output hashes still match current files. The separate Node dashboard harness passed in the preceding rerun. This review did not rerun tests unnecessarily.
- Generated evidence: curated files, quality/coverage reports, analytical outputs and the self-contained HTML export exist. User screenshots and mobile confirmation are documented, with the senior-2025 unavailable state confirmed.

## Remaining acceptance work

### Presentation format and AI accountability

Resolved: `presentation/workforce-retention-submission.pdf` and `presentation/workforce-retention.md` provide the requested portable deck formats. The 13-slide guide totals 900 seconds and explicitly covers human direction, Codex implementation, rejected generator recovery, verification and limitations. The earlier PDF remains unchanged as a source copy.

### Safe partial failure and error states

Resolved for the pipeline entry point on 2026-09-28: each run copies its code and saved inputs into an isolated release workspace. It builds, tests, verifies output hashes and optionally repeats there. A completed folder becomes visible through an atomic replacement of `releases/current.json`. Failures before that switch preserve the previous release. Three publication tests cover interrupted/failed builds, corrupt outputs, failed pointer replacement and successful switching. Full repeat replay produced 34 identical outputs and dashboard DOM checks passed before publication. Consumers must read the pointer once and use that release for all artifacts. Top-level outputs are legacy snapshots. Direct module execution bypasses publication. This does not certify storage-device failure durability or malformed dashboard payload handling.

### Accessibility verification

Update on 2026-09-28: the user confirmed the requested keyboard-navigation, hover-behavior and error-state checks as done. The manual browser QA item is closed on user-reported evidence, alongside mobile confirmation and screenshots. Individual error scenarios were not specified, so this does not establish malformed-payload injection coverage or a formal accessibility audit. The separate partial-publication finding above remains open. Browser URL policy blocked agent access; no retry or bypass occurred.

### Current documentation and human effort

The main README, requirements document, acceptance checklist and AI usage summary now reflect completed analysis, publication and user-reported QA. Historical AI log entries remain clearly labeled. The candidate reported approximately 15 hours of effort on 2026-09-28.

### Submission and access

The local repository has a GitHub remote, which does not prove reviewer access or submission. Current changes and the presentation remain uncommitted in the inspected working tree. Confirm access/deadline and deliver the intended version. Choose one final deck and exclude intermediate chart-workbook folders, alternate draft decks and Office lock files from the handoff.

## Additional confidence check

A fresh-copy installation/replay of the final artifact set remains advisable. Existing clean-environment evidence predates SQL/dashboard changes. This is separate from the completed same-environment repeat check and is not an additional explicit deliverable imposed by the brief. Minimum-version and cross-platform certification are also not claimed.

## Limits that do not themselves block the chosen scope

Unknown countries may remain unknown, 2025 senior cohorts may remain pending, B-F may remain explicitly supplementary, and historical context may remain unmatched. No folder rename or deployed Databricks/Power BI system is required. Avoid changing defensible analytical rules merely to make the dashboard appear complete.
