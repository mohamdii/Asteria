import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from temporal_join import select_observation


class TemporalJoinTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(country='GR', indicator='unemployment', value=10, period_end='2024-01-31',
                   available_on='2024-03-01', vintage_verified=True, vintage_id='fixture-v1', evidence_url='fixture://release')
        row.update(changes)
        return row

    def select(self, rows, cutoff=date(2024,3,2)):
        return select_observation(rows, 'GR', 'unemployment', cutoff)

    def test_release_day_excluded(self):
        self.assertEqual(self.select([self.row()], date(2024,3,1))['status'], 'no_verified_historical_match')
        self.assertEqual(self.select([self.row()])['status'], 'matched')

    def test_later_revision_never_replaces_historical_value(self):
        rows = [self.row(), self.row(value=11, available_on='2026-01-01', vintage_id='later')]
        self.assertEqual(self.select(rows)['observation']['value'], 10)

    def test_current_vintage_and_missing_evidence_rejected(self):
        for changes in ({'vintage_verified':False}, {'available_on':None}, {'evidence_url':''}):
            self.assertEqual(self.select([self.row(**changes)])['status'], 'no_verified_historical_match')

    def test_country_staleness_and_zero(self):
        self.assertEqual(self.select([self.row(country='IT')])['status'], 'no_verified_historical_match')
        self.assertEqual(self.select([self.row()], date(2025,1,1))['status'], 'stale')
        self.assertEqual(self.select([self.row(value=0)])['observation']['value'], 0)

    def test_ambiguous_versions_raise(self):
        with self.assertRaises(ValueError):
            self.select([self.row(), self.row(value=12)])

    def test_supplementary_vacancies_do_not_fill_preferred_gap(self):
        rows = [self.row(indicator='vacancies_bf_supplementary', value=2.2)]
        cutoff = date(2024, 3, 2)
        self.assertEqual(select_observation(rows, 'GR', 'vacancies', cutoff)['status'],
                         'no_verified_historical_match')
        self.assertEqual(select_observation(rows, 'GR', 'vacancies_bf_supplementary', cutoff)
                         ['observation']['value'], 2.2)
