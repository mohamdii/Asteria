# External coverage check

Checked 2026-09-26 against official APIs. See `analysis/external_coverage.csv` for country-level counts and `data/external/coverage_probe/provenance.json` for exact URLs, UTC retrieval times and SHA-256 checksums. Saved JSON payloads preserve source values and flags.

## Verified availability, 2021–2025

All six countries (GR, RO, PL, IT, IE, BG) have complete non-null coverage for each selected series:

| Provider | Indicator and selection | Native frequency | Per country | Total |
|---|---|---|---:|---:|
| Eurostat | une_rt_m: total age, total sex, seasonally adjusted, PC_ACT (% labour force) | Monthly | 60/60 | 360 |
| Eurostat | jvs_q_nace2: JVR, B-N business economy, TOTAL size, NSA | Quarterly | 20/20 | 120 |
| World Bank WDI | FP.CPI.TOTL.ZG, consumer-price inflation (% annual) | Annual | 5/5 | 30 |

This meets the numerical minimum of three indicators, two providers, and at least three years. The lenses are labour supply, labour demand and living-cost pressure. World Bank is the distributor of the CPI series, with underlying IMF/national sources; provider count does not mean independent underlying measurements.

## Definitions and source evidence

- [Eurostat unemployment metadata](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm): monthly unemployment series. API uses age=TOTAL, not Y15-74. Preserve seasonal adjustment and source status flags.
- [Eurostat vacancy metadata](https://ec.europa.eu/eurostat/cache/metadata/en/jvs_esms.htm): vacancy rate = vacant posts / (occupied + vacant posts). Business economy B-N was selected to avoid the headline public-sector coverage difference noted for Italy. Countries can use different reference-date practices; common sector coverage does not eliminate all comparability differences. NSA series can be seasonal. The downloaded dataset is labelled 2001–2025; later refreshes require checking successor datasets rather than assuming it extends.
- [World Bank CPI metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/FP.CPI.TOTL.ZG): annual consumer-price inflation, not Eurostat HICP. Do not silently substitute or splice those concepts.
- [Eurostat reuse terms](https://ec.europa.eu/eurostat/help/copyright-notice) and [World Bank licensing](https://datacatalog.worldbank.org/public-licenses): retain attribution and check applicable third-party conditions when packaging data.

## Availability is not historical knowability

These are current API vintages retrieved in September 2026. Non-null 2025 values do not prove that they were published by 2025-12-31, or available when an employee was hired. Dataset update timestamps are not observation release dates. Revisions may incorporate later information. Do not claim point-in-time-safe joins from these payloads alone.

Next establish release-date/vintage evidence or explicitly limited, documented lag assumptions. A lag alone cannot remove revision leakage. No numerical publication lag has been assumed by this probe. Preserve reference period, original frequency, release/availability evidence, retrieval time, age and flags during ingestion. Never join full-year inflation to earlier dates in the same year as if already known.

## Recommended use

Proceed with these candidates, subject to temporal-contract validation. Quarterly labour-market comparisons can use quarterly vacancies and explicitly aggregated monthly unemployment. Inflation stays annual; use annual analysis or clearly identified lagged annual context, not fabricated monthly observations. The five-year annual panel has only 30 country-year cells before workforce exclusions, so avoid treating repeated quarterly copies as extra independent evidence. Senior cohorts need sample-size review before country-quarter analysis.

This is a coverage probe, not production ingestion. Replay, retries, atomic outputs, partial-failure diagnostics, normalized status flags and robust provider adapters remain implementation work. Python certificate verification failed for Eurostat locally; the probe uses Windows curl with certificate verification enabled as a fallback. Initially incorrect dataset/indicator selections were corrected from live API metadata; empty dimensions now fail explicitly.
