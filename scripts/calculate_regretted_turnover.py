"""Trailing twelve-month turnover with auditable employee-days and uncertainty."""
import csv
import json
from collections import Counter
from datetime import date, timedelta
from clean_assessment import ROOT, anniversary, main as clean, write_csv


def calculate(rows, end, target):
    start = anniversary(end, -12) + timedelta(days=1)
    days = (end-start).days + 1
    daily = [0] * days
    audit = []
    for row in rows:
        entry = {k: row[k] for k in ('employee_id', 'source_csv_line', 'hire_date', 'termination_date', 'termination_type', 'regretted_exit', 'quality_flags')}
        employee_days = 0
        if row['valid_employment_dates'] != 'true':
            status = 'excluded_invalid_dates'
        elif row['regretted_turnover_eligible'] != 'true':
            status = 'excluded_contradiction'
        else:
            hire = date.fromisoformat(row['hire_date'])
            departure = date.fromisoformat(row['termination_date']) if row['termination_date'] else None
            first, last = max(start, hire), min(end, departure or end)
            employee_days = max(0, (last-first).days + 1)
            for offset in range(employee_days):
                daily[(first-start).days+offset] += 1
            status = 'no_departure_in_window'
            if departure and start <= departure <= end:
                kind, regret = row['termination_type'], row['regretted_exit']
                if kind == 'Voluntary' and regret == 'true':
                    status = 'confirmed_regretted_departure'
                elif kind in ('', 'Voluntary') and regret in ('', 'true'):
                    status = 'potentially_regretted_unknown'
                else:
                    status = 'other_departure'
        entry.update(employee_days=employee_days, status=status)
        audit.append(entry)
    counts = Counter(r['status'] for r in audit)
    total_days = sum(r['employee_days'] for r in audit)
    assert total_days == sum(daily)
    average = total_days/days
    confirmed = counts['confirmed_regretted_departure']
    ambiguous = counts['potentially_regretted_unknown']
    lower = confirmed/average if average else None
    upper = (confirmed+ambiguous)/average if average else None
    decision = ('unavailable' if lower is None else 'above_target' if lower > target else
                'met_under_classification_scenarios' if upper <= target else 'uncertain_due_to_classification')
    summary = dict(window_start=str(start), window_end=str(end), calendar_days=days,
                   records=len(rows), classifications=dict(sorted(counts.items())), employee_days=total_days,
                   average_daily_headcount=average, confirmed_regretted_departures=confirmed,
                   potentially_regretted_unknown_departures=ambiguous, confirmed_rate=lower,
                   classification_upper_rate=upper, target=target, target_status=decision,
                   notes=['Range covers unknown classifications among eligible departures only; it is not a confidence interval.',
                          'Excluded records can affect both numerator and denominator; the range does not bound that missing-data risk.',
                          'All eligible employees contribute headcount, including unknown departure classifications and pre-window hires.',
                          'Termination date is included as the last day employed.'])
    headcount = [{'date': str(start+timedelta(days=i)), 'headcount': n} for i,n in enumerate(daily)]
    return summary, audit, headcount


def main():
    clean()
    raw = ROOT/'data/raw'
    as_of = date.fromisoformat(json.loads((raw/'assessment_data_manifest.json').read_text())['workforce_as_of_date'])
    with (raw/'retention_objectives.csv').open(newline='', encoding='utf-8') as stream:
        objective = next(r for r in csv.DictReader(stream) if r['objective_id']=='REGRETTED_TURNOVER_12M')
    target = float(objective['target_value'])
    if objective['direction'] != 'at_most' or objective['unit'] != 'proportion' or not 0 <= target <= 1:
        raise ValueError('Invalid regretted-turnover objective contract')
    if not date.fromisoformat(objective['effective_from']) <= as_of <= date.fromisoformat(objective['effective_to']):
        raise ValueError('Snapshot outside objective effective period')
    with (ROOT/'data/curated/employee_lifecycle_curated.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    summary, audit, headcount = calculate(rows, as_of, target)
    summary['objective_id'] = objective['objective_id']
    out = ROOT/'analysis'
    out.mkdir(exist_ok=True)
    write_csv(out/'regretted_turnover_employee_audit.csv', audit, list(audit[0]))
    write_csv(out/'regretted_turnover_daily_headcount.csv', headcount, ['date','headcount'])
    (out/'regretted_turnover_summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
