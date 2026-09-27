# Synthetic source recovery: optional experiment only

Submission curation uses conservative cleaning of the supplied CSVs. It does not load generator corrections. Missing countries remain unknown, invalid dates are quarantined, and provisional mappings are flagged. The earlier recovery bypassed the assessment's data-quality challenge by using hidden generator values, so it is retained only as an optional experiment.

Run `python scripts/clean_assessment.py --recover-synthetic` to regenerate experiment curation in `experiments/synthetic_recovery/curated`. This never overwrites `data/curated` or `analysis`, and does not recalculate experiment KPIs. The main pipeline always rebuilds conservative submission results.

`experiments/synthetic_recovery/previous_run` preserves the earlier recovered outputs and historical manifest for comparison. They are not certified by the current submission pipeline. Do not mix them with submission outputs. The account below describes that experiment, not current submission cleaning.

`scripts/recover_synthetic_source.cjs` captures pre-defect rows, then lets the original generator finish. It requires the generated CSV to equal the supplied raw CSV byte for byte before writing corrections. Both HTML and raw CSV SHA-256 hashes are recorded in `config/synthetic_source_corrections.json`. To reproduce the evidence, retain the original assessment HTML and run `node scripts/recover_synthetic_source.cjs`. Only the optional experiment uses this evidence; normal curation does not need it.

Recovery corrects 61 cells across 52 employees: 17 country codes (9 blanks and 8 overwritten alias labels), 5 hire dates, 17 termination dates, 5 termination types, 7 regretted flags and 10 career levels. Some defects added fictitious departures or replaced non-senior levels with `Sr Mgmt`; recovery removes those departures and restores the generated levels. Blank departure fields on active generated records remain blank.

Raw files remain unchanged. Experiment curation verifies their manifest and matches each correction to its exact original value. Unknown IDs, duplicate correction keys and stale values fail the build. Every original field is retained in an `_original` column. `experiments/synthetic_recovery/curated/source_recovery_audit.csv` contains old/new values, employee ID, source line and generator hash. The corresponding file under `data/curated` is header-only because submission data receives no generator corrections.

The experiment has 2,400 unique employees, all with known countries and valid employment dates. Submission curation instead retains 9 unknown countries and quarantines 10 invalid-date records. Both remove seven exact duplicate copies. External economic-data coverage remains partial.

Use rebuilt summaries and a successful current pipeline manifest for submission results. Archived recovered outputs are historical comparisons only.

Archived experiment outcomes: six-month retention is 1,596 / 1,822 (87.60%); senior twelve-month retention is 204 / 260 (78.46%); trailing regretted turnover is 82 / 1,625.23 average daily headcount (5.05%). Conservative submission outcomes are 1,580 / 1,813 (87.15%), 209 / 266 (78.57%) and 5.10%, respectively.

Replay initially caught Windows checkout line-ending conversions in 29 archived HTML files. Their bytes were restored only after LF conversion reproduced each existing manifest hash exactly. `.gitattributes` preserves archived HTML bytes and the raw CSV's required CRLF format on future checkouts. No source hashes were relaxed or rewritten to bypass validation.

Historical recovery validation: 67 Python tests passed and 35 output hashes matched on repeated builds. This does not certify the current submission revision. Current validation is recorded in `analysis/pipeline_manifest.json` and the acceptance checklist.
