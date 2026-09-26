import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from join_metric_external import enrich

class MetricJoinTests(unittest.TestCase):
    def test_missing_context_preserves_outcome_and_pending_is_not_attempted(self):
        rows=[dict(employee_id='a',hire_date='2024-01-01',status='retained'),dict(employee_id='b',hire_date='2024-01-01',status='pending')]
        joined,_=enrich(rows,{'a':{'country_code':''},'b':{'country_code':'GR'}},[])
        self.assertEqual(len(joined),2)
        self.assertEqual(joined[0]['status'],'retained')
        self.assertEqual(joined[0]['unemployment_status'],'missing_country')
        self.assertEqual(joined[1]['unemployment_status'],'outside_metric_population')

    def test_turnover_uses_window_start_even_for_later_hire(self):
        row=dict(employee_id='a',hire_date='2025-06-01',status='no_departure_in_window',employee_days='214')
        observation=dict(country='GR',indicator='unemployment',value=9,period_end='2025-04-30',available_on='2025-05-31',vintage_id='v',vintage_verified=True,evidence_url='fixture')
        joined,_=enrich([row],{'a':{'country_code':'GR'}},[observation],'2025-01-01')
        self.assertEqual(joined[0]['unemployment_status'],'no_verified_historical_match')
        self.assertEqual(joined[0]['employee_days'],'214')
        self.assertEqual(joined[0]['external_cutoff'],'2025-01-01')
