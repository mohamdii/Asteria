"""Build an offline interactive dashboard from reconciled SQL views."""
import json
import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    report=json.loads((ROOT/'analysis/sql_reporting.json').read_text())
    if report['reconciliation']!='passed': raise ValueError('SQL reconciliation required')
    report['associations']=json.loads((ROOT/'analysis/association_analysis.json').read_text())
    report['data_quality']=json.loads((ROOT/'data/curated/quality_summary.json').read_text())
    if report['data_quality']['cleaning_policy'] != 'conservative_supplied_data':
        raise ValueError('Submission dashboard requires conservative supplied-data curation')
    with sqlite3.connect(ROOT/'analysis/reporting.sqlite') as db:
        db.row_factory=sqlite3.Row
        report['sources']=[dict(r) for r in db.execute('SELECT * FROM input_lineage ORDER BY path')]
    payload=json.dumps(report,ensure_ascii=True).replace('<','\\u003c')
    html=(ROOT/'dashboard/template.html').read_text(encoding='utf-8-sig').replace('__DATA__',payload)
    (ROOT/'analysis/dashboard.html').write_text(html,encoding='utf-8')
    print('Built analysis/dashboard.html')
if __name__=='__main__': main()
