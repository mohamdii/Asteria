import importlib.util
import unittest
from datetime import date
from pathlib import Path

from asteria.quality import cleaning as clean


class CleaningTests(unittest.TestCase):
    def test_cleaning_uses_only_supplied_raw_files(self):
        import contextlib
        import csv
        import io
        import json
        import shutil
        import tempfile
        from unittest.mock import patch
        original_root = clean.ROOT
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(original_root / 'data/raw', root / 'data/raw')
            with patch.object(clean, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                clean.main()
                output = root / 'data/curated'
                summary = json.loads((output / 'quality_summary.json').read_text())
                self.assertEqual(summary['cleaning_policy'], 'conservative_supplied_data')
                self.assertEqual(summary['issues']['missing_or_unknown_country'], 9)
                self.assertEqual(summary['employment_date_quarantine'], 10)
                with (output / 'employee_lifecycle_curated.csv').open(newline='', encoding='utf-8') as stream:
                    records = {r['employee_id']: r for r in csv.DictReader(stream)}
                self.assertEqual(records['ACP000120']['country_code'], '')
                self.assertEqual(records['ACP000073']['country_code'], 'GR')
                self.assertEqual(records['ACP000159']['hire_date'], '')

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
