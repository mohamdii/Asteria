# Presenter guide

13 slides, 15 minutes. Questions follow. Use workforce-retention-submission.pdf.

## 1. Workforce retention

0:00-0:45 (45 seconds)

Introduce this as an analysis of supplied synthetic workforce data. The question is whether retention and regretted turnover meet the stated objectives, and how much historical economic evidence can responsibly provide context. Explain that the delivered application is an offline HTML dashboard backed by a Python pipeline. The presentation covers the results first, then the decisions that make them interpretable, and finally a proposed production design.

Sources: docs/requirements-and-decisions.md

## 2. Senior retention is the clearest shortfall

0:45-2:00 (75 seconds)

Start with the business finding. Six-month retention exceeds the target by 1.15 percentage points. Senior retention falls 11.43 percentage points below its target and deserves investigation. Regretted turnover remains below the ceiling. These measures use different eligible populations, so their rates should not be compared as if they measured the same thing. All findings describe this synthetic dataset. The external analysis does not explain why employees leave. Use the next slides to show how the denominators and exclusions support these conclusions.

Sources: analysis/new_hire_6m_summary.json; analysis/senior_hire_12m_summary.json; analysis/regretted_turnover_summary.json

## 3. Conservative cleaning preserves uncertainty

2:00-3:15 (75 seconds)

Explain that the raw input remains unchanged. Cleaning removes exact duplicate rows and applies documented country aliases, including EL to GR and ROM to RO. It does not guess missing countries. Nine unique records still have unknown country. Five of those fall within the mature six-month population, which explains the five shown in coverage. Ten records have missing hire dates or termination before hire and are excluded from date-based metrics, while retained in the audit. Flags can overlap and must not be added as if they were disjoint counts. The provisional Sr Mgmt mapping receives a separate sensitivity check. No hidden generator values contribute to the results.

Sources: data/curated/quality_summary.json; docs/requirements-and-decisions.md

## 4. Retention uses mature hiring cohorts

3:15-4:30 (75 seconds)

Walk through the retention definition. The hiring objective period runs from 2021 through 2025. The snapshot is 31 December 2025. A person must have had enough time to reach the relevant calendar-month anniversary to enter the denominator. Termination on the anniversary counts as retained under the selected inclusive boundary rule. Someone with an immature observation remains pending even if an early departure is already known, preventing an asymmetric denominator. Senior means Senior Leader including the provisional Sr Mgmt mapping. Excluding that mapping produces 203 retained from 259 eligible hires, or 78.38 percent, so the shortfall persists.

Sources: analysis/new_hire_6m_summary.json; analysis/senior_hire_12m_summary.json; docs/requirements-and-decisions.md

## 5. Regretted turnover uses daily headcount

4:30-5:45 (75 seconds)

The turnover window is 1 January through 31 December 2025. Its denominator comes from 586,744 employee-days divided by 365, giving an unrounded average daily headcount of about 1,607.5178. The displayed 1,607.52 is rounded for reading. It is not the count of all people who contributed during the year. The numerator contains 82 confirmed regretted exits. Treating the two potentially regretted unknown departures as regretted produces an upper classification scenario of 84 exits and 5.23 percent. This is a classification sensitivity scenario, not a confidence interval.

Sources: analysis/regretted_turnover_summary.json

## 6. The dashboard exposes population limits

5:45-7:00 (75 seconds)

Demonstrate the HTML dashboard for about one minute, or describe these steps if a live demo is unavailable. First show the company-wide KPI cards. Change the retention measure to senior twelve-month retention and choose 2025. The user-provided screenshot confirms the result is zero mature hires and Unavailable, rather than a zero retention rate. Explain that all 49 senior hires in 2025 remain pending at this snapshot. Restore all years, then show the country comparison and an economic signal. The economic panel respects measure, country and hire year but includes all business units, as its note states. The coverage selector uses the full metric population independently of cohort filters.

Sources: dashboard/template.html; docs/dashboard-browser-qa.md; analysis/senior_hire_12m_summary.json

## 7. Historical context must predate the decision

7:00-8:00 (60 seconds)

Explain the difference between reference period and release availability. A number describing an earlier month can still have been published after the hire date, so the join checks both dates. Same-day releases are excluded by the strict rule. Retention uses the hire date as its cutoff. Turnover uses the start of its annual window. Each joined value retains its source period and vintage. Age limits exclude stale observations. Annual CPI remains annual rather than being expanded into invented monthly measurements. Saved source evidence and metadata allow the offline pipeline to replay the selection.

