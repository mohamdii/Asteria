---
marp: true
size: 16:9
paginate: true
---

# ASTERIA

Workforce

retention

Results and evidence

31 December 2025 snapshot

Synthetic workforce data

<!-- 0:00-0:45. Sources: docs/requirements-and-decisions.md -->

---

# Senior retention falls below target

87.15%

78.57%

86.00%

90.00%

0.00% 20.00% 40.00% 60.00% 80.00% 100.00%

Six-month retention

Senior twelve-month

Target Observed

11.43

percentage points

below the senior 

target

Regretted turnover: 5.10% against a 7.50% ceiling

<!-- 0:45-2:00. Sources: analysis/new_hire_6m_summary.json; analysis/senior_hire_12m_summary.json; analysis/regretted_turnover_summary.json -->

---

# Cleaning preserves uncertainty

2,407

supplied rows

2,400

unique records after 7 exact duplicates

8 country aliases standardized

9 missing countries remain unknown

10 invalid-date records quarantined

Raw data stays unchanged. Every exclusion remains auditable.

<!-- 2:00-3:15. Sources: data/curated/quality_summary.json; docs/requirements-and-decisions.md -->

---

# Retention starts with eligible cohorts

6 months

1,580 / 1,813

87.15% retained

12 months, senior

209 / 266

78.57% retained

Only hires who reach the milestone by the snapshot enter the denominator.

Hiring period: 2021-2025. Termination on the anniversary counts as retained.

<!-- 3:15-4:30. Sources: analysis/new_hire_6m_summary.json; analysis/senior_hire_12m_summary.json; docs/requirements-and-decisions.md -->

---

# Turnover stays below its ceiling

5.10%

5.23%

7.50%

0.00% 1.00% 2.00% 3.00% 4.00% 5.00% 6.00% 7.00% 8.00% 9.00% 10.00%

Confirmed exits

Including unknowns

Ceiling

82 exits / 1,607.52 average daily headcount

The upper scenario adds 2 potentially regretted exits. It is not a confidence interval.

<!-- 4:30-5:45. Sources: analysis/regretted_turnover_summary.json -->

---

# When a cohort is too recent

Senior retention, Hire year 2025

Unavailable

0 mature hires

The dashboard keeps pending hires outside the denominator.

Company-wide KPI cards remain fixed while cohort filters change.

<!-- 5:45-7:00. Sources: dashboard/template.html; docs/dashboard-browser-qa.md; analysis/senior_hire_12m_summary.json -->

---

# Historical context has a time boundary

Published before the cutoff

Reference period ends by the cutoff

Maximum source age

120 days

Unemployment

240 days

Vacancy rate

730 days

Annual CPI

Retention cutoff: hire date. Turnover cutoff: start of the annual window.

<!-- 7:00-8:00. Sources: docs/historical-evidence-and-flow.md; docs/requirements-and-decisions.md -->

---

# Coverage changes with the indicator

60.2%

99.7%

77.7%

0.0% 10.0% 20.0% 30.0% 40.0% 50.0% 60.0% 70.0% 80.0% 90.0% 100.0%

Unemployment

Annual CPI inflation

Vacancies, B-F

1,813 mature hires in the six-month population

B-F covers industry and construction. Missing evidence does not remove KPI records.

<!-- 8:00-9:15. Sources: analysis/metric_external_coverage.md -->

---

# Weak associations limit interpretation

-0.123

0.162

-0.009

-1.000 -0.800 -0.600 -0.400 -0.200 0.000 0.200 0.400 0.600 0.800 1.000

Unemployment

Annual CPI inflation

Vacancies, B-F

Six-month retention in synthetic matched cohorts

Small cohorts, reused vintages and selection prevent causal conclusions.

<!-- 9:15-10:15. Sources: analysis/association_analysis.md -->

---

# The working solution uses Python and HTML

01 Python Cleaning, metrics and temporal joins

02 SQLite Reconciled reporting views

03 HTML Interactive dashboard and audit context

One entry point: scripts/run_pipeline.py. Saved evidence supports offline replay.

<!-- 10:15-11:15. Sources: docs/code-structure.md; analysis/pipeline_manifest.json; docs/dashboard-browser-qa.md -->

---

# Proposed production

architecture

Azure Data Factory

Schedules acquisition and processing

ADLS and Databricks

Preserve evidence and build validated Delta tables

Approved release, SQL and Power BI

Publish only a consistent, validated run

Future design only. No cloud deployment.

<!-- 11:15-12:30. Sources: docs/production-architecture.md -->

---

# AI assistance and human accountability

Human direction

Set scope, challenged cleaning, approved changes,

and reported browser checks.

Codex implementation

Built code, tests, documentation and presentation.

Source evidence and repeat runs checked the outputs.

A rejected approach

Removed hidden-generator recovery. Missing countries

remain unknown in the submitted analysis.

Known limits: no causal claims or deployed cloud system.

<!-- 12:30-14:00. Sources: AI_USAGE.md; docs/dashboard-browser-qa.md; tests/test_publication.py -->

---

# What the evidence supports

Senior retention is the priority

Investigate internal drivers of the shortfall

Resolve missing countries and unknown classifications

Expand historical evidence before stronger economic claims

Questions

<!-- 14:00-15:00. Sources: docs/requirements-and-decisions.md; analysis/association_analysis.md -->
