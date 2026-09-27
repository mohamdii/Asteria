"""Inspect and curate the supplied snapshot without altering raw inputs."""
import calendar
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = {'GR', 'RO', 'PL', 'IT', 'IE', 'BG'}


def apply_corrections(row, corrections):
    """Apply only exact source-matched, evidence-backed synthetic repairs."""
    result = dict(row)
    for correction in corrections:
        field = correction['field']
        if field == 'employee_id' or field not in row:
            raise ValueError('Unsupported correction field: ' + field)
        if row[field] != correction['original']:
            raise ValueError('Correction source mismatch: ' + row['employee_id'] + '/' + field)
        result[field] = correction['corrected']
    return result


def anniversary(day, months):
    index = day.year * 12 + day.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def curate(row, as_of):
    result = dict(row)
    flags = []
    result['country_code_original'] = row['country_code']
    result['career_level_original'] = row['career_level']
    result['country_code'] = {'EL': 'GR', 'ROM': 'RO'}.get(row['country_code'], row['country_code'])
    if result['country_code'] != row['country_code']:
        flags.append('country_alias_mapped')
    if result['country_code'] not in COUNTRIES:
        flags.append('missing_or_unknown_country')
    if row['career_level'] == 'Sr Mgmt':
        result['career_level'] = 'Senior Leader'
        flags.append('seniority_mapping_assumed')
    dates = {}
    for key in ('hire_date', 'termination_date'):
        try:
            dates[key] = date.fromisoformat(row[key]) if row[key] else None
        except ValueError:
            dates[key] = None
            flags.append('invalid_' + key)
    hire, end = dates['hire_date'], dates['termination_date']
    if not row['hire_date']:
        flags.append('missing_hire_date')
    if hire and hire > as_of:
        flags.append('hire_after_snapshot')
    if end and end > as_of:
        flags.append('termination_after_snapshot')
    if hire and end and end < hire:
        flags.append('termination_before_hire')
    if end and not row['termination_type']:
        flags.append('termination_type_unknown')
    if end and row['regretted_exit'] not in ('true', 'false'):
        flags.append('regretted_classification_unknown')
    if row['regretted_exit'] == 'true' and row['termination_type'] not in ('Voluntary', ''):
        flags.append('regretted_type_conflict')
    if not row['termination_date'].strip():
        if row['regretted_exit'] == 'true':
            flags.append('regretted_without_departure')
        if row['termination_type'].strip():
            flags.append('termination_type_without_departure')
    date_errors = {'invalid_hire_date', 'invalid_termination_date', 'missing_hire_date',
                   'hire_after_snapshot', 'termination_after_snapshot', 'termination_before_hire'}
    valid = not bool(date_errors.intersection(flags))
    employment_conflict = bool({'regretted_without_departure', 'termination_type_without_departure'}.intersection(flags))
    retention_ok = valid and not employment_conflict
    regretted_ok = retention_ok and 'regretted_type_conflict' not in flags
    result['valid_employment_dates'] = str(valid).lower()
    result['retention_eligible'] = str(retention_ok).lower()
    result['headcount_eligible'] = str(retention_ok).lower()
    result['regretted_turnover_eligible'] = str(regretted_ok).lower()
    result['country_analysis_eligible'] = str(retention_ok and result['country_code'] in COUNTRIES).lower()
    result['is_senior_assumed'] = str(result['career_level'] == 'Senior Leader').lower()
    result['regretted_classification'] = ('conflict' if employment_conflict or 'regretted_type_conflict' in flags else
        row['regretted_exit'] if end and row['regretted_exit'] in ('true', 'false') else ('unknown' if end else 'not_applicable'))
    for months in (6, 12):
        result[f'mature_{months}m_as_of'] = str(valid and anniversary(hire, months) <= as_of).lower() if valid else 'false'
    result['quality_flags'] = '|'.join(flags)
    return result


