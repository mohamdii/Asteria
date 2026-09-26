import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_expanded_historical_features import ROOT, unemployment, cpi, vacancies


class HistoricalExtractionTests(unittest.TestCase):
    def load(self,name):
        folder=ROOT/'data/external/historical_expanded'
        return (folder/name).read_bytes(),json.loads((folder/(name+'.meta.json')).read_text())

    def test_unemployment_column_order_and_vintage(self):
        rows=unemployment(*self.load('unemployment_20240301_bp.html'))
        self.assertEqual(len(rows),30)
        poland=next(r for r in rows if r['country']=='PL' and r['period_end']=='2024-01-31')
        self.assertEqual(poland['value'],2.9)
        self.assertEqual(poland['available_on'],'2024-03-01')
        self.assertTrue(all(r['available_on']=='2024-03-01' for r in rows))

    def test_flags_preserved(self):
        rows=unemployment(*self.load('unemployment_20250731_ap.html'))
        self.assertTrue(any(r['country']=='GR' and r['source_flags']=='release_footnote' for r in rows))

    def test_cpi_without_release_mapping_not_admitted(self):
        raw,meta=self.load('cpi_202403.json')
        self.assertEqual(cpi(raw,meta,{'dates':{}}),[])
        dates=json.loads((ROOT/'config/wdi_release_dates.json').read_text())
        rows=cpi(raw,meta,dates)
        self.assertTrue(rows)
        self.assertTrue(all(r['available_on']=='2024-03-28' and r['frequency']=='A' for r in rows))

    def test_vacancy_sector_not_silently_combined(self):
        rows=vacancies(*self.load('vacancies_20240315_ap.html'))
        self.assertEqual(len(rows),30)
        self.assertTrue(all(r['sector']=='B-F' and r['indicator']=='vacancies_bf_supplementary' for r in rows))
        greece=next(r for r in rows if r['country']=='GR' and r['period_end']=='2023-12-31')
        self.assertEqual(greece['value'],2.2)
        later=vacancies(*self.load('vacancies_20240614_bp.html'))
        revised=next(r for r in later if r['country']=='GR' and r['period_end']=='2023-12-31')
        self.assertEqual(revised['value'],2.9)
