import sys
import unittest
from datetime import date
from pathlib import Path

from asteria.metrics.retention import classify, summarize


class RetentionTests(unittest.TestCase):
    def classify(self, **changes):
        row = dict(employee_id='test', source_csv_line=2, country_code='', business_unit='Sales',
                   hire_date='2025-06-30', termination_date='', quality_flags='', valid_employment_dates='true', retention_eligible='true')
        row.update(changes)
        return classify(row, date(2025, 12, 31), date(2021, 1, 1), date(2025, 12, 31))

    def test_anniversary_departure_boundary(self):
        self.assertEqual(self.classify(termination_date='2025-12-30')['status'], 'retained')
        self.assertEqual(self.classify(termination_date='2025-12-29')['status'], 'left_before_milestone')

    def test_immature_early_departure_still_pending(self):
        self.assertEqual(self.classify(hire_date='2025-10-01', termination_date='2025-11-01')['status'], 'pending_observation')

    def test_outside_period_and_invalid(self):
        self.assertEqual(self.classify(hire_date='2020-12-31')['status'], 'outside_objective_hire_period')
        self.assertEqual(self.classify(hire_date='', valid_employment_dates='false')['status'], 'excluded_invalid_dates')

    def test_missing_country_does_not_exclude(self):
        self.assertEqual(self.classify()['status'], 'retained')

    def test_contradiction_excluded_from_denominator(self):
        row = self.classify(retention_eligible='false')
        self.assertEqual(row['status'], 'excluded_contradiction')
        result = summarize([row], .86)
        self.assertEqual(result['eligible_hires'], 0)
        self.assertEqual(result['excluded_contradiction'], 1)
        self.assertIsNone(result['retention_rate'])

    def test_exact_target_and_empty_denominator(self):
        rows = [{'status': 'retained'}]*86 + [{'status':'left_before_milestone'}]*14 + [{'status':'pending_observation'}]*20
        result = summarize(rows, .86)
        self.assertEqual(result['eligible_hires'], 100)
        self.assertEqual(result['retention_rate'], .86)
        self.assertEqual(result['target_status'], 'met')
        self.assertIsNone(summarize([], .86)['retention_rate'])


if __name__ == '__main__':
    unittest.main()
