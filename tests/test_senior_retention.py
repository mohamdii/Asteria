import sys
import unittest
from datetime import date
from pathlib import Path
from asteria.metrics.senior_retention import calculate


class SeniorRetentionTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(employee_id='test', source_csv_line=2, country_code='GR', business_unit='Sales',
                   hire_date='2024-12-31', termination_date='', quality_flags='', valid_employment_dates='true',
                   retention_eligible='true', career_level='Senior Leader', career_level_original='Senior Leader')
        row.update(changes)
        return row

    def run_metric(self, rows, **kwargs):
        return calculate(rows, date(2025,12,31), date(2021,1,1), date(2025,12,31), .9, **kwargs)

    def test_twelve_month_boundary_and_pending_early_exit(self):
        audit, summary = self.run_metric([
            self.row(termination_date='2025-12-31'),
            self.row(termination_date='2025-12-30'),
            self.row(hire_date='2025-01-01', termination_date='2025-02-01')])
        self.assertEqual([r['status'] for r in audit], ['retained','left_before_milestone','pending_observation'])
        self.assertEqual(summary['retention_rate'], .5)

    def test_seniority_and_sensitivity(self):
        rows = [self.row(), self.row(career_level_original='Sr Mgmt', termination_date='2025-02-01'),
                self.row(career_level='Manager', career_level_original='Manager')]
        self.assertEqual(self.run_metric(rows)[1]['eligible_hires'], 2)
        strict = self.run_metric(rows, include_mapped=False)[1]
        self.assertEqual(strict['eligible_hires'], 1)
        self.assertEqual(strict['retention_rate'], 1)

    def test_exclusions_and_zero_denominator(self):
        _, summary = self.run_metric([self.row(valid_employment_dates='false'), self.row(retention_eligible='false'),
                                      self.row(hire_date='2020-01-01')])
        self.assertEqual(summary['excluded_invalid_dates'], 1)
        self.assertEqual(summary['excluded_contradiction'], 1)
        self.assertEqual(summary['outside_objective_hire_period'], 1)
        self.assertIsNone(summary['retention_rate'])

    def test_leap_day_anniversary(self):
        audit, _ = self.run_metric([self.row(hire_date='2024-02-29', termination_date='2025-02-28')])
        self.assertEqual(audit[0]['twelve_month_anniversary'], '2025-02-28')
        self.assertEqual(audit[0]['status'], 'retained')
