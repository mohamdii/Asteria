import importlib.util
import unittest
from datetime import date
from pathlib import Path

spec = importlib.util.spec_from_file_location('clean', Path(__file__).resolve().parents[1] / 'scripts/clean_assessment.py')
clean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean)


class CleaningTests(unittest.TestCase):
    def test_evidenced_repair_preserves_input_and_rejects_stale_value(self):
        raw = {'employee_id': 'a', 'country_code': ''}
        repairs = [{'field': 'country_code', 'original': '', 'corrected': 'GR'}]
        self.assertEqual(clean.apply_corrections(raw, repairs)['country_code'], 'GR')
        self.assertEqual(raw['country_code'], '')
        with self.assertRaises(ValueError):
            clean.apply_corrections(dict(raw, country_code='IT'), repairs)

    def test_recovered_snapshot_has_no_country_or_employment_gaps(self):
        import csv
        import json
        root = Path(__file__).resolve().parents[1]
        evidence = json.loads((root / 'config/synthetic_source_corrections.json').read_text())
        with (root / 'data/raw/employee_lifecycle_events.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        for raw in rows:
            fixes = [c for c in evidence['corrections'] if c['employee_id'] == raw['employee_id']]
            row = clean.curate(clean.apply_corrections(raw, fixes), date(2025, 12, 31))
            self.assertEqual(row['country_analysis_eligible'], 'true', raw['employee_id'])
            self.assertEqual(row['quality_flags'], '', raw['employee_id'])

    def row(self, **changes):
        record = dict(country_code='GR', career_level='Manager', hire_date='2025-06-30', termination_date='', termination_type='', regretted_exit='')
        record.update(changes)
        return clean.curate(record, date(2025, 12, 31))

    def test_calendar_month_end_and_leap_year(self):
        self.assertEqual(clean.anniversary(date(2024, 2, 29), 12), date(2025, 2, 28))
        self.assertEqual(clean.anniversary(date(2025, 8, 31), 6), date(2026, 2, 28))

    def test_maturity_boundary(self):
        self.assertEqual(self.row()['mature_6m_as_of'], 'true')
        self.assertEqual(self.row(hire_date='2025-07-01')['mature_6m_as_of'], 'false')

    def test_missing_country_is_not_global_exclusion(self):
        row = self.row(country_code='')
        self.assertEqual(row['valid_employment_dates'], 'true')
        self.assertEqual(row['country_analysis_eligible'], 'false')

    def test_invalid_dates_quarantined(self):
        for changes in ({'hire_date':''}, {'hire_date':'bad'}, {'termination_date':'2025-01-01'}, {'termination_date':'2026-01-01'}):
            with self.subTest(changes=changes):
                self.assertEqual(self.row(**changes)['valid_employment_dates'], 'false')

    def test_unknown_regretted_not_false(self):
        row = self.row(termination_date='2025-09-01', termination_type='Voluntary')
        self.assertEqual(row['regretted_classification'], 'unknown')

    def test_mapping_preserves_original(self):
        row = self.row(country_code='EL', career_level='Sr Mgmt')
        self.assertEqual((row['country_code'], row['country_code_original']), ('GR', 'EL'))
        self.assertEqual(row['career_level_original'], 'Sr Mgmt')
        self.assertIn('seniority_mapping_assumed', row['quality_flags'])

    def test_departure_without_date_blocks_employment_metrics(self):
        for changes in ({'regretted_exit':'true'}, {'termination_type':'Voluntary'}):
            with self.subTest(changes=changes):
                row = self.row(**changes)
                self.assertEqual(row['valid_employment_dates'], 'true')
                for field in ('retention_eligible', 'headcount_eligible', 'regretted_turnover_eligible'):
                    self.assertEqual(row[field], 'false')
                self.assertEqual(row['regretted_classification'], 'conflict')

    def test_type_conflict_only_blocks_regretted_metric(self):
        row = self.row(termination_date='2025-09-01', termination_type='Involuntary', regretted_exit='true')
        self.assertEqual(row['retention_eligible'], 'true')
        self.assertEqual(row['headcount_eligible'], 'true')
        self.assertEqual(row['regretted_turnover_eligible'], 'false')

    def test_unknown_is_not_contradiction(self):
        row = self.row(termination_date='2025-09-01', termination_type='Voluntary')
        self.assertEqual(row['regretted_classification'], 'unknown')
        self.assertEqual(row['regretted_turnover_eligible'], 'true')


if __name__ == '__main__':
    unittest.main()
