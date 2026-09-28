# Requirements and decisions

Submission policy and implemented scope as of 2026-09-27. This document consolidates the supplied brief, implementation decisions and unresolved questions. Business interpretations below are working assumptions, not claimed recruiter confirmations.

## Decision the product supports

Help workforce leadership identify which retention objectives need investigation, where outcomes differ across hiring cohorts and workforce segments, and whether available economic context shows descriptive patterns worth investigating. Keep data gaps and denominator choices visible so users do not confuse incomplete observations with employee failures.

The product supports prioritization of further investigation. It does not identify causes of employee departures, estimate intervention effects or predict individual employee risk. The company and employee records are fictional.

## Scope and source contract

Software emphasis: a local, reproducible Python pipeline, SQL reporting and an offline HTML dashboard. Inputs are the supplied employee lifecycle CSV, retention objectives, data dictionary and saved public economic evidence. The workforce snapshot is 2025-12-31; hiring objectives cover 2021-2025. Preserve 2020 hires for headcount and departures in the turnover window.

The workforce grain is one employment record per employee after exact duplicate removal. The supplied fields do not establish transfer or rehire histories. Six operating countries are in scope: Greece, Romania, Poland, Italy, Ireland and Bulgaria. Both permanent and fixed-term employment contribute under the stated eligibility rules.

Source objective thresholds come from [retention_objectives.csv](../data/raw/retention_objectives.csv), not dashboard constants. Raw inputs remain unchanged and are checked against their manifest. This document describes the implemented analytical scope; it does not declare the entire assessment submission complete.

## Metric definitions and boundary decisions

**Six-month new-hire retention:** among eligible hires within the objective period whose six-calendar-month anniversary is on or before the snapshot, divide employees still employed on that anniversary by all eligible mature hires. Target: at least 86%. Group by hire cohort, not departure year.

**Senior twelve-month retention:** apply the same rule at twelve calendar months to Senior Leader records, including the flagged provisional mapping of Sr Mgmt. Managers are outside this scope. Target: at least 90%. Publish a sensitivity result excluding provisionally mapped records.

**Trailing twelve-month regretted turnover:** for 2025-01-01 through 2025-12-31, count eligible Voluntary departures with regretted_exit=true and divide by average daily headcount of the same eligible population. Target: at most 7.5%. Average daily headcount is total employee-days divided by 365, not year-end headcount or the number of distinct employees seen during the year.

Calendar anniversaries clip to the last day of a shorter month. Termination date is treated as the last day employed; a departure on an anniversary counts as retained. Both choices are explicit assumptions. Immature hires are pending and excluded from retention numerators and denominators even if an early departure is already known. A zero denominator produces unavailable, not 0%.

Unknown departure classifications remain unknown. Turnover reports the confirmed rate and a scenario including potentially qualifying unknown departures. That scenario is neither a confidence interval nor a bound on the effect of excluded invalid-date records. The detailed eligibility and ambiguity rules are in [metric and quality rules](metric-and-quality-rules.md).

## Cleaning decision and consequences

The submission uses conservative cleaning of supplied values:

- Remove exact duplicate copies; fail on conflicting records sharing an employee ID.
- Normalize EL to GR and ROM to RO while preserving originals.
- Keep missing countries unknown. Otherwise-eligible employees remain in company-wide KPIs but cannot receive country-specific external matches.
- Flag Sr Mgmt to Senior Leader as provisional and report sensitivity without it.
- Quarantine missing, malformed, reversed or post-snapshot employment dates from date-based metrics. Retain the records and reasons in the audit.
- Preserve valid departures with unknown termination type or regretted status. Do not convert an unknown regretted flag to false.
- Exclude employment-status contradictions from retention and headcount; exclude regretted-type contradictions from the turnover population using the same population for numerator and denominator.

Current reconciliation: 2,407 raw rows become 2,400 unique records after seven duplicate copies are removed. Ten records have invalid employment dates, including five missing hire dates and five termination-before-hire cases. Nine country values remain unknown. There are 2,381 country-analysis-eligible records. These counts describe quality populations, not the final mature-hire denominators.

Rejected approach: restoring hidden pre-corruption values from the assessment generator. It bypasses the intended missing-data problem and is not a method available for real HR records. The source HTML, recovery code and experiment artifacts have been removed at the user's request. Only static requirements and source links remain in JSON; all workforce calculations use the supplied CSVs.

## External context and timing

Use Eurostat unemployment and vacancy evidence and World Bank annual CPI evidence to examine labour supply, labour demand and cost-of-living context. B-N vacancies remain the preferred series but have no verified historical matches in the current integrated evidence. B-F industry/construction vacancies are explicitly supplementary, not an interchangeable substitute.

