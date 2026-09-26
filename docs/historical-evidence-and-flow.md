# Historical releases and workforce integration

Retrieved 2026-09-26. This is an initial evidence batch and a partial join demonstration, not complete 2021–2025 historical coverage.

## Retrieved evidence

- Eurostat 1 March 2024 unemployment release: first table, seasonally adjusted totals, rates in percent of labour force. Six countries and five reference months (January, October, November, December 2023 and January 2024) yield 30 exact values from this release. All carry availability 2024-03-01, including older periods: do not backdate revised values to an earlier release. [Release](https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-01032024-bp).
- Eurostat 14 June 2024 vacancy release: saved as evidence, but headline scope differs from selected B-N, and the detailed table has separate B-F and G-N rates. Without occupied/vacant post weights, averaging these rates cannot reconstruct B-N. Not admitted into the strict B-N feature series. [Release](https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-14062024-bp).
- World Bank WDI archive version 202403: retrieved six countries, CPI inflation, years 2020–2023. Of 24 requested cells, 18 are non-null. Retain nulls. Version is labelled March 2024; exact daily publication is not established. It remains outside the strict daily join pending availability evidence or an explicitly documented month-end bound policy. [Archive API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/1886686-advanced-data-api-queries).

Raw files, SHA-256 hashes, source URLs and retrieval timestamps are in `data/external/historical_releases/`. The earlier `wdi_cpi_2024_02.json` is an XML error response from an invalid archive selection, not a usable dataset; it is not referenced by the successful manifest or parser. Archive website access returned 403; the official archive API supplied data. Version listing differs from the website's February 2024 label: only API-verified 202403 was used. HTTP success alone is not sufficient; JSON structure is validated.

## Current flow and insertion point

1. Existing raw workforce -> clean_assessment.py -> curated workforce and eligibility flags.
2. Existing retention calculators -> employee-level milestone outcomes and objective summaries. Keep these calculations independent of economic coverage.
3. Archived external releases -> source-specific extraction -> canonical observation records with period, country, value, fixed dimensions, exact vintage and availability evidence.
4. Build an employee feature table by calling temporal_join.select_observation for each country/indicator at hire_date. Keep one series definition per call. Missing country, missing evidence, stale values and invalid employment all remain explicit statuses.
5. LEFT JOIN employee features to each retention audit by employee_id. Preserve the full metric population; never allow missing external matches to silently alter headline retention. Summarize both matched-subset coverage and the full cohort.
6. For turnover, calculate country/window outcomes first, then select external information before each window start. The existing company-wide snapshot rate cannot simply be repeated for each country. Country-level historical outcomes still need implementation.
7. Only then group into cohorts and produce relationship views. Repeated country-period economic values do not create independent observations; retain source period and account for clustering and small sample sizes.

Example: Poland January 2024 unemployment was 2.9% in the 1 March 2024 release. A Polish hire on 15 March may receive this observation (44 days after period-end). A hire on 15 February or 1 March may not receive this vintage. A later revision must not replace the archived 2.9% value for that cutoff. Existing retention outcomes do not change.

## Executed demonstration

Run `python scripts/build_historical_join_demo.py` offline against saved evidence. It validates raw hashes, extracts the first unemployment rates table, requires six country rows and writes verified observations plus an employee feature audit. This remains a source-specific parser for this single release layout.

Across 2,400 employee records: 104 matched, 1,686 have no verified historical match in this batch, 591 have only stale evidence, nine lack country and ten have invalid/excluded employment. Counts include all curated employees, not only final objective denominators. The resulting audit is `analysis/historical_unemployment_join_demo.csv`.

## Remaining work

Expand archived unemployment releases across the chosen analysis years; obtain exact B-N vacancy archives or explicitly revise the source contract; establish CPI availability bounds/dates and expand archive vintages; verify parser layouts and release correction notices. Then implement the left joins and matched-cohort coverage reports. The present batch is not sufficient for the assessment's complete historical analytical slice.
