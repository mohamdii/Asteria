# Metric and quality decisions

**Submission policy:** the rules below operate directly on supplied CSVs. Hidden generator values are excluded from submission metrics. [Synthetic recovery](source-recovery.md) is an isolated optional experiment. Current results are in `analysis/*_summary.json`; original values and source lines remain in curated records.

Status: curation and all three snapshot objective calculations implemented under the conventions below. Software emphasis. Historical turnover trends and external integration remain future work.

## Scope and provenance

The source snapshot is 2025-12-31. Reporting covers 2021–2025. Preserve 2020 hires because they can contribute headcount and departures in later reporting periods. Raw files remain unchanged and are verified against the supplied manifest before each run. The observed grain is one employment record per employee, plus exact duplicate copies. Rehires and transfers cannot be reconstructed from these fields.

## Cleaning rules

- Remove only exact duplicate copies, preserving a source-line audit. Fail on conflicting records sharing an employee ID rather than arbitrarily selecting one.
- Map EL to GR and ROM to RO. Preserve original country codes.
- Preserve missing countries. Otherwise-valid records can enter company-wide metrics, but not country comparisons or external country joins.
- Provisionally map Sr Mgmt to Senior Leader, preserve the original label, and flag the assumption. Managers are not senior hires under this convention. Later senior results should include a sensitivity check excluding the assumed mappings.
- Missing, malformed, reversed, or post-snapshot employment dates prevent reliable employment reconstruction. Retain records in the curated file with eligibility false and copy them to a quarantine file. Do not invent dates.
- Missing termination type does not erase a valid departure. Retention uses departure dates regardless of type.
- Blank regretted flags on terminated records mean unknown. On records without a termination date they are treated as not applicable. Preserve original values.
- Curated data contains all unique employees, including quarantined records. Downstream calculations must use eligibility flags. Quality flag counts can overlap.

## Metric conventions for the next calculation stage

Use calendar-month anniversaries, clipping to the last day of a shorter destination month. Termination date means last day employed. An employee is employed on day d when hire_date <= d and termination_date is blank or >= d. Consequently, departure on an anniversary still counts as retained on that date. This boundary is a documented assumption, not a supplied business definition.

Six-month retention: among date-valid hires within the selected hiring cohort and target effective period whose six-month anniversary is on or before the snapshot, divide employees still employed on that anniversary by all eligible hires. Exclude all immature hires from both numerator and denominator, even if an early departure is already known, and report their count separately.

Senior twelve-month retention: the same rule at twelve months, restricted to Senior Leader after the provisional mapping. Group these retention measures by hiring cohort rather than departure quarter.

Trailing twelve-month regretted turnover: for reporting date T, use the calendar window (T minus twelve calendar months, T], inclusive of its first following day and T. Count date-valid departures with termination_type=Voluntary and regretted_exit=true within the window. Divide by daily average headcount for the same population and window. Include permanent and fixed-term staff. Do not filter headcount to people with known departure classifications.

Unknown departure classifications are not zero regretted exits. Report confirmed numerator, ambiguous departures, and a sensitivity range treating potentially qualifying unknown departures as regretted. Contradictory explicit classifications require review. Label the confirmed rate as potentially understated when ambiguity remains.

Daily average headcount: total employee-days in the window divided by its actual calendar-day count (including leap days). Clip each valid employment interval to the window. Report missing/invalid-date exclusions because headcount may be understated. A zero denominator produces an unavailable rate, not zero.

Use the objective CSV for thresholds: >=0.86, >=0.90, <=0.075. Retain counts alongside rates. No causal inference from this synthetic workforce dataset.

## Acceptance criteria

The separate schema audit (`python scripts/validate_assessment.py`) checks every dictionary-required field, strict ISO dates, finite decimal targets in [0,1], effective_from <= effective_to (same-day windows allowed), selected categorical domains and departure contradictions. It recognizes EL, ROM and Sr Mgmt as documented aliases; curation still flags their mappings. Free-text fields have no invented controlled vocabulary. The audit reports violations. Curation now enforces the user-approved contradiction exclusions below; other schema violations remain audit-only.

## Approved contradiction policy

Flag contradictory employee records and exclude them from affected metrics while continuing with unaffected records. Preserve the source record and audit the reason.

- A true regretted flag or populated termination type without a termination date makes employment status uncertain. Set retention_eligible, headcount_eligible, and regretted_turnover_eligible to false. Exclude from retention numerators and denominators, headcount, and regretted turnover.
- A true regretted flag with Involuntary or End of Contract is a conflict under the proposed voluntary-only numerator. With valid dates, retain the record for retention and general headcount but set regretted_turnover_eligible=false. When turnover is implemented, use this same restricted population for both its numerator and average-headcount denominator and report exclusions.
- Keep unknown classifications separate from contradictions. Unknown values remain available for the planned turnover sensitivity analysis; eligibility does not mean a confirmed regretted exit.
- Invalid employment dates continue to block all date-based metrics. valid_employment_dates alone does not imply metric eligibility. Maturity flags describe observation length only.
- Both retention calculators enforce retention_eligible and report excluded_contradiction separately. Turnover enforces regretted_turnover_eligible for both numerator and denominator.

On the supplied raw files, the audit found five termination-before-hire records, already excluded by curation, and no other violations of these checks. Nullable missing hire dates are still metric exclusions despite passing dictionary nullability. This audit is not a claim of complete semantic correctness.

- Supplied hashes, sizes, and row counts verify before curation.
- Every input row reconciles to one curated employee or an audited duplicate copy.
- Original mapped labels and source CSV lines remain available.
- Invalid employment dates never receive eligibility true.
- Unknown country prevents country eligibility without preventing otherwise-valid company-wide use.
- Unknown regretted classification is never converted to false.
- Calendar-anniversary maturity is tested at month ends and the snapshot boundary.
- Same inputs produce byte-identical outputs on rerun.
- Raw file hashes remain unchanged.

## Next stage

Six-month outputs include an exclusive status for every unique employee and annual hiring-cohort summaries. Invalid-date exclusions take precedence over hire-period classification; records missing hire dates cannot be assigned to the reporting period. Pending cohorts are excluded even when an early departure is already known. Annual results for 2025 are partial mature-cohort results, not full-year estimates.

Senior retention now has employee and annual cohort outputs plus sensitivity excluding the assumed Sr Mgmt mappings. The main result is 209/266 (78.57%); excluding mapped records gives 203/259 (78.38%). Both are below the 90% target. All 49 senior hires from 2025 are pending, not failures. Two senior records have missing hire dates; 63 senior records were hired before the objective period. No additional career-level metrics were added.

Snapshot turnover is now implemented for 2025-01-01 through 2025-12-31. There are 586,744 employee-days over 365 days, giving average headcount 1,607.5178. The confirmed numerator is 82 (5.1010%). Two potentially qualifying unknown departures raise the scenario numerator to 84 (5.2254%). Both scenarios meet the 7.5% target. Ten invalid-date records are excluded, and their impact is not bounded by this classification-only range.

Potentially qualifying unknown departures have termination_type blank or Voluntary and regretted_exit blank or true, excluding confirmed Voluntary/true cases. Explicit false or nonvoluntary cases are outside this scenario numerator. This is a deterministic sensitivity range, not a statistical confidence interval. Employee-level days reconcile to independently accumulated daily counts. Zero average headcount produces unavailable rates.

Next examine cohort sizes before choosing quarterly reporting and external data coverage. Historical turnover trends, external integration, packaging, and a dashboard remain future work.