Sources: docs/historical-evidence-and-flow.md; docs/requirements-and-decisions.md

## 8. External coverage varies by indicator

8:00-9:15 (75 seconds)

The matched population depends on the indicator. Unemployment has 1,092 matches, five missing countries, 222 missing-evidence cases and 494 stale cases. CPI matches 1,808, leaving only the five missing countries. The supplementary vacancy series matches 1,408, with five missing countries, 279 missing-evidence cases and 121 stale cases. Bâ€“F covers industry and construction. It does not represent every workforce sector. The preferred broader Bâ€“N series has no verified historical matches and is not substituted silently. Coverage affects contextual analysis, while headline retention still uses the full eligible population.

Sources: analysis/metric_external_coverage.md

## 9. Economic associations are weak or unstable

9:15-10:15 (60 seconds)

Read these as descriptive correlations, not causal effects or statistical significance. The unemployment analysis has 72 country-quarter cohorts. Restricting to cohorts with at least ten hires changes its correlation to minus 0.071. The vacancy correlation changes sign to plus 0.054 under that check. CPI uses 30 country-year cohorts and retains its annual frequency. Reused source periods mean cohort counts are not independent economic samples. Country composition, calendar trends and selection remain possible explanations. All senior unemployment and vacancy cohorts have fewer than ten matched hires. One turnover window cannot support a credible repeated-period relationship analysis.

Sources: analysis/association_analysis.md

## 10. The delivered solution runs locally

10:15-11:15 (60 seconds)

Explain the actual implementation clearly. Python code handles cleaning, metric eligibility, external parsing and temporal matching. SQLite reporting views reconcile the results, and the builder embeds them into a standalone HTML dashboard. The dashboard template is source code, and analysis/dashboard.html is generated output. Acquisition tools are separate from deterministic offline processing. The pipeline entry point coordinates the work. Existing checks include Python tests, SQL reconciliation, saved-input hashes, repeat-output verification and a simulated DOM dashboard harness. User screenshots provide additional visual evidence. Do not describe the simulated DOM as a complete browser accessibility test. The current workflow builds in an isolated release folder and publishes only after checks pass, using an atomic current-release pointer. Open the dashboard from that release.

Sources: docs/code-structure.md; analysis/pipeline_manifest.json; docs/dashboard-browser-qa.md

## 11. Proposed production architecture

11:15-12:30 (75 seconds)

This slide is a proposal, not a record of deployed cloud services. In the proposed architecture, ADF coordinates acquisition and processing. Bronze storage retains source bytes and metadata. Databricks silver tables contain validated workforce data and economic vintages, and gold tables contain metrics and coverage. A release registry keeps one consistent approved run. Failed checks preserve the previously published release. Databricks SQL and Power BI form a proposed consumption path. Entra identities, Key Vault, Unity Catalog and monitoring support access and operations. No Azure, Databricks or Power BI deployment has been provisioned or tested for this project.

Sources: docs/production-architecture.md

## 12. AI assistance and human accountability

12:30-14:00 (90 seconds)

Explain your role accurately: you questioned the cleaning approach, required removal of the original source HTML and hidden-generator recovery, approved the package refactor and publication changes, and confirmed manual browser checks. Codex implemented and tested code, researched saved source evidence, and produced documentation and presentation materials. A significant rejected approach was recovering missing values from privileged synthetic generator truth. The submitted solution keeps missing countries unknown and invalid employment dates quarantined. Verification combines raw hashes, employee audits, SQL reconciliation, repeated output hashes and tests, including interrupted-publication cases. The two decorative images were AI-generated and do not depict real project staff or deployed infrastructure. Distinguish your reported browser checks from agent-run tests. Exact model versions were not verified. My approximate effort was 15 hours.

Sources: AI_USAGE.md; docs/dashboard-browser-qa.md; tests/test_publication.py

## 13. Next decisions

14:00-15:00 (60 seconds)

Close by returning to the main result. Senior retention is the priority for further investigation, while the other two headline objectives meet their thresholds in this synthetic data. A real investigation would need internal evidence about onboarding, roles, teams and departures rather than assuming the macroeconomic signals explain the gap. Ask data owners to resolve missing countries and unknown classifications through traceable corrections. Improve historical source coverage and collect repeated turnover windows before extending the analysis. Confirm the eligibility rules and provisional seniority mapping before production deployment. The fifteen-minute walkthrough ends here, with questions afterward.

Sources: docs/requirements-and-decisions.md; analysis/association_analysis.md
