# SQL reporting layer

`python -m asteria.reporting.sql` builds `analysis/reporting.sqlite` using Python's standard-library SQLite module. It is also the final data stage of `python scripts/run_pipeline.py`. No database server or additional package is needed.

The schema and SQL views are in `sql/reporting.sql`. Tables store metric audit classifications, objective targets, external matches and source-file hashes. Composite primary keys prevent duplicate employee/metric/indicator rows. Missing external values are SQL NULL, not zero.

Views:

- `kpis`: numerators, denominators, rates, targets, target status and classification upper rate. For retention the upper-rate column equals the rate; uncertainty bounds apply only to turnover.
- `retention_cohorts`: country, business-unit and hire-year counts/rates for the two retention objectives, including groups with no mature observations (NULL rate).
- `quality_counts`: all audit outcome/status counts, including exclusions and pending observations; not a replacement for the detailed curation quality audit.
- `external_coverage`: match statuses within each metric population, including turnover employee-days.

SQL aggregates the existing tested employee classifications; it does not independently reimplement date-boundary classification. Every build reconciles all three KPI numerators, denominators, rates and target decisions with Python summaries. Turnover employee-days/upper rate and every external coverage status count are also reconciled. Integrity and foreign-key checks run before the temporary database replaces the final database.

`analysis/sql_reporting.json` exports the views for a future dashboard. Lineage hashes remain in the database. Pipeline reproducibility tracks both outputs and the SQL source. Byte-level SQLite reproducibility is tested on the current runtime; other SQLite versions may store equivalent data differently.

Example query:

```sql
SELECT metric, numerator, denominator, rate, target, target_status
FROM kpis ORDER BY metric;
```

External coverage remains incomplete, preferred B-N unavailable, and B-F supplementary. These views do not establish causal relationships. Country-period values repeated over employees are not independent economic observations.
