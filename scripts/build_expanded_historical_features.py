"""Replay archived values, retain evidence and expose partial match coverage."""
import calendar
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime
from build_historical_join_demo import Tables
from clean_assessment import ROOT, anniversary, write_csv
from expand_historical_coverage import plain
from temporal_join import select_observation

COUNTRIES={'Greece':'GR','Romania':'RO','Poland':'PL','Italy':'IT','Ireland':'IE','Bulgaria':'BG'}
ISO3={'GRC':'GR','ROU':'RO','POL':'PL','ITA':'IT','IRL':'IE','BGR':'BG'}
INDICATORS=('unemployment','inflation','vacancies','vacancies_bf_supplementary')
VACANCY_POLICY = {
    'vacancies': {'sector': 'B-N', 'analytical_role': 'preferred'},
    'vacancies_bf_supplementary': {'sector': 'B-F', 'analytical_role': 'supplementary'},
}


def vacancies(raw,meta):
    text=plain(raw)
    match=re.search(r'Euro indicators\s+(\d{1,2} [A-Za-z]+ 20\d{2})\s+Next release:',text)
    if not match: raise ValueError('Publication date missing')
    released=datetime.strptime(match[1],'%d %B %Y').date()
    parser=Tables(); parser.feed(raw.decode('utf-8'))
    start=next(i for i,r in enumerate(parser.rows) if r and 'main economic activity branches' in r[0])
    rows=parser.rows[start:]
    if 'B to F' not in ' '.join(rows[1]): raise ValueError('Sector definition mismatch')
    periods=[c for c in rows[2] if c][:5]
    if len(periods)!=5 or any(not re.fullmatch(r'20\d{2}Q[1-4]',p) for p in periods): raise ValueError('Quarter header mismatch')
    result=[]; seen=set()
    for cells in rows[3:]:
        if len(seen)==6: break
        country=cells[0].rstrip('*').strip() if cells else ''
        if country not in COUNTRIES: continue
        if country in seen or len(cells)!=11: raise ValueError('Unexpected sector row')
        seen.add(country)
        for period,value in zip(periods,cells[1:6]):
            if value==':': continue
            if not re.fullmatch(r'\d+(\.\d+)?\*?',value): raise ValueError('Unknown vacancy flag/value')
            year,q=int(period[:4]),int(period[-1]); month=q*3
            result.append(dict(country=COUNTRIES[country],indicator='vacancies_bf_supplementary',value=float(value.rstrip('*')),
                source_value_text=value,source_flags='release_footnote' if '*' in value or '*' in cells[0] else '',
                period_start=f'{year}-{month-2:02}-01',period_end=f'{year}-{month:02}-{calendar.monthrange(year,month)[1]}',
                frequency='Q',unit='percent_total_posts',sector='B-F',seasonal_adjustment='NSA',available_on=str(released),
                vintage_id='Eurostat-'+str(released),vintage_verified=True,evidence_url=meta['url'],availability_basis='dated_release',
                source_file=meta['file'],source_sha256=meta['sha256']))
    if len(seen)!=6: raise ValueError('Missing sector country rows')
    return result


def unemployment(raw, meta):
    text=plain(raw)
    match=re.search(r'Euro indicators\s+(\d{1,2} [A-Za-z]+ 20\d{2})\s+Next release:',text)
    if not match: raise ValueError('Publication date not found')
    released=datetime.strptime(match[1],'%d %B %Y').date()
    # Reference month comes from release overview, not filename or assumed lag.
    match=re.search(r'In ([A-Za-z]+) (20\d{2}), the euro area',text)
    if not match: raise ValueError('Reference month not found')
    reference=datetime.strptime(' '.join(match.groups()),'%B %Y').date()
    periods=[anniversary(reference,-12)]+[anniversary(reference,-i) for i in (3,2,1,0)]
    parser=Tables(); parser.feed(raw.decode('utf-8'))
    start=next(i for i,r in enumerate(parser.rows) if r and 'Seasonally adjusted unemployment, totals' in r[0])
    rows=parser.rows[start:]
    month_row=next([c for c in r if c] for r in rows[:5] if len([c for c in r if c])==10)
    for observed,expected in zip(month_row[:5],periods):
        if not observed.lower().startswith(expected.strftime('%b').lower()):
            raise ValueError('Unexpected rate-column month ordering')
    result=[]; seen=set()
    for cells in rows:
        if cells and 'youth' in cells[0].lower(): break
        country=cells[0].rstrip('*').strip() if cells else ''
        if country not in COUNTRIES: continue
        if country in seen or len(cells)!=11: raise ValueError('Unexpected country row')
        seen.add(country)
        for period,value in zip(periods,cells[1:6]):
            if value==':': continue
            if not re.fullmatch(r'\d+(\.\d+)?\*?',value): raise ValueError('Unrecognized value or flag: '+value)
            result.append(dict(country=COUNTRIES[country],indicator='unemployment',value=float(value.rstrip('*')),
                source_value_text=value,source_flags='release_footnote' if '*' in value or '*' in cells[0] else '',
                period_start=str(period),period_end=str(period.replace(day=calendar.monthrange(period.year,period.month)[1])),
                frequency='M',unit='percent_labour_force',seasonal_adjustment='SA',
                available_on=str(released),vintage_id='Eurostat-'+str(released),vintage_verified=True,
                evidence_url=meta['url'],availability_basis='dated_release',source_file=meta['file'],source_sha256=meta['sha256']))
    if len(seen)!=6: raise ValueError('Missing country rows')
    return result


