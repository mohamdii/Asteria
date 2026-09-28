import sys,unittest
from pathlib import Path
from asteria.reporting.associations import correlation,analyze
class AssociationTests(unittest.TestCase):
 def test_correlation_boundaries(self):
  self.assertAlmostEqual(correlation([(1,2),(2,4),(3,6)]),1)
  self.assertAlmostEqual(correlation([(1,6),(2,4),(3,2)]),-1)
  self.assertIsNone(correlation([(1,2),(1,3),(1,4)]))
  self.assertIsNone(correlation([(1,2)]))
 def test_repeated_evidence_not_counted_as_new_observations(self):
  row=dict(in_metric_population='true',status='retained',country_code='GR',business_unit='Digital',hire_year='2023',hire_date='2023-04-10',unemployment_status='matched',unemployment_value='10',unemployment_period_end='2023-02-28',unemployment_vintage_id='v1',unemployment_age_days='41')
  result=analyze([row,dict(row,status='left_before_milestone')],'unemployment')
  self.assertEqual(result['matched']['rate'],0.5)
  self.assertEqual(result['distinct_country_reference_periods'],1)
  self.assertEqual(result['cohort_count'],1)
  self.assertIsNone(result['min10_cohort_pearson'])
