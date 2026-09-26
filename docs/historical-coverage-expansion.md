# Historical coverage expansion

Checked 2026-09-26. The expanded batch contains 42 WDI CPI archives (2020–2025 versions), 22 unemployment releases (March 2024–December 2025), and seven vacancy releases (March 2024–September 2025). Manifest-listed responses are hashed and replayed offline. Failed attempts remain in the acquisition log, including attempts subsequently recovered via English-language URLs; they are not automatically counts of remaining missing releases.

## CPI timing resolution

The [official WDI update history](https://datahelpdesk.worldbank.org/knowledgebase/articles/906522-data-updates-and-errata) supplies dates for 25 matching archive months. `config/wdi_release_dates.json` records these. March 2024 maps to 28 March, December 2023 to 20 December, and December 2024 to 16 December. The mapping pairs each archive YYYYMM with the documented WDI update of that month; it does not claim the earliest national CPI publication date or observation-specific first publication. That archive-to-update correspondence is an explicit evidence interpretation, retained in `availability_basis`.

Archive versions without a reviewed matching update date are saved but not admitted to the daily historical join. Null cells stay null. This gives 580 non-null vintage observations from the dated versions; repeated years across vintages are revisions, not independent measurements. The 2025 archive files currently lack reviewed dates in the map. Joins in 2025 can use sufficiently recent older dated vintages.

## Unemployment

Replayed 22 monthly releases, producing 659 non-null vintage observations. The parser checks the total-unemployment table, the five rate-column month positions, all six countries, publication date and source hashes. Source asterisks are preserved as release footnotes. No latest API value is used to fill archive gaps.

## Vacancy policy accepted by the user

B?N remains the preferred vacancy measure (`vacancies`). B?F is approved only as a separate supplementary indicator (`vacancies_bf_supplementary`), replacing the former candidate identifier. The seven releases yield 210 B?F vintage observations. B?F measures industry and construction, so its relevance to Digital, Finance and Sales is limited; it is not a role-specific measure of employee opportunities.

The feature output now contains both series for each employee, with explicit sector and analytical role. There are currently no verified historical B?N observations in this replay, so otherwise eligible records have a blank preferred value and `no_verified_historical_match`. B?F never fills that blank. Both series use the same publication-before-cutoff and freshness rules, independently. Missing external context does not remove an employee from a workforce KPI. Analyses using available external context must report their own matched sample sizes.

For example, a hire with no eligible B?N release but an eligible B?F release receives two separate records: preferred B?N unavailable, supplementary B?F matched. Any later comparison must name the sector and must not present B?F as company-wide labour demand. B?N and B?F rates are not averaged or spliced together.

The [15 March 2024 release](https://ec.europa.eu/eurostat/en/web/products-euro-indicators/w/3-15032024-ap) gives Greece Q4 2023 B–F vacancies as 2.2%; the [14 June 2024 release](https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-14062024-bp) gives 2.9% for that same quarter. Both vintages are retained. A test initially used the later value for the earlier release; inspection corrected the expected value and now tests both explicitly.

## Coverage achieved

Across all 2,400 curated employees (not the final metric denominators): unemployment matches 695, CPI 2,315, and the B–F candidate 683. Nine records lack country and ten have invalid/excluded employment. Each employee remains in the coverage output for every indicator, including unmatched records. Headline retention calculations are unchanged.

| Hiring year | Workforce records | Unemployment matches | CPI matches | B–F candidate matches |
|---|---:|---:|---:|---:|
| 2021 | 418 | 0 | 416 | 0 |
| 2022 | 397 | 0 | 396 | 0 |
| 2023 | 396 | 0 | 391 | 0 |
| 2024 | 434 | 362 | 433 | 350 |
| 2025 | 336 | 333 | 333 | 333 |

Full historical coverage is not yet achieved: unemployment and vacancy publications before 2024 require older release formats, including PDFs. A 2023 observation revised in a 2024 release cannot be attached to a 2023 hire. The requirement for about three years of external reference history is met by the current source data, but a three-year point-in-time matched analytical panel is not yet established. Do not claim otherwise.

## Reproduction and remaining work

`python scripts/build_expanded_historical_features.py` runs offline and writes canonical observations, employee features and coverage. `python -m unittest discover -s tests` runs the tests including four source-extraction tests. Acquisition is separate and network-enabled via `scripts/expand_historical_coverage.py`; it reuses hash-verified cached responses. It remains a research acquisition tool rather than a finished production connector.

Next resolve the B–F choice, recover pre-2024 unemployment/vacancy releases and test their parsers, and extend reviewed CPI release dates. Then left-join these features to the metric audits and report matched-subset sample sizes separately from full-population KPIs. No causal or predictive analysis has been performed.
