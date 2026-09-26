import sqlite3
import unittest
from pathlib import Path

class SqlReportingTests(unittest.TestCase):
    def test_zero_eligible_retention_is_unavailable(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript((Path(__file__).resolve().parents[1]/'sql/reporting.sql').read_text(encoding='utf-8-sig'))
            db.execute("INSERT INTO objective VALUES ('new_hire_6m',0.86,NULL)")
            db.execute("INSERT INTO audit VALUES ('new_hire_6m','a',NULL,NULL,'2025','pending',0)")
            self.assertEqual(db.execute('SELECT rate,target_status FROM kpis').fetchone(),(None,'unavailable'))

    def test_turnover_uses_employee_days_and_unknown_upper_bound(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript((Path(__file__).resolve().parents[1]/'sql/reporting.sql').read_text(encoding='utf-8-sig'))
            db.execute("INSERT INTO objective VALUES ('regretted_turnover',0.75,10)")
            db.execute("INSERT INTO audit VALUES ('regretted_turnover','a',NULL,NULL,'2025','confirmed_regretted_departure',10)")
            db.execute("INSERT INTO audit VALUES ('regretted_turnover','b',NULL,NULL,'2025','potentially_regretted_unknown',10)")
            self.assertEqual(db.execute('SELECT denominator,rate,classification_upper_rate,target_status FROM kpis').fetchone(),(2,0.5,1,'uncertain_due_to_classification'))
