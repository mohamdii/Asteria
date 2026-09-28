# Workforce assessment - software emphasis

Submission results use conservative cleaning of the supplied CSVs: exact duplicates are removed, EL/ROM are normalized, missing countries remain unknown, and invalid employment dates are quarantined. Sr Mgmt is a flagged provisional Senior Leader mapping with sensitivity analysis. No hidden generator values enter the main metrics. See [cleaning decisions](docs/metric-and-quality-rules.md).

The original assessment HTML, generator recovery code and recovery artifacts have been removed. Requirements are preserved as static reference text in `config/assessment_reference.json`; external source URLs are in `config/source_links.json`. Neither executes source HTML. The pipeline processes supplied CSVs and saved external evidence only.

The data-preparation pipeline replays saved workforce and external evidence, calculates the three required metrics, joins historical context, and reports coverage. The analytical product and dashboard are implemented. Submission status and remaining logistics are recorded in docs/submission-review-2026-09-28.md.

## Setup

Requires Python 3.11+ (latest verification: Python 3.12.14). Retain `asteria`, `scripts`, `tests`, `sql`, `dashboard`, `config`, `data/raw`, and both historical evidence directories with their manifests.

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

The command checks prerequisites and saved evidence hashes; validates and cleans workforce data; calculates six-month retention, senior twelve-month retention, and trailing regretted turnover; replays historical releases; builds coverage reports and metric-specific joins; builds and reconciles SQLite reporting views; and runs the test suite. Each run builds in a new isolated release folder. Existing published outputs are never overwritten. No external service is contacted by the replay stages. Raw workforce files are verified against their saved manifest. The assessment HTML and Node.js are not needed.

A successful run validates the release manifest and every output hash, then atomically replaces `releases/current.json`. This pointer identifies the complete current release. Failed or interrupted builds leave the previous pointer and release unchanged. Unpublished staging folders remain for diagnosis. Concurrent successful runs publish in completion order. This protects against process interruption, not storage-device failure.

The command prints the current dashboard path. To find it later in PowerShell:

```powershell
$releaseId = (Get-Content releases/current.json -Raw | ConvertFrom-Json).release
Join-Path (Get-Location) "releases/$releaseId/analysis/dashboard.html"
```

Read the pointer once and use that release folder for all reports and its `analysis/pipeline_manifest.json`. Existing top-level `analysis/` and `data/curated/` files are legacy snapshots and no longer refreshed by the pipeline. Direct module execution is a development operation and bypasses publication. Keep the current and any in-use older release folders. `releases/` is ignored by Git; include a complete successful release when packaging generated results for handoff.

Node, when installed, runs the dashboard DOM checks before publication. Without Node the pipeline prints an explicit skipped-check notice. Python tests and output validation always run.

Repeat verification establishes identical outputs in the same environment. Clean-environment and cross-platform certification remain separate checks. For stable CSV bytes, use the recorded platform/runtime; line endings can differ across platforms.

## Results and rules

- [Code structure and commands](docs/code-structure.md)

- [Requirements, scope and decisions](docs/requirements-and-decisions.md)
- [Source register, contracts and attribution](docs/source-register.md)
- [Production architecture mapping](docs/production-architecture.md)

- [Metric-specific external coverage](analysis/metric_external_coverage.md)
- [Country/year coverage and acquisition priorities](analysis/external_coverage_report.md)
- Metric results, employee audits and external joins: `analysis/new_hire_6m_*`, `analysis/senior_hire_12m_*`, `analysis/regretted_turnover_*`
- [Metric and quality rules](docs/metric-and-quality-rules.md)
- [Publication timing](docs/temporal-alignment.md)
- [Historical evidence progress and limitations](docs/historical-coverage-expansion.md)
- [HTTP download behavior](docs/http-downloads.md)

B-N vacancy rates remain preferred but lack verified historical matches; B-F is supplementary. Coverage remains partial and no causal analysis is claimed. Missing external context does not remove employees from headline KPIs. Some schema checks are audit-only; metric-specific contradiction exclusions are enforced by curation.

## Online acquisition is separate

Acquisition changes the saved evidence set and can change results. It is not part of offline replay. Existing acquisition scripts use a shared HTTP client with limited retries, timeouts and certificate-verifying curl fallback on Windows. For the configured PDF list, `python -m asteria.acquisition.pdfs` downloads missing files and validates cached hashes. See the historical coverage document for other acquisition scripts and known gaps.

## Clean-workspace verification procedure

Create a fresh directory containing only `scripts`, `asteria`, `tests`, `sql`, `config`, `dashboard`, `data/raw`, `data/external/historical_expanded`, `data/external/historical_pdfs`, `requirements-historical.txt`. Exclude caches and both derived `canonical_observations.json` files. Do not copy `analysis`, `data/curated`, or installed dependencies.

Create a virtual environment with `python -m venv .venv`, then use `.venv\Scripts\python.exe` on Windows to install the requirements into `.tools/pdf` and run the pipeline with `--verify-reproducibility`. Compare the `outputs` mapping in the resulting manifest with the original manifest. Package installation can also use a separately downloaded wheel with `--no-index --find-links`, keeping replay independent of network access.

Historical fresh-copy evidence in `analysis/clean_environment_verification.json` predates the final dashboard and publication workflow. The latest isolated release build passed repeated-output verification for 34 files using the existing dependency installation. A fresh dependency installation of the final version remains recommended. Cross-platform verification is not claimed.

Assessment links and full visible reference text are preserved in `config/assessment_reference.json`. Collected project source URLs are in `config/source_links.json`. The assessment itself has internal navigation links only, not external URLs. Legacy extraction is retired; `analysis/assessment_profile.json` is a historical artifact, not a current pipeline output. Previous verification reports describe the earlier pipeline; rerun verification for the updated input contract.

The [SQL reporting layer](docs/sql-reporting.md) produces `analysis/reporting.sqlite` and `analysis/sql_reporting.json`. Include the `sql` directory when copying the project. Existing clean-environment verification reports predate this stage; the current pipeline repeat check includes it.

Open the dashboard path printed by the pipeline for the offline interactive dashboard. The pipeline rebuilds it from reconciled SQL reports. Retention filters affect cohort charts only; KPI cards and external-coverage populations stay company-wide. Include `dashboard/template.html` when copying the project. Optional UI logic check: `node dashboard/check.cjs` (Node is not required for replay). Desktop screenshots and user-reported mobile, keyboard, hover and error-state checks are recorded in `docs/dashboard-browser-qa.md`. Agent-operated browser verification was blocked by URL policy.

See the [assessment acceptance audit](docs/assessment-acceptance-checklist.md) for the requirement-by-requirement status and remaining submission work. The dashboard includes the required filters, selected economic context, relationship views, coverage and methodology.

Exploratory cohort associations are built by `asteria/reporting/associations.py` within replay. See [initial findings and limitations](docs/association-findings.md) and `analysis/association_analysis.json` for cohort points, matched/unmatched breakdowns and sensitivity results. No significance or causal claims are made.

## Presentation and handoff

Use [the submission PDF](presentation/workforce-retention-submission.pdf), [Markdown deck](presentation/workforce-retention.md), and [timed speaker notes](presentation/speaker-notes.md). The 13-slide presentation totals 15 minutes and includes AI accountability. The earlier PDF is retained as a source copy.

The latest successful release is selected by `releases/current.json`; use its dashboard, reports and manifest together. The candidate reports approximately 15 hours of effort. Final handoff still needs confirmed reviewer access/deadline. See [current review](docs/submission-review-2026-09-28.md).