For retention, select context at each employee's hire date before aggregating outcomes. For turnover, use the window start as a common country-context cutoff, including for employees hired later in the window; this is baseline context, not a prediction for a fixed baseline employee cohort.

Require the correct country and series dimensions, a non-null value, verified vintage evidence, reference-period end on or before the cutoff, and availability strictly before the cutoff. Same-day releases are excluded because intraday timing is unknown. Select the latest eligible reference period and then eligible vintage; conflicting ties are errors. Reject observations older than 120 days for unemployment, 240 days for vacancies or 730 days for CPI, measured from reference-period end. These are analytical age limits, not provider guarantees.

CPI archive availability uses reviewed WDI update-date mappings, not a claim about first national publication. Preserve frequency, period, vintage, age and evidence in lineage. Never manufacture monthly CPI measurements from annual values, borrow another country's value or drop an employee from a headline KPI merely because economic context is unavailable. See [temporal alignment](temporal-alignment.md) and [current metric coverage](../analysis/metric_external_coverage.md).

## Descriptive analysis and dashboard contract

Relationship analysis covers both retention measures, using country-by-hire-quarter cohorts for unemployment and B-F vacancies and country-by-hire-year cohorts for CPI. Cohort exposure is the mean of employee-specific eligible as-of observations. Correlations weight cohorts equally. Employee and cohort counts are not independent economic sample sizes because source observations can be reused.

Report matched/unmatched populations, small cohorts, within-country centering, minimum-ten-hire and leave-one-country-out sensitivity in the analysis artifacts. Report all preselected comparisons, including weak or unstable results. No significance tests, causal claims or predictive validation are supplied. Country centering does not resolve time trends, selection or omitted-variable confounding. Turnover relationship estimation is deferred because one annual window and six country contexts do not support a credible repeated-period analysis.

The dashboard presents company-wide KPI cards. Country, hire year, retention measure and business unit filter retention exploration; relationship views use country/year/measure and selected indicator, not business unit. Turnover remains a snapshot KPI and coverage population rather than a historical turnover trend. Tables and unavailable states accompany charts. Current outputs and caveats are in [association analysis](../analysis/association_analysis.md).

## Questions and working answers

These questions should be confirmed with a business owner before production use; no external responses are recorded here.

- Does Sr Mgmt mean Senior Leader? Provisionally yes, with an exclusion sensitivity. A confirmed mapping could change the senior denominator.
- Is termination date the last day employed? Assumed yes. A different convention changes anniversary outcomes and employee-days.
- Should fixed-term employees and pre-period hires contribute? Include both employment types and include earlier hires when they contribute turnover headcount; retention still requires hires within its objective period.
- Does regretted turnover include nonvoluntary exits? Count only explicitly voluntary regretted exits; treat conflicting classifications as quality issues and report eligible unknowns separately.
- How should missing countries or dates be corrected? Require authoritative source evidence. No country imputation or date invention is applied to submission data.
- Is a full historical turnover series necessary? The current deliverable implements the snapshot trailing window; expansion requires explicit scope and additional validation.
- Is supplementary B-F acceptable context? Keep its narrower sector visible and preserve the unavailable B-N result; it does not satisfy a claim of B-N coverage.

## Acceptance evidence and remaining work

For the implemented scope, each employee must have an auditable outcome or exclusion; counts must reconcile to the retained input grain; SQL reports must reconcile with Python metrics; temporal joins must satisfy evidence and cutoff rules; source files must retain their hashes; and repeated offline builds must produce identical outputs. The pipeline must use conservative cleaning without source HTML or generator corrections.

Current verification records 68 passing Python tests, dashboard DOM checks and 35 byte-identical output files across repeated builds. See [pipeline manifest](../analysis/pipeline_manifest.json). This is same-environment verification, not browser visual QA, cross-platform certification or a fresh installation test of the final package.

Remaining submission work includes the consolidated source register and usage terms, production architecture mapping, browser/keyboard/mobile checks, final clean-environment replay, presentation, and reviewer access. Partial-failure handling currently removes the success marker but is not transactional across all files; consumers must not treat a partial run as a complete publication. See the [acceptance checklist](assessment-acceptance-checklist.md). Human review, actual effort, recruiter answers and submission logistics must not be inferred from automated checks.

## Rejected or deferred scope

No hidden-generator repairs in submission data, automatic imputation, silent vacancy-series substitution, invented release dates, causal claims, individual-risk predictions, cloud deployment or reconstruction of unsupported rehire histories. Broader production scheduling, security and promotion are to be described in the architecture mapping, not claimed as deployed features. These cuts preserve a reproducible local implementation and make unresolved evidence visible.
