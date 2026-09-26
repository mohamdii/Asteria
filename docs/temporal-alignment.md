# Publication timing and temporal joins

Decision recorded 2026-09-26. This contract distinguishes retrospective description from information actually known at a historical decision date. No historical release dates or vintages have been fabricated.

## Source evidence

| Indicator | Documented timing | Revision implications |
|---|---|---|
| Eurostat monthly unemployment | Approximately 31 days after reference month-end | Routine and major revisions; current historical values may differ from earlier releases |
| Eurostat quarterly vacancies | Normally around 50 days for flash and 78 days for final release after quarter-end | Flash coverage is incomplete; detailed B-N country values must be verified in the actual release. Final estimates can also be revised |
| World Bank annual CPI inflation | Annual frequency; reviewed metadata does not establish an observation-specific publication date | Current API lastupdated is dataset-level, not proof of when each exact value became public |

Sources checked: [unemployment metadata, sections 14 and 17](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm), [vacancy metadata, sections 9, 14 and 17](https://ec.europa.eu/eurostat/cache/metadata/en/jvs_esms.htm), [CPI indicator metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/FP.CPI.TOTL.ZG), [World Bank update history](https://datahelpdesk.worldbank.org/knowledgebase/articles/906522-data-updates-and-errata).

Typical lags are research guidance only, not assigned publication dates. A conservative lag cannot by itself eliminate revision leakage. A current methodology page also does not establish every historical release schedule.

## Two explicit uses

1. Strict historical features (default for known-at-hiring claims): require an archived exact observation value, its vintage, publication evidence, and the date that exact value became available. Missing evidence yields no eligible match. Existing September 2026 downloads have no verified historical vintages and cannot supply 2021–2025 strict features.
2. Retrospective context: current-vintage observations may describe historical conditions in charts or explicitly retrospective associations. Label the retrieval/vintage date and revision caveat. Never describe these as forecasts, historically available features, or compliant substitutes for the assessment's no-future-information requirement. Strict integration remains unfinished until historical evidence is obtained.

## Join anchors

- Six-month and senior twelve-month retention: use each employee's hire date as the economic-feature cutoff. Join before grouping into hiring cohorts. Do not attach the whole hire-quarter average to an employee hired before that quarter ended.
- Trailing turnover: for a prospective contextual comparison use the first day of its twelve-month window as the cutoff. Period-overlapping signals belong only in a separate retrospective descriptive view. Retention is an outcome observed later; its later observation must not affect feature selection.
- Use canonical country codes (Eurostat EL maps to GR); no country borrowing or global-average replacement. Missing country yields an explicit unmatched record, not loss of the employee's valid company-wide metric.

## Exact historical selection

For a fixed country, indicator, unit, frequency, seasonal adjustment and sector:

1. Require non-null value and verified vintage with an evidence reference.
2. Require reference period end <= cutoff and available_on < cutoff. Dates only imply unknown intraday release timing, so same-day releases are conservatively excluded.
3. Choose the latest reference period; within it choose the latest eligible vintage. Conflicting ties are errors, not arbitrary first matches.
4. Reject stale values rather than carry them indefinitely. Initial project limits measured from reference-period end are 120 days (monthly unemployment), 240 days (quarterly vacancies), and 730 days (annual CPI). These are configurable analytical choices, not provider guarantees; report unmatched counts and later test sensitivity.
5. Preserve period start/end, frequency, exact source status, value, unit, country, dimensions, available_on, vintage_id, evidence URL, retrieval timestamp, and age_days. If evidence is absent, available_on remains null.

Never relabel annual CPI as monthly observations. An explicitly carried annual value remains one annual measurement, with its age and source period. Repeated country-period values across employees are not independent economic observations.

## Current limitations and next action

Coverage fixtures contain 2021–2025 reference periods but do not contain verified historical releases. Early 2021 hiring cutoffs will also need pre-2021 observations or explicit unmatched coverage. Obtain archived releases/vintages for the selected series and verify actual country/sector values before populating strict features. If vintage evidence cannot be recovered, report the failed strict coverage and keep current-vintage results explicitly retrospective; do not silently approximate compliance.

The reusable selector and tests implement the strict gate. Provider normalization, historical evidence collection and workforce integration remain next steps.
