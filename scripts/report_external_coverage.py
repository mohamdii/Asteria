"""Reconcile historical feature coverage and prioritize acquisition gaps."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ('matched', 'no_verified_historical_match', 'stale', 'missing_country', 'invalid_or_excluded_employment')


def summarize(rows):
    groups = defaultdict(Counter)
    priorities = defaultdict(Counter)
    seen = set()
    employee_indicators = defaultdict(set)
    indicators = set()
    for row in rows:
        key = (row['employee_id'], row['indicator'])
        if key in seen:
            raise ValueError('Duplicate employee/indicator')
        seen.add(key)
        employee_indicators[row['employee_id']].add(row['indicator'])
        indicators.add(row['indicator'])
        status = row['join_status']
        if status not in STATUSES:
            raise ValueError('Unknown join status: '+status)
        year = row['hire_date'][:4] or 'unknown'
        country = row['country'] or 'unknown'
        groups[(row['indicator'], country, year)][status] += 1
        if '2021' <= year <= '2025' and status in ('stale', 'no_verified_historical_match'):
            priorities[(row['indicator'], row['hire_date'][:7])][country] += 1
    if any(values != indicators for values in employee_indicators.values()):
        raise ValueError('Incomplete indicator coverage for employee')
    coverage = []
    for (indicator, country, year), counts in sorted(groups.items()):
        total = sum(counts.values())
        eligible = counts['matched'] + counts['stale'] + counts['no_verified_historical_match']
        coverage.append(dict(indicator=indicator, country=country, hire_year=year, records=total,
            **{s:counts[s] for s in STATUSES}, external_match_eligible=eligible,
            matched_pct_all=round(100*counts['matched']/total, 2),
            matched_pct_eligible=round(100*counts['matched']/eligible, 2) if eligible else None))
    ranked = []
    for (indicator, month), counts in sorted(priorities.items(), key=lambda x:(-sum(x[1].values()), x[0])):
        ranked.append(dict(indicator=indicator, hire_month=month, affected_records=sum(counts.values()),
            countries=dict(sorted(counts.items())),
            action='Find verified B-N evidence; do not substitute B-F' if indicator=='vacancies' else 'Find earlier published, sufficiently recent evidence'))
    return coverage, ranked


def main():
    source = ROOT/'analysis/expanded_historical_features.csv'
    with source.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    coverage, priorities = summarize(rows)
    payload = dict(source=str(source.relative_to(ROOT)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        scope='All curated employees; workforce KPI eligibility and milestone maturity are separate. Priorities cover hire dates in 2021-2025 only.',
        denominators='All = records in group. Eligible = matched + stale + no verified historical match. Missing country/employment exclusions remain visible.',
        priority_caveat='Hire months identify evidence needs, not publication dates. Counts overlap across indicators and are not guaranteed gains from one release.',
        coverage=coverage, acquisition_priorities=priorities)
    (ROOT/'analysis/external_coverage_report.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    lines = ['# External coverage by country and hire year', '', payload['scope'], '', payload['denominators'], '',
        '| Indicator | Country | Hire year | Records | Matched | Missing evidence | Stale | Missing country | Employment excluded | Matched / eligible |',
        '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in coverage:
        pct = 'N/A' if r['matched_pct_eligible'] is None else str(r['matched_pct_eligible'])+'%'
        lines.append(f"| {r['indicator']} | {r['country']} | {r['hire_year']} | {r['records']} | {r['matched']} | {r['no_verified_historical_match']} | {r['stale']} | {r['missing_country']} | {r['invalid_or_excluded_employment']} | {pct} |")
    lines += ['', '## Acquisition priorities', '', payload['priority_caveat'], '']
    for indicator in sorted({r['indicator'] for r in priorities}):
        lines += [f'### {indicator}', '']
        for r in [p for p in priorities if p['indicator']==indicator][:5]:
            lines.append(f"- Hires in {r['hire_month']}: {r['affected_records']} unmatched records; country counts {r['countries']}. {r['action']}.")
        lines.append('')
    (ROOT/'analysis/external_coverage_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(groups=len(coverage), employees=len({r['employee_id'] for r in rows}), priority_months=len(priorities))))


if __name__ == '__main__':
    main()
