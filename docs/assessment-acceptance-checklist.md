# Assessment acceptance audit

Current status: see [the 2026-09-28 submission review](submission-review-2026-09-28.md). The older counts and statuses below are historical and superseded by that review.

Current cleaning decision: submission uses conservative supplied-data cleaning. The source assessment HTML, generator recovery code and experiment artifacts have been removed. Static requirements and links remain in JSON only. Missing countries remain unknown; 10 invalid-date records are quarantined; seniority alias assumptions retain sensitivity analysis. Older recovery entries are historical only.

Cleaning-policy verification: full offline repeat replay passed with 68 Python tests and 35 byte-identical outputs using Python 3.12.14 and pypdf 6.19.0. Dashboard DOM checks passed. This resolves the cleaning decision and repeat-replay gap; it does not resolve outstanding browser QA, final clean-environment verification, architecture/source documentation or presentation work.

Reviewed 2026-09-26 against `config/assessment_reference.json`, current scripts, SQL, dashboard template, documentation and saved verification evidence. The original assessment HTML was not used. Selected track: Software emphasis. Both emphasis tracks require the complete vertical slice.

Overall: **not ready to declare complete**. This is a deliverable review, not a fresh test run. Latest recorded run: 62 Python tests, dashboard DOM-harness checks, 32 byte-identical outputs on repeated same-environment builds. Older clean-copy reports predate SQL/dashboard.

Status meanings: Complete = evidence exists for the stated scope; Partial = substantive work exists but explicit requirements remain; Missing = no deliverable found; Unverified = depends on execution or information not available in the reviewed artifacts.

| Requirement | Status | Evidence and remaining acceptance work |
|---|---|---|
| Refine decision, scope, grain, metrics and temporal assumptions | Complete for implemented scope | `docs/requirements-and-decisions.md` consolidates the leadership decision, grain, metric definitions, working assumptions, open questions, cleaning policy, temporal rules, rejected scope, consequences and acceptance evidence. Business-owner confirmation is not claimed. |
| All three auditable retention objectives | Complete | Three calculators, employee audits, summary JSON, SQL reconciliation; includes maturity, invalid records, senior-mapping sensitivity and unknown-turnover scenario. Scope is snapshot turnover, not a historical turnover series. |
| At least two authoritative public providers | Complete | Eurostat and World Bank, with saved source metadata and releases. Provider count does not establish independence of underlying measurements. |
| Three external indicators and two useful lenses | Complete for acquisition | Unemployment, CPI and vacancies; labour supply, cost of living and labour demand. B-F remains supplementary under the approved decision. Analysis of these signals remains missing. |
| Approximately three years of source history where supported | Complete for reference-period acquisition; partial for strict joins | Current API fixtures cover 2021-2025. Archived publications and strict join availability are incomplete; do not claim full point-in-time coverage. The assessment does not require 100% employee matches. |
| Source register and contracts | Complete for selected series | `docs/source-register.md` consolidates definitions, dimensions, units, cadence, timing, vintage interpretation, evidence paths, country mapping, lineage lookup, fitness and coverage gaps. Official Eurostat reuse terms and the CPI-specific CC BY-4.0 label were checked on 2026-09-27; full-release redistribution exceptions remain explicit. |
| Raw, canonical and consumption layers | Complete for implemented scope | Raw files/releases, curated workforce, canonical observations, joined audits, SQLite reports and dashboard. |
| Traceable source/unit/frequency/period/load-time/quality lineage | Partial | Full selected-observation lineage plus source hashes and retrieval manifests exist. Document the lookup from observation source file/hash to retrieval timestamp and expose useful source dates in the dashboard. |
| No future-information joins; mixed-frequency integrity | Complete under documented assumptions | As-of selector, hire/window-start cutoffs, strict prior publication, vintage evidence and age thresholds; CPI remains annual. CPI archive-date mapping is an explicit interpretation. |
| Evaluate economic relationships | Missing | Coverage and KPI calculations are not association analysis. Add a defensible descriptive/statistical method with independent country-period units or clustering, sample size, uncertainty, confounding and multiple-comparison treatment. Avoid causal claims. |
| At least three evidence-backed findings and a limitation/non-finding | Partial | Three headline objective findings and caveats exist. Add analytical findings from the external-signal analysis and document decision relevance, segment stability, data-health effects and further evidence needed. |
| Interactive country/time/objective/workforce-segment filters | Partial | Country, retention objective and business unit controls exist. A time filter is missing. Turnover is selectable only in coverage; make any supported objective/time scope and fixed snapshot constraints explicit. |
| Retention trends/status alongside selected external signals | Partial | Retention cohort trends/status exist. Dashboard shows coverage, not actual signal values/trends alongside outcomes. Add a selected-signal view retaining native periods and units. |
| Relationship views with sample size or uncertainty | Missing | No relationship plot or equivalent table. Add it after the association dataset/method is validated. |
| Dashboard trust: freshness, coverage, exclusions, attribution, methodology | Partial | Coverage/exclusions/methodology and hash lineage exist. Show observation/release/retrieval dates or age summaries and readable provider attribution; hashes alone are not sufficient user-facing source context. |
| Accessible interactions and graceful empty/error states | Partial | Labels, SVG descriptions, table alternatives and unavailable states exist; DOM harness checks key filters. Real-browser layout, keyboard, mobile and accessibility review is outstanding; malformed/missing embedded-data handling needs review. |
| One-command core run and documented dependencies | Complete in current environment | `python scripts/run_pipeline.py`; pinned pypdf, offline saved evidence. Dashboard and SQL included. README clean-copy instructions must also include `dashboard/template.html`. |
| Deterministic replay and intentional overwrite | Complete in current environment | Latest pipeline manifest records 32 equal output hashes across two builds; raw inputs are unchanged. No cross-platform byte-equivalence claim. |
| Resilient API handling and observable failures | Partial | Shared client retries/timeouts/Retry-After/TLS fallback tested. Acquisition remains research-oriented; standardize provider failure reporting and content validation. |
| Safe partial failure | Partial | Pipeline stops and removes success marker; SQLite replacement is staged. Earlier stages can leave mixed-generation derived files, and an old dashboard can still be opened. Add staging/publication gating or an explicit consumer validity check. |
| Clear adapters/domain/configuration | Partial | Metric/temporal/HTTP/SQL/UI boundaries exist. Providers still share research-script helpers; scattered constants/contracts need a documented rationale or modest consolidation. |
| Tests across service and UI boundaries | Partial | 62 Python tests and separate JS DOM harness. JS check is not part of the core test command; no real-browser test. Re-run clean-copy verification for the final artifact set. |
| Python 3.11+, SQL, local HTML, no paid infrastructure | Complete for implementation | Python/SQLite/self-contained HTML. Tested runtime is Python 3.14; minimum-version compatibility has not been independently exercised. |
| Production architecture view | Complete as a proposed mapping | `docs/production-architecture.md` provides a Mermaid diagram and repository-to-ADF/Databricks/ADLS/Power BI mapping, with scheduling, secrets, permissions, observability, run-scoped publication, rollback and environment promotion. Cloud deployment and integration testing are explicitly not claimed. |
| README and requirements documentation | Partial | Core usage and limitations exist, but stale historical statements remain across docs. Consolidate current state, link architecture/refinement/source register and distinguish old verification evidence. |
| Generated evidence/screenshots or export | Partial | CSV/JSON/SQLite/HTML outputs exist; HTML is an export. Add representative reviewed screenshots or another reviewed presentation export; visual QA is still outstanding. |
| AI usage/accountability | Partial | Task descriptions, changed suggestions, failures and checks are logged. Keep historical entries distinct from current status; add actual human review and approximate effort when supplied. Do not invent a model version or human validation. |
| 15-minute presentation | Missing | Add a lightweight Markdown, HTML or PDF deck: 3 minutes scope, 5 architecture/reliability, 4 dashboard/findings, 3 tradeoffs/AI/next steps. |
| Repository submission/access and deadline | Unverified | No evidence of reviewer access, final submission or deadline in inspected files. User must supply/confirm these logistics. |

