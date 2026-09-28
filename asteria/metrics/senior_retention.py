"""Required senior-hire twelve-month metric and seniority-mapping sensitivity."""
import csv
import json
from datetime import date
from asteria.metrics.retention import classify, summarize
from asteria.paths import ROOT
from asteria.common import write_csv


def senior_rows(rows, include_mapped=True):
    return [r for r in rows if r['career_level'] == 'Senior Leader'
            and (include_mapped or r['career_level_original'] != 'Sr Mgmt')]


def calculate(rows, as_of, start, stop, target, include_mapped=True):
    audit = []
    for row in senior_rows(rows, include_mapped):
        decision = classify(row, as_of, start, stop, months=12)
        decision.update(career_level=row['career_level'], career_level_original=row['career_level_original'])
        audit.append(decision)
    summary = summarize(audit, target)
    assert summary['records'] == sum(summary[k] for k in ('eligible_hires', 'pending_observation', 'excluded_invalid_dates', 'excluded_contradiction', 'outside_objective_hire_period'))
    return audit, summary


def main():
    as_of = date.fromisoformat(json.loads((ROOT / 'data/raw/assessment_data_manifest.json').read_text())['workforce_as_of_date'])
    with (ROOT / 'data/raw/retention_objectives.csv').open(newline='', encoding='utf-8') as stream:
        objective = next(r for r in csv.DictReader(stream) if r['objective_id'] == 'SENIOR_HIRE_12M')
    if objective['direction'] != 'at_least' or objective['unit'] != 'proportion':
        raise ValueError('Unsupported senior objective contract')
    start, stop = (date.fromisoformat(objective[k]) for k in ('effective_from', 'effective_to'))
    target = float(objective['target_value'])
    if start > stop or not 0 <= target <= 1:
        raise ValueError('Invalid objective dates or threshold')
    with (ROOT / 'data/curated/employee_lifecycle_curated.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    audit, overall = calculate(rows, as_of, start, stop, target)
    _, sensitivity = calculate(rows, as_of, start, stop, target, include_mapped=False)
    annual = [{'hire_year': year, **summarize([r for r in audit if r['hire_year'] == year], target)} for year in sorted({r['hire_year'] for r in audit})]
    output = ROOT / 'analysis'
    output.mkdir(exist_ok=True)
    write_csv(output / 'senior_hire_12m_employee_audit.csv', audit, list(audit[0]) if audit else ['employee_id', 'status'])
    write_csv(output / 'senior_hire_12m_by_hire_year.csv', annual, list(annual[0]) if annual else ['hire_year', 'retention_rate'])
    summary = {'objective_id': objective['objective_id'], 'as_of': str(as_of), 'hire_period': [str(start), str(stop)],
               'non_senior_records_outside_scope': len(rows)-len(audit), 'overall': overall,
               'excluding_assumed_sr_mgmt': sensitivity, 'by_hire_year': annual,
               'notes': ['Senior Leader includes provisionally mapped Sr Mgmt; Manager is outside scope.',
                         '2025 hires have no complete twelve-month observation window and no rate.',
                         'Retention is evaluated on the anniversary, with termination date inclusive.',
                         'Unknown hire dates are excluded before period classification.']}
    (output / 'senior_hire_12m_summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