def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    raw = ROOT / 'data/raw'
    manifest = json.loads((raw / 'assessment_data_manifest.json').read_text())
    for item in manifest['files']:
        payload = (raw / item['name']).read_bytes()
        with (raw / item['name']).open(newline='', encoding='utf-8') as stream:
            count = sum(1 for _ in csv.DictReader(stream))
        if hashlib.sha256(payload).hexdigest() != item['sha256'] or len(payload) != item['bytes'] or count != item['data_rows']:
            raise ValueError('Raw manifest verification failed: ' + item['name'])
    as_of = date.fromisoformat(manifest['workforce_as_of_date'])
    with (raw / 'employee_lifecycle_events.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    evidence = json.loads((ROOT / 'config/synthetic_source_corrections.json').read_text(encoding='utf-8'))
    if not manifest.get('synthetic') or evidence['mode'] != 'verified_synthetic_generator_recovery':
        raise ValueError('Source recovery is restricted to the verified synthetic assessment')
    if hashlib.sha256((raw / 'employee_lifecycle_events.csv').read_bytes()).hexdigest() != evidence['raw_sha256']:
        raise ValueError('Recovery evidence does not match raw snapshot')
    corrections = {}
    correction_keys = set()
    for item in evidence['corrections']:
        key = (item['employee_id'], item['field'])
        if key in correction_keys:
            raise ValueError('Duplicate source correction: ' + str(key))
        correction_keys.add(key)
        corrections.setdefault(item['employee_id'], []).append(item)
    seen, ids, curated, audit = set(), set(), [], []
    recovery_audit = []
    for line, row in enumerate(rows, start=2):
        signature = tuple(row.items())
        if signature in seen:
            audit.append({'source_csv_line': line, 'employee_id': row['employee_id'], 'issue': 'exact_duplicate_removed', 'action': 'exclude_duplicate_copy'})
            continue
        if row['employee_id'] in ids:
            raise ValueError('Conflicting employee records require review: ' + row['employee_id'])
        seen.add(signature)
        ids.add(row['employee_id'])
        repairs = corrections.get(row['employee_id'], [])
        record = curate(apply_corrections(row, repairs), as_of)
        for field, value in row.items():
            record[field + '_original'] = value
        record['source_recovery_fields'] = '|'.join(item['field'] for item in repairs)
        record['source_recovery_method'] = evidence['mode'] if repairs else ''
        if repairs:
            record['quality_flags'] = '|'.join(filter(None, [record['quality_flags'], 'synthetic_source_recovered']))
        for item in repairs:
            recovery_audit.append({'source_csv_line': line, **item, 'source_sha256': evidence['source_sha256']})
        record['source_csv_line'] = line
        curated.append(record)
        for flag in filter(None, record['quality_flags'].split('|')):
            action = 'retain_with_flag'
            if record['valid_employment_dates'] == 'false':
                action = 'quarantine_from_date_based_metrics'
            elif flag in ('regretted_without_departure', 'termination_type_without_departure'):
                action = 'exclude_retention_headcount_and_regretted_turnover'
            elif flag == 'regretted_type_conflict':
                action = 'exclude_regretted_turnover_only'
            audit.append({'source_csv_line': line, 'employee_id': row['employee_id'], 'issue': flag, 'action': action})
    if set(corrections) - ids:
        raise ValueError('Correction references an unknown employee')
    out = ROOT / 'data/curated'
    out.mkdir(parents=True, exist_ok=True)
    fields = list(curated[0])
    quarantined = [r for r in curated if r['valid_employment_dates'] == 'false']
    write_csv(out / 'employee_lifecycle_curated.csv', curated, fields)
    write_csv(out / 'employment_date_quarantine.csv', quarantined, fields)
    write_csv(out / 'quality_audit.csv', audit, ['source_csv_line', 'employee_id', 'issue', 'action'])
    write_csv(out / 'source_recovery_audit.csv', recovery_audit,
              ['source_csv_line', 'employee_id', 'field', 'original', 'corrected', 'source_sha256'])
    summary = {
        'as_of': str(as_of), 'raw_manifest_verified': True, 'raw_rows': len(rows),
        'curated_rows_including_quarantine': len(curated), 'exact_duplicates_removed': len(rows)-len(curated),
        'employment_date_quarantine': len(quarantined), 'valid_employment_dates': len(curated)-len(quarantined),
        'country_analysis_eligible': sum(r['country_analysis_eligible']=='true' for r in curated),
        'contradictory_records': sum(r['regretted_classification']=='conflict' for r in curated),
        'source_recovery': {'mode': evidence['mode'], 'corrected_cells': len(recovery_audit),
                            'corrected_employees': len(corrections),
                            'fields': dict(sorted(Counter(r['field'] for r in recovery_audit).items())),
                            'evidence': 'config/synthetic_source_corrections.json'},
        'issues': dict(sorted(Counter(a['issue'] for a in audit).items())),
        'note': 'Flags can overlap. Curated file retains quarantined rows; consumers must filter eligibility. Maturity flags are not final metric denominators.'
    }
    (out / 'quality_summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
