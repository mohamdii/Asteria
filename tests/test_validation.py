import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_assessment import ROOT, read_csv, validate_record


class ValidationTests(unittest.TestCase):
    def rules(self, dataset, **changes):
        row = read_csv(ROOT / 'data/raw' / (dataset + '.csv'))[0]
        row.update(changes)
        schema = [c for c in read_csv(ROOT / 'data/raw/data_dictionary.csv') if c['dataset'] == dataset]
        return {f['rule'] for f in validate_record(row, schema, date(2025, 12, 31))}

    def test_every_nonnullable_field_rejects_whitespace(self):
        for col in read_csv(ROOT / 'data/raw/data_dictionary.csv'):
            if col['nullable'] == 'no':
                with self.subTest(field=col['column_name']):
                    self.assertIn('required_value_missing', self.rules(col['dataset'], **{col['column_name']: '  '}))

    def test_bad_categories_and_boolean(self):
        for field in ('employment_type', 'career_level', 'termination_type', 'country_code'):
            with self.subTest(field=field):
                self.assertIn('unrecognized_value', self.rules('employee_lifecycle_events', **{field: 'unexpected'}))
        self.assertIn('invalid_boolean', self.rules('employee_lifecycle_events', regretted_exit='yes'))

    def test_dates(self):
        self.assertIn('invalid_iso_date', self.rules('retention_objectives', effective_from='2025-02-30'))
        self.assertIn('invalid_iso_date', self.rules('retention_objectives', effective_from='20250101'))
        self.assertIn('effective_dates_reversed', self.rules('retention_objectives', effective_from='2026-01-01'))
        self.assertNotIn('effective_dates_reversed', self.rules('retention_objectives', effective_from='2025-12-31'))

    def test_target_range_and_nonfinite(self):
        for value in ('-0.1', '1.1'):
            self.assertIn('proportion_out_of_range', self.rules('retention_objectives', target_value=value))
        for value in ('NaN', 'Infinity', 'abc'):
            self.assertIn('invalid_finite_decimal', self.rules('retention_objectives', target_value=value))
        for value in ('0', '1'):
            self.assertNotIn('proportion_out_of_range', self.rules('retention_objectives', target_value=value))

    def test_contradiction_detected(self):
        self.assertIn('regretted_without_departure', self.rules('employee_lifecycle_events', termination_date='', regretted_exit='true'))
        self.assertIn('termination_type_without_departure', self.rules('employee_lifecycle_events', termination_date='', termination_type='Voluntary'))

    def test_nullable_blanks_and_aliases_accepted(self):
        self.assertEqual(self.rules('employee_lifecycle_events', country_code='', termination_date='', termination_type='', regretted_exit=''), set())
        self.assertEqual(self.rules('employee_lifecycle_events', country_code='EL', career_level='Sr Mgmt'), set())

    def test_missing_column(self):
        schema = [{'column_name':'employment_type', 'logical_type':'string', 'nullable':'no'}]
        self.assertEqual(validate_record({}, schema, date(2025,12,31))[0]['rule'], 'missing_column_or_cell')


if __name__ == '__main__':
    unittest.main()
