# Source register and contracts

Reviewed 2026-09-27 against saved acquisition manifests, canonical observations, join code and official metadata/usage pages. This register documents the conservative submission pipeline. It does not refresh economic observations or certify complete historical coverage. Exact request URLs, retrieval timestamps and hashes remain in the manifests linked below.

## Scope and source roles

The supplied fictional employee snapshot, objectives and dictionary in `data/raw` define workforce outcomes. Their integrity contract is `assessment_data_manifest.json`; generator-recovered values are excluded from submission data. The assessment pack is supplied material, not a public statistical dataset with an independently verified open-data licence.

External sources cover Greece, Romania, Poland, Italy, Ireland and Bulgaria. Canonical codes are GR, RO, PL, IT, IE and BG. Normalize Eurostat EL to GR; map WDI GRC/ROU/POL/ITA/IRL/BGR to the corresponding canonical codes. Keep unknown workforce country values unmatched.

Eurostat and World Bank are two distributors, not proof of independent underlying measurements. The three economic concepts are labour supply (unemployment), labour demand (vacancies), and consumer-price pressure (CPI inflation). B-N and B-F are separate vacancy definitions, not two interchangeable measurements.

## Eurostat monthly unemployment

**Identity and dimensions:** API dataset `une_rt_m`; project indicator `unemployment`. The saved selection is monthly, total sex, total age, seasonally adjusted, unit PC_ACT. Canonical unit is `percent_labour_force`. Archived release parsers extract the corresponding total seasonally adjusted unemployment-rate table. Country-level context is not occupation-specific labour availability.

**Frequency and publication:** monthly. Metadata describes publication around 31 days after month end and subsequent revisions. This typical lag is not used to invent availability dates: the pipeline uses the date on the exact archived release containing the selected value. Current metadata does not establish every past release schedule. [Official unemployment metadata](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm).

**Evidence and limitations:** saved HTML and PDF releases supply historical vintages. Retain source footnotes and PDF page numbers where extracted. Layout, country completeness and release-date checks limit parser acceptance to reviewed formats. Missing or stale historical evidence remains unmatched; a later revision never acquires an earlier availability date. Project maximum age is 120 days from reference-period end. Earlier-year release coverage remains incomplete.

**Fitness:** broad labour-market context for retention cohorts. National aggregation, revision effects and reused observations limit interpretation; it does not identify why an employee left. Reuse conditions are in the Eurostat section below.

## Eurostat quarterly vacancies: preferred B-N

