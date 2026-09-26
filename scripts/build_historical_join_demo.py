"""Offline evidence extraction and explicitly partial workforce join."""
import calendar
import csv
import json
import hashlib
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from clean_assessment import ROOT, write_csv
from temporal_join import select_observation


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None
    def handle_starttag(self, tag, attrs):
        if tag=='tr': self.row=[]
        if tag in ('td','th') and self.row is not None: self.cell=[]
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row)
            self.row=None


def main():
    folder=ROOT/'data/external/historical_releases'
    manifest=json.loads((folder/'manifest.json').read_text())
    for item in manifest:
        if item['status']=='downloaded' and hashlib.sha256((folder/item['file']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Historical evidence hash mismatch: '+item['file'])
    urls={r['file']:r['url'] for r in manifest}
    parser=Tables()
    parser.feed((folder/'unemployment_2024_03_01.html').read_text(encoding='utf-8'))
    countries={'Greece':'GR','Romania':'RO','Poland':'PL','Italy':'IT','Ireland':'IE','Bulgaria':'BG'}
    periods=['2023-01','2023-10','2023-11','2023-12','2024-01']
    observations=[]
    seen=set()
    for cells in parser.rows:
        if not cells or cells[0] not in countries or cells[0] in seen: continue
        if len(cells)!=11: raise ValueError('Unexpected unemployment table structure')
        seen.add(cells[0])
        for period,value in zip(periods,cells[1:6]):
            year,month=map(int,period.split('-'))
            observations.append(dict(country=countries[cells[0]],indicator='unemployment',value=float(value),
                period_start=period+'-01',period_end=f'{period}-{calendar.monthrange(year,month)[1]}',frequency='M',
                unit='percent_labour_force',seasonal_adjustment='SA',available_on='2024-03-01',
                vintage_id='Eurostat-2024-03-01',vintage_verified=True,evidence_url=urls['unemployment_2024_03_01.html']))
    if len(observations)!=30: raise ValueError('Expected six countries and five periods')
    wb=json.loads((folder/'wdi_cpi_2024_03.json').read_text())
    if wb['pages']!=1: raise ValueError('Unprocessed archive pages')
    archive_rows=wb['source']['data']
    with (ROOT/'data/curated/employee_lifecycle_curated.csv').open(newline='',encoding='utf-8') as f:
        employees=list(csv.DictReader(f))
    joined=[]
    for employee in employees:
        result={'status':'invalid_or_excluded_employment','observation':None}
        if employee['retention_eligible']=='true':
            result=select_observation(observations,employee['country_code'],'unemployment',date.fromisoformat(employee['hire_date']))
        observation=result['observation'] or {}
        joined.append(dict(employee_id=employee['employee_id'],country=employee['country_code'],cutoff=employee['hire_date'],
            join_status=result['status'],value=observation.get('value',''),period_end=observation.get('period_end',''),
            available_on=observation.get('available_on',''),vintage_id=observation.get('vintage_id',''),age_days=result.get('age_days','')))
    (folder/'verified_unemployment_observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
    write_csv(ROOT/'analysis/historical_unemployment_join_demo.csv',joined,list(joined[0]))
    summary=dict(scope='Partial demonstration using ONE Eurostat release, not full historical coverage',
                 unemployment_observations=len(observations),wb_archive_cells=len(archive_rows),
                 wb_nonnull_cells=sum(r['value'] is not None for r in archive_rows),
                 wb_strict_join_status='not_joined_month_only_vintage_requires_daily_availability_policy_or_evidence',
                 vacancy_strict_join_status='not_joined_release_sector_dimensions_do_not_match_B-N',
                 employee_join_counts=dict(Counter(r['join_status'] for r in joined)))
    (ROOT/'analysis/historical_evidence_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
