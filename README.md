# Workforce assessment - software emphasis

Submission results use conservative cleaning of the supplied CSVs: exact duplicates are removed, EL/ROM are normalized, missing countries remain unknown, and invalid employment dates are quarantined. Sr Mgmt is a flagged provisional Senior Leader mapping with sensitivity analysis. No hidden generator values enter the main metrics. See [cleaning decisions](docs/metric-and-quality-rules.md).

Generator recovery is an [optional experiment](docs/source-recovery.md), isolated under `experiments/synthetic_recovery`. Run `python scripts/clean_assessment.py --recover-synthetic` to regenerate its curated data without changing submission outputs. Earlier recovered metrics are retained there as historical comparison artifacts. The main pipeline always uses conservative cleaning.

The data-preparation pipeline replays saved workforce and external evidence, calculates the three required metrics, joins historical context, and reports coverage. The complete assessment product (including the dashboard) is still in progress.

## Setup

Requires Python 3.11+ (tested with Python 3.14). Retain `data/raw`, both historical evidence directories and their manifests, `config`, `scripts`, and `tests`.

Install the pinned PDF dependency once (network access required):

```powershell
python -m pip install --target .tools/pdf -r requirements-historical.txt
```

## One-command offline replay

From the repository root:

```powershell
python scripts/run_pipeline.py
```

To rebuild twice and verify byte-identical output files:

```powershell
python scripts/run_pipeline.py --verify-reproducibility
```

The command checks prerequisites and saved evidence hashes; validates and cleans workforce data; calculates six-month retention, senior twelve-month retention, and trailing regretted turnover; replays historical releases; builds coverage reports and metric-specific joins; builds and reconciles SQLite reporting views; and runs the test suite. Derived outputs are overwritten. No external service is contacted by the replay stages. Raw workforce files are verified against their saved manifest. The assessment HTML and Node.js are not needed.

A successful run writes `analysis/pipeline_manifest.json` with input/output SHA-256 hashes, runtime versions and repeat-verification status. A failed run exits nonzero and leaves no success marker; individual derived files may already have been written, so do not treat them as a completed run without that manifest. The workflow is not transactional. The manifest covers pipeline outputs, not legacy demonstration/probe artifacts in `analysis`.

Repeat verification establishes identical outputs in the same environment. Clean-environment and cross-platform certification remain separate checks. For stable CSV bytes, use the recorded platform/runtime; line endings can differ across platforms.

## Results and rules

- [Requirements, scope and decisions](docs/requirements-and-decisions.md)
- [Source register, contracts and attribution](docs/source-register.md)

- [Metric-specific external coverage](analysis/metric_external_coverage.md)
- [Country/year coverage and acquisition priorities](analysis/external_coverage_report.md)
- Metric results, employee audits and external joins: `analysis/new_hire_6m_*`, `analysis/senior_hire_12m_*`, `analysis/regretted_turnover_*`
- [Metric and quality rules](docs/metric-and-quality-rules.md)
- [Publication timing](docs/temporal-alignment.md)
- [Historical evidence progress and limitations](docs/historical-coverage-expansion.md)
- [HTTP download behavior](docs/http-downloads.md)

B-N vacancy rates remain preferred but lack verified historical matches; B-F is supplementary. Coverage remains partial and no causal analysis is claimed. Missing external context does not remove employees from headline KPIs. Some schema checks are audit-only; metric-specific contradiction exclusions are enforced by curation.

## Online acquisition is separate

Acquisition changes the saved evidence set and can change results. It is not part of offline replay. Existing acquisition scripts use a shared HTTP client with limited retries, timeouts and certificate-verifying curl fallback on Windows. For the configured PDF list, `python scripts/replay_historical_pdfs.py --download` downloads missing files and validates cached hashes. See the historical coverage document for other acquisition scripts and known gaps.

## Clean-workspace verification procedure

Create a fresh directory containing only `scripts`, `tests`, `sql`, `config`, `dashboard`, `data/raw`, `data/external/historical_expanded`, `data/external/historical_pdfs`, `requirements-historical.txt`. Exclude caches and both derived `canonical_observations.json` files. Do not copy `analysis`, `data/curated`, or installed dependencies.

Create a virtual environment with `python -m venv .venv`, then use `.venv\Scripts\python.exe` on Windows to install the requirements into `.tools/pdf` and run the pipeline with `--verify-reproducibility`. Compare the `outputs` mapping in the resulting manifest with the original manifest. Package installation can also use a separately downloaded wheel with `--no-index --find-links`, keeping replay independent of network access.

Verified on the current Windows host: the fresh-copy virtual-environment run passed twice, with all 60 tests and all 30 output hashes matching the original workspace. Evidence: `analysis/clean_environment_verification.json`. Cross-platform and alternate-runtime verification remain untested.

Assessment links and full visible reference text are preserved in `config/assessment_reference.json`. Collected project source URLs are in `config/source_links.json`. The assessment itself has internal navigation links only, not external URLs. Legacy extraction is retired; `analysis/assessment_profile.json` is a historical artifact, not a current pipeline output. Previous verification reports describe the earlier pipeline; rerun verification for the updated input contract.

The [SQL reporting layer](docs/sql-reporting.md) produces `analysis/reporting.sqlite` and `analysis/sql_reporting.json`. Include the `sql` directory when copying the project. Existing clean-environment verification reports predate this stage; the current pipeline repeat check includes it.

Open `analysis/dashboard.html` in a browser for the offline interactive dashboard. The pipeline rebuilds it from reconciled SQL reports. Retention filters affect cohort charts only; KPI cards and external-coverage populations stay company-wide. Include `dashboard/template.html` when copying the project. Optional UI logic check: `node dashboard/check.cjs` (Node is not required for replay). Browser visual verification remains outstanding in the current tool environment.

See the [assessment acceptance audit](docs/assessment-acceptance-checklist.md) for the requirement-by-requirement status and remaining submission work. The working dashboard is an initial implementation, not yet the complete analytical experience required by the brief.

Exploratory cohort associations are built by `scripts/analyze_associations.py` within replay. See [initial findings and limitations](docs/association-findings.md) and `analysis/association_analysis.json` for cohort points, matched/unmatched breakdowns and sensitivity results. No significance or causal claims are made.

Continuation on 2026-09-27: the dashboard includes hire-year filtering and descriptive external-signal relationship views with sample counts and sensitivity checks. See [current acceptance updates](docs/assessment-acceptance-checklist.md). The expanded Node checks pass, but Python is unavailable on this host and no browser is connected. The current preview is not certified by the older pipeline manifest; full replay and browser QA remain required.
