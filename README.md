# Workforce assessment exploration

Expanded historical evidence can be replayed offline with `python scripts/build_expanded_historical_features.py`. See [coverage and limitations](docs/historical-coverage-expansion.md). It produces `analysis/expanded_historical_features.csv` and yearly match coverage; B–F vacancies remain a separate candidate, not a replacement for B–N. Pre-2024 unemployment/vacancy release coverage remains incomplete.

Publication timing and joining rules are documented in [temporal alignment](docs/temporal-alignment.md). The strict selector in `scripts/temporal_join.py` rejects unverified vintages and future releases. Current API fixtures are retrospective data, not verified historical features. Historical evidence collection and integration remain unfinished.

Initial extraction, profiling, and curation of the supplied synthetic assessment data. This is the data preparation stage, not the completed assessment product.

Requires Python 3.11+ with no additional packages. From the repository root:

```powershell
python scripts/clean_assessment.py
python scripts/validate_assessment.py
python scripts/calculate_retention.py
python scripts/calculate_senior_retention.py
python scripts/calculate_regretted_turnover.py
python -m unittest discover -s tests -v
```

The cleaning command verifies raw inputs, applies documented rules, and overwrites derived files deterministically in `data/curated/`. Raw inputs remain unchanged. It produces all unique records with eligibility flags, an employment-date quarantine, a row-level quality audit, and a JSON summary. Do not use every curated row indiscriminately for metrics.

Read [metric and quality rules](docs/metric-and-quality-rules.md) before using the outputs. Each metric command rebuilds curation. Six-month results are in `analysis/new_hire_6m_*`; senior twelve-month results, annual cohort counts, employee decisions, and mapping sensitivity are in `analysis/senior_hire_12m_*`. Snapshot trailing-twelve-month turnover, employee-day decisions, daily headcounts, and classification sensitivity are in `analysis/regretted_turnover_*`. Historical turnover trends, external data, SQL transformations, and a dashboard remain future work. The selected assessment track is Software emphasis.

The original pack extraction and exploration can be repeated with Node.js using `node scripts/explore-assessment.cjs`. It refuses to overwrite differing raw data.

The validation command audits dictionary nullability and types, selected pack-specific categories, date ordering, target ranges, and departure contradictions. Results are in `analysis/schema_validation.json`. The audit itself reports findings. Curation enforces departure-contradiction exclusions through retention_eligible, headcount_eligible, and regretted_turnover_eligible; six-month retention consumes its eligibility flag. Other schema checks are not yet pipeline gates. See the documented policy for metric-specific treatment.

External acquisition scripts share a bounded HTTP download client with retries, Retry-After handling and certificate-verifying Windows curl fallback. See [download behavior and limitations](docs/http-downloads.md).
