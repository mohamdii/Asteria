"""Build local SQL reporting tables and reconcile them with Python metrics."""
import csv
import hashlib
import json
import math
import sqlite3
from pathlib import Path
from asteria.paths import ROOT
METRICS=('new_hire_6m','senior_hire_12m','regretted_turnover')
INDICATORS=('unemployment','inflation','vacancies','vacancies_bf_supplementary')


def main():
    output=ROOT/'analysis'; destination=output/'reporting.sqlite'
    temporary=output/'reporting.build.sqlite'
    if temporary.exists(): temporary.unlink()
    db=sqlite3.connect(temporary)
    db.row_factory=sqlite3.Row
    sources=[ROOT/'sql/reporting.sql',ROOT/'analysis/metric_external_coverage.json']
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript(sources[0].read_text(encoding='utf-8-sig'))
        summaries={}
        for metric in METRICS:
            path=output/(metric+'_summary.json'); sources.append(path)
            summary=json.loads(path.read_text()); summaries[metric]=summary
            target=summary['target'] if metric=='regretted_turnover' else summary['overall']['target']
            db.execute('INSERT INTO objective VALUES (?,?,?)',(metric,target,summary.get('calendar_days')))
            path=output/(metric+'_with_external.csv'); sources.append(path)
            with path.open(encoding='utf-8',newline='') as stream:
                for row in csv.DictReader(stream):
                    db.execute('INSERT INTO audit VALUES (?,?,?,?,?,?,?)',(metric,row['employee_id'],row['country_code'] or None,row.get('business_unit') or None,row['hire_date'][:4] or None,row['status'],int(row.get('employee_days',0))))
                    for indicator in INDICATORS:
                        def field(name): return row[indicator+'_'+name] or None
                        db.execute('INSERT INTO external_match VALUES (?,?,?,?,?,?,?,?)',(metric,row['employee_id'],indicator,field('status'),float(field('value')) if field('value') is not None else None,field('period_end'),field('available_on'),field('evidence_url')))
        coverage=json.loads((output/'metric_external_coverage.json').read_text())['metrics']
        for row in db.execute('SELECT * FROM kpis'):
            summary=summaries[row['metric']]
            if row['metric']=='regretted_turnover':
                expected=(summary['confirmed_regretted_departures'],summary['average_daily_headcount'],summary['confirmed_rate'],summary['target_status'])
                assert math.isclose(row['classification_upper_rate'],summary['classification_upper_rate'],abs_tol=1e-12)
                assert db.execute("SELECT SUM(employee_days) FROM audit WHERE metric='regretted_turnover'").fetchone()[0]==summary['employee_days']
            else:
                s=summary['overall']; expected=(s['retained'],s['eligible_hires'],s['retention_rate'],s['target_status'])
            for actual,wanted in zip((row['numerator'],row['denominator'],row['rate']),expected[:3]):
                assert actual==wanted if wanted is None else math.isclose(actual,wanted,rel_tol=1e-12,abs_tol=1e-12)
            assert row['target_status']==expected[3]
        for metric,s in coverage.items():
            assert db.execute('SELECT COUNT(*) FROM audit WHERE metric=?',(metric,)).fetchone()[0]==s['audit_rows']
            for indicator,item in s['indicators'].items():
                actual={r['status']:r['records'] for r in db.execute('SELECT status,records FROM external_coverage WHERE metric=? AND indicator=?',(metric,indicator))}
                assert actual==item['statuses']
        for path in sources:
            db.execute('INSERT INTO input_lineage VALUES (?,?)',(str(path.relative_to(ROOT)).replace('\\','/'),hashlib.sha256(path.read_bytes()).hexdigest()))
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        tables={name:[dict(r) for r in db.execute('SELECT * FROM '+name+' ORDER BY '+order)] for name,order in [('kpis','metric'),('retention_cohorts','metric,country,business_unit,hire_year'),('quality_counts','metric,status'),('external_coverage','metric,indicator,status')]}
        db.commit()
    finally:
        db.close()
    temporary.replace(destination)
    (output/'sql_reporting.json').write_text(json.dumps(dict(reconciliation='passed',reports=tables),indent=2)+'\n',encoding='utf-8')
    print('SQL reports reconciled with Python KPIs and external coverage.')


if __name__=='__main__': main()