## Follow-up review ? 2026-09-27

The table above is the historical 2026-09-26 audit. These updates supersede its analysis and dashboard rows:

- Association analysis already exists, including matched/unmatched breakdowns, country-centering, minimum-size and leave-one-country-out sensitivity. See docs/association-findings.md. Its cohort counts are not independent sample sizes; inferential uncertainty remains intentionally unestimated.
- The dashboard now includes hire-year filtering and economic exposure/retention scatterplots with accessible tables, sample counts, source-age ranges, and full-population sensitivity summaries. Country/year/measure affect relationships; business-unit filtering affects only retention charts. Preferred B?N has an explicit unavailable state. Actual native-period source timelines and release/retrieval dates remain unfinished.
- The Node DOM harness passed both existing checks and new year-filter, relationship, empty-selection, B?N and annual-CPI checks on this host. No Python executable was available on PATH. Full replay and fresh-copy verification remain pending; old manifests do not certify the updated dashboard. The browser tool reported no connected browsers, so visual/keyboard/mobile verification remains pending.
- The original assessment HTML was checked against the saved reference: its SHA-256 matches after CRLF-to-LF normalization. No requirement change was found through that comparison.

Immediate next steps: restore a Python 3.11+ runtime and pinned dependency, run the complete repeat-verification command, then browser QA. Finish source register/refinement/production architecture, publication safeguards and presentation before submission. Human effort/review and submission logistics still require the candidate's input.

## Recommended completion order (original audit)

1. Specify and implement a small external-association analysis with explicit effective sample sizes, selection bias and sensitivity checks. Existing missingness is not a reason to invent matches or assume B-F replaces B-N.
2. Add time filtering, actual signal context and relationship views to the dashboard; retain honest unavailable states. Test the resulting full interaction path.
3. Consolidate source contracts, refinement/acceptance decisions and the required production architecture view.
4. Review the dashboard in a real browser, harden partial-failure publication as needed, and perform a final fresh-copy replay of the full artifact set.
5. Create the presentation, record real human validation/effort, and complete repository handoff.

## User input needed later

- Actual approximate effort and which outputs you personally reviewed; these cannot be inferred from automated test results.
- Recruiter deadline and repository access/submission preference.
- Confirmation that you can explain the final analytical method and its limitations after we walk through the results.

Routine implementation can proceed under existing authorization. No new business decision is required merely to complete this checklist.

