import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from calculate_regretted_turnover import calculate


class TurnoverTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(employee_id='test', source_csv_line=2, hire_date='2020-01-01', termination_date='',
                   termination_type='', regretted_exit='', quality_flags='', valid_employment_dates='true', regretted_turnover_eligible='true')
        row.update(changes)
        return row

    def run_metric(self, rows, end=date(2025,12,31), target=.075):
        return calculate(rows, end, target)

    def test_inclusive_window_boundaries(self):
        summary, audit, daily = self.run_metric([self.row(termination_date=d, termination_type='Voluntary', regretted_exit='true') for d in ('2024-12-31','2025-01-01','2025-12-31')])
        self.assertEqual([r['employee_days'] for r in audit], [0,1,365])
        self.assertEqual(summary['confirmed_regretted_departures'], 2)
        self.assertEqual(daily[0]['headcount'], 2)
        self.assertEqual(daily[-1]['headcount'], 1)

    def test_unknowns_and_nonvoluntary_departures(self):
        rows = [self.row(termination_date='2025-12-31', termination_type=t, regretted_exit=r) for t,r in
                [('Voluntary','true'),('Voluntary',''),('','true'),('',''),('Involuntary',''),('Voluntary','false')]]
        summary, _, _ = self.run_metric(rows)
        self.assertEqual(summary['average_daily_headcount'], 6)
        self.assertEqual(summary['confirmed_regretted_departures'], 1)
        self.assertEqual(summary['potentially_regretted_unknown_departures'], 3)
        self.assertAlmostEqual(summary['classification_upper_rate'], 4/6)

    def test_exclusions_remove_both_sides(self):
        rows = [self.row(termination_date='2025-12-31', termination_type='Voluntary', regretted_exit='true', **flags)
                for flags in ({'valid_employment_dates':'false'}, {'regretted_turnover_eligible':'false'})]
        summary, _, _ = self.run_metric(rows)
        self.assertEqual(summary['employee_days'], 0)
        self.assertEqual(summary['confirmed_regretted_departures'], 0)
        self.assertIsNone(summary['confirmed_rate'])

    def test_leap_year_and_partial_employment(self):
        summary, audit, _ = self.run_metric([self.row(hire_date='2024-02-29', termination_date='2024-03-01')], end=date(2024,12,31))
        self.assertEqual(summary['calendar_days'], 366)
        self.assertEqual(audit[0]['employee_days'], 2)
        self.assertEqual(summary['average_daily_headcount'], 2/366)

    def test_threshold_and_uncertainty(self):
        rows = [self.row(termination_date='2025-12-31', termination_type='Voluntary', regretted_exit='true')] + [self.row() for _ in range(9)]
        self.assertEqual(self.run_metric(rows, target=.1)[0]['target_status'], 'met_under_classification_scenarios')
        rows[1] = self.row(termination_date='2025-12-31', termination_type='Voluntary')
        self.assertEqual(self.run_metric(rows, target=.1)[0]['target_status'], 'uncertain_due_to_classification')

    def test_empty_population(self):
        self.assertEqual(self.run_metric([])[0]['target_status'], 'unavailable')