def cpi(raw,meta,dates):
    payload=json.loads(raw)
    if payload['pages']!=1: raise ValueError('Unhandled pages')
    result=[]
    for row in payload['source']['data']:
        dimensions={v['concept']:v['id'] for v in row['variable']}
        version=dimensions['Version']
        if version not in dates['dates'] or row['value'] is None: continue
        year=int(dimensions['Time'][2:])
        available=dates['dates'][version]
        if f'{year}-12-31'>available: continue
        result.append(dict(country=ISO3[dimensions['Country']],indicator='inflation',value=row['value'],
            period_start=f'{year}-01-01',period_end=f'{year}-12-31',frequency='A',unit='percent_annual_change',
            available_on=available,vintage_id='WDI-'+version,vintage_verified=True,evidence_url=meta['url'],
            release_evidence_url=dates['evidence_url'],availability_basis='archive_month_mapped_to_documented_update',
            source_file=meta['file'],source_sha256=meta['sha256']))
    return result


def main():
    folder=ROOT/'data/external/historical_expanded'
    manifest=json.loads((folder/'manifest.json').read_text())
    dates=json.loads((ROOT/'config/wdi_release_dates.json').read_text())
    observations=[]; failures=[]
    if (ROOT/'data/external/historical_pdfs/manifest.json').exists():
        from replay_historical_pdfs import main as replay_pdfs
        observations.extend(replay_pdfs())
    for meta in manifest['files']:
        raw=(folder/meta['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=meta['sha256']: raise ValueError('Evidence hash mismatch')
        try:
            if meta['file'].startswith('unemployment'): observations.extend(unemployment(raw,meta))
            elif meta['file'].startswith('cpi_'): observations.extend(cpi(raw,meta,dates))
            elif meta['file'].startswith('vacancies'): observations.extend(vacancies(raw,meta))
        except (ValueError,KeyError,StopIteration) as error:
            failures.append({'file':meta['file'],'error':str(error)})
    # Same release might be reachable under more than one URL; identical observations collapse.
    unique={}
    for row in observations:
        key=(row['country'],row['indicator'],row['period_end'],row['vintage_id'])
        if key in unique and unique[key]['value']!=row['value']: raise ValueError('Conflicting release values')
        unique[key]=row
    observations=sorted(unique.values(),key=lambda r:(r['indicator'],r['country'],r['period_end'],r['available_on']))
    (folder/'canonical_observations.json').write_text(json.dumps(observations,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'data/curated/employee_lifecycle_curated.csv').open(newline='',encoding='utf-8') as f: employees=list(csv.DictReader(f))
    joined=[]
    for row in employees:
        for indicator in INDICATORS:
            selected={'status':'invalid_or_excluded_employment','observation':None}
            if row['retention_eligible']=='true': selected=select_observation(observations,row['country_code'],indicator,date.fromisoformat(row['hire_date']))
            obs=selected['observation'] or {}
            joined.append(dict(employee_id=row['employee_id'],country=row['country_code'],hire_date=row['hire_date'],indicator=indicator,
                sector=VACANCY_POLICY.get(indicator, {}).get('sector', ''),
                analytical_role=VACANCY_POLICY.get(indicator, {}).get('analytical_role', 'context'),
                join_status=selected['status'],value=obs.get('value',''),period_end=obs.get('period_end',''),
                available_on=obs.get('available_on',''),vintage_id=obs.get('vintage_id',''),availability_basis=obs.get('availability_basis',''),
                source_flags=obs.get('source_flags',''),
                evidence_url=obs.get('evidence_url',''),age_days=selected.get('age_days','')))
    write_csv(ROOT/'analysis/expanded_historical_features.csv',joined,list(joined[0]))
    summary=dict(vacancy_policy=VACANCY_POLICY, observations=dict(Counter(o['indicator'] for o in observations if o['value'] is not None)),parser_failures=failures,
        matches={i:dict(Counter(r['join_status'] for r in joined if r['indicator']==i)) for i in INDICATORS},
        workforce_rows=len(employees),scope='All curated employees; not just metric denominators. CPI archive month is mapped to documented WDI update date; not first CPI publication.')
    (ROOT/'analysis/expanded_historical_coverage.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    coverage=[]
    for indicator in INDICATORS:
        for year in range(2021,2026):
            group=[r for r in joined if r['indicator']==indicator and r['hire_date'].startswith(str(year))]
            coverage.append(dict(indicator=indicator,hire_year=year,records=len(group),matched=sum(r['join_status']=='matched' for r in group)))
    write_csv(ROOT/'analysis/historical_match_coverage_by_year.csv',coverage,list(coverage[0]))
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