**Identity and dimensions:** saved API dataset `jvs_q_nace2`, rate JVR, NACE B-N, total enterprise size, not seasonally adjusted; project indicator `vacancies`. Canonical unit is `percent_posts`, frequency Q and sector B-N. The vacancy rate measures vacant posts relative to occupied plus vacant posts. Eurostat describes flash and final dissemination around 50 and 78 days after quarter end, respectively. Exact release evidence, not typical lag, determines project availability. [Official vacancy metadata](https://ec.europa.eu/eurostat/cache/metadata/en/jvs_esms.htm).

**Fitness and gap:** preferred business-economy labour-demand context. The saved current-vintage API probe contains 2021-2025 values, but the integrated historical replay has no verified B-N matches. The main join retains explicit unavailable results. Common sector selection does not remove country-method differences or seasonality. The saved dataset identifier is a historical contract; future acquisition must verify any successor rather than assume continuity.

## Eurostat quarterly vacancies: supplementary B-F

**Identity and dimensions:** project indicator `vacancies_bf_supplementary`, frequency Q, canonical unit `percent_posts`, sector B-F, not seasonally adjusted. Values come from the explicitly labelled industry-and-construction tables in saved Eurostat HTML/PDF releases. They are not relabelled B-N API observations.

**Evidence and fitness:** retain each release's publication date and revised values separately. The parser checks table sector, periods, countries and rate units. Maximum age is 240 days from reference-period end for both vacancy series. B-F is narrower context with limited relevance to Digital, Finance or Sales; it is not a measure of vacancies for those employees' roles. It is supplementary only and never fills a missing B-N value. Eurostat reuse conditions apply to both series.

## World Bank consumer-price inflation

**Identity:** WDI indicator `FP.CPI.TOTL.ZG`; project indicator `inflation`. Canonical frequency A and unit `percent_annual_change`. This is annual consumer-price inflation, not a CPI index level or Eurostat HICP. Current indicator metadata identifies IMF International Financial Statistics as the underlying source and lists CC BY-4.0. [Indicator definition, origin and licence](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/FP.CPI.TOTL.ZG).

**Acquisition and timing:** saved historical requests use World Bank API source 57 and YYYYMM archive versions, with exact URLs in the expanded manifest. Reference years and archive versions are distinct dimensions. The project admits only archive months with reviewed WDI update dates in `config/wdi_release_dates.json`, based on the [official update history](https://datahelpdesk.worldbank.org/knowledgebase/articles/906522-data-updates-and-errata). This archive-month correspondence is an explicit interpretation, not an observation-specific first national publication date. Unmapped versions and null values cannot enter strict joins. No fixed publication lag is invented.

**Fitness and limitations:** annual living-cost context, not employee-specific spending or wage pressure. Revisions are retained as vintages. Project age limit is 730 days from reference-year end. Annual values remain annual even when reused for several hiring dates; they must not be presented as independent monthly measurements.

## Usage terms and attribution

**Eurostat:** statistical data and publications may generally be reused with source acknowledgement, subject to individual notices and stated exceptions. Third-party materials and standalone logos have separate restrictions. Modified data/text must be identified and accompanied by a disclaimer that Eurostat is not responsible. The selected statistical countries are EU members, but full archived releases can include additional countries and material; do not treat this register as blanket clearance for commercial redistribution of entire publications. [Eurostat copyright and reuse notice](https://ec.europa.eu/eurostat/help/copyright-notice), checked 2026-09-27.

Project attribution: “Source: Eurostat, unemployment and job-vacancy releases; exact release URLs and access dates are recorded in the source manifests. Values were extracted, normalized and aggregated for this assessment. Eurostat is not responsible for these transformations or conclusions.” Preserve publication notices in saved documents; provider branding is not project branding.

**World Bank:** the CPI indicator's own licence label supports CC BY-4.0 attribution, rather than relying only on a generic open-data assumption. The Bank's licensing page describes attribution and identification of changes, and additional licence terms; other datasets can have different licences. [World Bank data licensing](https://datacatalog.worldbank.org/public-licenses), checked 2026-09-27.

Project attribution: “Source: World Bank, World Development Indicators, FP.CPI.TOTL.ZG; underlying source: IMF International Financial Statistics. CC BY 4.0. Archive selection, normalization and cohort aggregation by the assessment author; exact requests and retrieval dates are in the source manifests.” Retain the indicator and licence links when sharing derived results. Do not imply provider endorsement.

## Lineage and replay contract

The following files serve distinct purposes:

- [Current-vintage probe provenance](../data/external/coverage_probe/provenance.json): API availability checks; these payloads alone do not establish historical knowability.
- [Expanded-release manifest](../data/external/historical_expanded/manifest.json): saved HTML/CPI response filenames, exact URLs, retrieval timestamps and SHA-256 hashes.
- [PDF manifest](../data/external/historical_pdfs/manifest.json): PDF filenames, URLs, reported release dates, retrieval timestamps and hashes.
- [Combined canonical observations](../data/external/historical_expanded/canonical_observations.json): normalized periods, countries, series, units, values, available_on, vintage IDs and evidence references; PDF observations also retain source page.
- `analysis/*_external_lineage.json`: employee/cutoff selection decisions and selected observation evidence; joined CSVs expose matching fields alongside the original employee audit.

To retrieve an observation's download timestamp, match `source_file` and `source_sha256` to the appropriate manifest entry, then read `retrieved_at` and `url`. The timestamp describes collection, not publication. A mismatch is a provenance error, not permission to substitute a similarly named file.

The analytical observation identity includes country, indicator, frequency, unit, adjustment/sector, reference period and vintage. Provider adapters fix dimensions before selection; the temporal selector assumes that fixed-series contract rather than independently validating every dimension. It rejects ambiguous best matches. New adapters must preserve that invariant.

Strict selection requires a verified non-null value with vintage, availability and evidence; reference-period end must be on/before cutoff and availability strictly before cutoff. Select latest eligible period, then latest eligible vintage; reject stale values. Hire date anchors retention context; window start anchors turnover context. Original workforce outcomes survive the left join. Missing context does not remove employees from headline KPIs. See [temporal rules](temporal-alignment.md).

Offline replay verifies saved evidence hashes. Online acquisition is a separate operation using the [shared HTTP behavior](http-downloads.md). Parser failures stop the affected build; acquisition failures must not become fabricated zeroes. Acquisition remains research-oriented and is not claimed as a fully scheduled production connector.

## Coverage and remaining limitations

The current-vintage probe found complete 2021-2025 reference-period values for all six countries in the three selected API series. This does not imply complete point-in-time joins.

For the current conservative six-month population of 1,813 mature hires, matches are 1,092 unemployment, 1,808 CPI, zero B-N and 1,408 supplementary B-F. For 266 mature senior hires they are 150, 266, zero and 211. Among 1,868 employees contributing positive turnover-window days they are 1,861, 1,861, zero and 1,861. The turnover KPI denominator remains average daily headcount, not 1,868. These are employee match counts, not independent economic sample sizes. [Generated metric coverage](../analysis/metric_external_coverage.md) is authoritative after each rebuild.

Priorities remain preferred B-N historical evidence, missing earlier/intervening unemployment and vacancy releases, and review of additional CPI archive availability dates. Do not relax vintage gates merely to improve coverage. Current provider metadata is not a retroactive guarantee of historical schedules, and successful parsing is not a claim of causal validity or complete visual inspection of every source PDF.
