"""Read-only validation of raw assessment records; writes a separate findings report."""
import csv
import json
import re
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from asteria.paths import ROOT
ALLOWED = {
    'country_code': {'GR', 'RO', 'PL', 'IT', 'IE', 'BG', 'EL', 'ROM'},
    'career_level': {'Individual Contributor', 'Manager', 'Senior Leader', 'Sr Mgmt'},
    'employment_type': {'Permanent', 'Fixed Term'},
    'termination_type': {'Voluntary', 'Involuntary', 'End of Contract'},
    'regretted_exit': {'true', 'false'},
    'direction': {'at_least', 'at_most'},
    'unit': {'proportion'},
}


def validate_record(row, contract, as_of):
    findings, parsed = [], {}
    def flag(field, rule):
        findings.append({'field': field, 'rule': rule})
    for column in contract:
        field = column['column_name']
        value = row.get(field)
        if value is None:
            flag(field, 'missing_column_or_cell')
            continue
        if not value.strip():
            if column['nullable'] == 'no':
                flag(field, 'required_value_missing')
            continue
        if field in ALLOWED and value not in ALLOWED[field]:
            flag(field, 'unrecognized_value')
        kind = column['logical_type']
        if kind == 'date':
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError()
                parsed[field] = date.fromisoformat(value)
            except ValueError:
                flag(field, 'invalid_iso_date')
        elif kind == 'decimal':
            try:
                number = Decimal(value)
                if not number.is_finite():
                    raise InvalidOperation()
                parsed[field] = number
            except InvalidOperation:
                flag(field, 'invalid_finite_decimal')
        elif kind == 'boolean' and value not in {'true', 'false'}:
            flag(field, 'invalid_boolean')
    start, stop = parsed.get('effective_from'), parsed.get('effective_to')
    if start and stop and start > stop:
        flag('effective_from', 'effective_dates_reversed')
    if 'target_value' in parsed and not Decimal(0) <= parsed['target_value'] <= Decimal(1):
        flag('target_value', 'proportion_out_of_range')
    hire, end = parsed.get('hire_date'), parsed.get('termination_date')
    if hire and end and end < hire:
        flag('termination_date', 'termination_before_hire')
    for field in ('hire_date', 'termination_date', 'record_updated_at'):
        if parsed.get(field) and parsed[field] > as_of:
            flag(field, 'date_after_snapshot')
    if not row.get('termination_date', '').strip():
        if row.get('regretted_exit') == 'true':
            flag('regretted_exit', 'regretted_without_departure')
        if row.get('termination_type', '').strip():
            flag('termination_type', 'termination_type_without_departure')
    if row.get('regretted_exit') == 'true' and row.get('termination_type') in {'Involuntary', 'End of Contract'}:
        flag('regretted_exit', 'regretted_type_conflict_under_proposed_rule')
    return findings


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def main():
    raw = ROOT / 'data/raw'
    contract = read_csv(raw / 'data_dictionary.csv')
    as_of = date.fromisoformat(json.loads((raw / 'assessment_data_manifest.json').read_text())['workforce_as_of_date'])
    findings, summaries = [], {}
    for dataset in ('employee_lifecycle_events', 'retention_objectives'):
        rows = read_csv(raw / (dataset + '.csv'))
        schema = [c for c in contract if c['dataset'] == dataset]
        for line, row in enumerate(rows, 2):
            for finding in validate_record(row, schema, as_of):
                findings.append({'dataset': dataset, 'source_csv_line': line,
                                 'record_id': row.get('employee_id', row.get('objective_id')), **finding})
        dataset_findings = [f for f in findings if f['dataset'] == dataset]
        summaries[dataset] = {'rows_checked': len(rows), 'findings': len(dataset_findings),
                              'rules': dict(Counter(f['rule'] for f in dataset_findings))}
    report = {'mode': 'audit_only_no_cleaning_policy_changes', 'as_of': str(as_of),
              'summary': summaries, 'findings': findings,
              'limits': ['Allowed values are pack-specific conventions; EL, ROM and Sr Mgmt are recognized aliases, not unflagged canonical values.',
                         'Nullable blanks are permitted by this schema audit; metric eligibility is separately handled by curation.',
                         'Exact duplicates and conflicting IDs are handled by the existing cleaning step.',
                         'This audit does not prove source truth or implement a gate for future schema violations.']}
    dest = ROOT / 'analysis/schema_validation.json'
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
