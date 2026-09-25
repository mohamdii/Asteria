"""Auditable six-month retention under the documented mature-cohort convention."""
import csv
import json
from collections import Counter
from datetime import date
from clean_assessment import ROOT, anniversary, main as clean, write_csv


def classify(row, as_of, start, stop, months=6):
    result = {k: row[k] for k in ('employee_id', 'source_csv_line', 'country_code', 'business_unit', 'hire_date', 'termination_date', 'quality_flags')}
    anniversary_field = {6: 'six_month_anniversary', 12: 'twelve_month_anniversary'}[months]
    result[anniversary_field] = ''
    result['hire_year'] = row['hire_date'][:4] if row['hire_date'] else 'unknown'
    if row['valid_employment_dates'] != 'true':
        status = 'excluded_invalid_dates'
    elif row['retention_eligible'] != 'true':
        status = 'excluded_contradiction'
    else:
        hire = date.fromisoformat(row['hire_date'])
        milestone = anniversary(hire, months)
        result[anniversary_field] = str(milestone)
        if not start <= hire <= stop:
            status = 'outside_objective_hire_period'
        elif milestone > as_of:
            status = 'pending_observation'
        else:
            end = date.fromisoformat(row['termination_date']) if row['termination_date'] else None
            status = 'retained' if end is None or end >= milestone else 'left_before_milestone'
    result['status'] = status
    return result


def summarize(rows, target):
    counts = Counter(r['status'] for r in rows)
    denominator = counts['retained'] + counts['left_before_milestone']
    rate = counts['retained'] / denominator if denominator else None
    return {
        'records': len(rows), 'eligible_hires': denominator, 'retained': counts['retained'],
        'left_before_milestone': counts['left_before_milestone'],
        'pending_observation': counts['pending_observation'],
        'excluded_invalid_dates': counts['excluded_invalid_dates'],
        'excluded_contradiction': counts['excluded_contradiction'],
        'outside_objective_hire_period': counts['outside_objective_hire_period'],
        'retention_rate': rate, 'target': target,
        'target_status': 'unavailable' if rate is None else ('met' if rate >= target else 'below_target'),
    }


def main():
    clean()  # Verify raw provenance and rebuild curation before calculating.
    manifest = json.loads((ROOT / 'data/raw/assessment_data_manifest.json').read_text())
    with (ROOT / 'data/raw/retention_objectives.csv').open(newline='', encoding='utf-8') as stream:
        objective = next(r for r in csv.DictReader(stream) if r['objective_id'] == 'NEW_HIRE_6M')
    if objective['direction'] != 'at_least' or objective['unit'] != 'proportion':
        raise ValueError('Unsupported six-month objective contract')
    as_of = date.fromisoformat(manifest['workforce_as_of_date'])
    start, stop = (date.fromisoformat(objective[k]) for k in ('effective_from', 'effective_to'))
    target = float(objective['target_value'])
    with (ROOT / 'data/curated/employee_lifecycle_curated.csv').open(newline='', encoding='utf-8') as stream:
        audit = [classify(r, as_of, start, stop) for r in csv.DictReader(stream)]
    overall = summarize(audit, target)
    assert overall['records'] == sum(overall[k] for k in ('eligible_hires', 'pending_observation', 'excluded_invalid_dates', 'excluded_contradiction', 'outside_objective_hire_period'))
    annual = [{'hire_year': year, **summarize([r for r in audit if r['hire_year'] == year], target)} for year in sorted({r['hire_year'] for r in audit})]
    output = ROOT / 'analysis'
    output.mkdir(exist_ok=True)
    write_csv(output / 'new_hire_6m_employee_audit.csv', audit, list(audit[0]))
    write_csv(output / 'new_hire_6m_by_hire_year.csv', annual, list(annual[0]))
    summary = {'objective_id': objective['objective_id'], 'as_of': str(as_of), 'hire_period': [str(start), str(stop)],
               'overall': overall, 'by_hire_year': annual,
               'notes': ['Rates pool eligible hires, not averages of annual percentages.',
                         '2025 represents only mature cohorts, not the full hiring year.',
                         'Invalid dates take exclusion precedence; missing hire dates cannot be assigned to the objective period.',
                         'Termination on the anniversary counts as retained under the last-day-employed convention.']}
    (output / 'new_hire_6m_summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
