import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from replay_historical_pdfs import main, parse_pages
from temporal_join import select_observation


class HistoricalPdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = main()

    def test_source_cells_and_missing_values(self):
        self.assertEqual(len(self.rows),360)
        missing=[r for r in self.rows if r['value'] is None]
        self.assertEqual({r['country'] for r in missing},{'GR','IE'})
        self.assertTrue(all(r['period_end']=='2021-06-30' and r['available_on']=='2021-09-16' for r in missing))

    def test_industry_column_not_services_or_whole_economy(self):
        row=next(r for r in self.rows if r['country']=='IT' and r['available_on']=='2021-09-16' and r['period_end']=='2021-06-30')
        self.assertEqual(row['value'],1.7)
        self.assertEqual(row['sector'],'B-F')
        self.assertEqual(row['source_page'],4)

    def test_unemployment_rates_not_counts(self):
        row=next(r for r in self.rows if r['country']=='GR' and r['indicator']=='unemployment' and r['period_end']=='2022-11-30')
        self.assertEqual(row['value'],11.4)
        self.assertEqual(row['available_on'],'2023-01-09')

    def test_no_backdating_and_no_sector_substitution(self):
        self.assertEqual(select_observation([r for r in self.rows if r['available_on']=='2023-01-09'],'GR','unemployment',date(2022,12,31))['status'],'no_verified_historical_match')
        self.assertEqual(select_observation(self.rows,'GR','vacancies',date(2023,1,10))['status'],'no_verified_historical_match')
        self.assertEqual(select_observation(self.rows,'GR','unemployment',date(2023,1,10))['observation']['value'],11.4)

    def test_bad_publication_date_rejected(self):
        with self.assertRaisesRegex(ValueError,'date mismatch'):
            parse_pages(['16 September 2021'],{'reported_release_date':'2021-09-15'})

    def test_earlier_releases_are_available_only_after_publication(self):
        for released, cutoff in [('2021-07-30', date(2021,7,31)), ('2022-03-31', date(2022,4,1)), ('2021-09-01', date(2021,9,2)), ('2023-03-31', date(2023,4,1)), ('2023-06-30', date(2023,7,1))]:
            rows=[r for r in self.rows if r['available_on']==released]
            self.assertEqual(len(rows),30)
            for country in ['GR','IE','IT','PL','RO','BG']:
                self.assertEqual(select_observation(rows,country,'unemployment',date.fromisoformat(released))['status'],'no_verified_historical_match')
                self.assertEqual(select_observation(rows,country,'unemployment',cutoff)['status'],'matched')
