# Synthetic source recovery

At the user's request, curation now restores values from the assessment's deterministic generator before its intentional defects are injected. This changes populations and outcomes. It is specific to this fictional dataset, not a way to infer missing real employee attributes.

`scripts/recover_synthetic_source.cjs` captures pre-defect rows, then lets the original generator finish. It requires the generated CSV to equal the supplied raw CSV byte for byte before writing corrections. Both HTML and raw CSV SHA-256 hashes are recorded in `config/synthetic_source_corrections.json`. To reproduce the evidence, retain the original assessment HTML and run `node scripts/recover_synthetic_source.cjs`. Normal Python replay uses the saved evidence without Node or HTML.

Recovery corrects 61 cells across 52 employees: 17 country codes (9 blanks and 8 overwritten alias labels), 5 hire dates, 17 termination dates, 5 termination types, 7 regretted flags and 10 career levels. Some defects added fictitious departures or replaced non-senior levels with `Sr Mgmt`; recovery removes those departures and restores the generated levels. Blank departure fields on active generated records remain blank.

Raw files remain unchanged. Curation verifies their manifest and matches each correction to its exact original value. Unknown IDs, duplicate correction keys and stale values fail the build. Every original field is retained in an `_original` column. `data/curated/source_recovery_audit.csv` contains old/new values, employee ID, source line and generator hash. Recovered rows carry `synthetic_source_recovered`, distinct from unresolved defects.

The result is 2,400 unique employees, all with known countries and valid employment dates; seven exact duplicate copies are removed. No employment-date quarantine or unresolved departure classifications remain. Conservative eligibility rules still apply to future records without verified corrections. External economic-data coverage remains partial.

Earlier numeric findings and verification reports describe the uncorrected snapshot. Use rebuilt summaries and a successful current pipeline manifest for current results.

Current outcomes: six-month retention is 1,596 / 1,822 (87.60%); senior twelve-month retention is 204 / 260 (78.46%); trailing regretted turnover is 82 / 1,625.23 average daily headcount (5.05%). The senior sensitivity retains evidence-recovered senior levels because they are no longer assumed mappings.

Replay initially caught Windows checkout line-ending conversions in 29 archived HTML files. Their bytes were restored only after LF conversion reproduced each existing manifest hash exactly. `.gitattributes` preserves archived HTML bytes and the raw CSV's required CRLF format on future checkouts. No source hashes were relaxed or rewritten to bypass validation.

Validation: all 67 Python tests passed during full offline replay; all 35 generated output hashes matched on the repeated build. Dashboard DOM checks passed. This verifies calculations and interface logic, not visual browser QA or a fresh-machine installation.
