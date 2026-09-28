"""Expand saved historical evidence with bounded, resumable official requests."""
import hashlib
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from asteria.external.html import plain
from asteria.paths import ROOT
from asteria.acquisition.http_client import fetch

OUT = ROOT/'data/external/historical_expanded'


def save(name, url):
    path=OUT/name
    meta=OUT/(name+'.meta.json')
    if path.exists() and meta.exists():
        record=json.loads(meta.read_text())
        if hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']:
            return path.read_bytes(), record
    _,_,raw=fetch((name,url))
    if name.endswith('.json'):
        payload=json.loads(raw)
        if 'source' not in payload or payload.get('pages')!=1:
            raise ValueError('Archive error response or unhandled pagination')
    path.write_bytes(raw)
    record=dict(file=name,url=url,sha256=hashlib.sha256(raw).hexdigest(),retrieved_at=datetime.now(timezone.utc).isoformat())
    meta.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return raw,record


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    existing=json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else {'files':[],'errors':[]}
    manifest,errors=existing['files'],existing['errors']
    versions=json.loads((ROOT/'data/external/historical_releases/wdi_versions.json').read_text())['source'][0]['concept'][0]['variable']
    versions=[v['id'] for v in versions if '202001'<=v['id']<='202512']
    def archive(version):
        url=f'https://api.worldbank.org/v2/sources/57/country/GRC;ROU;POL;ITA;IRL;BGR/series/FP.CPI.TOTL.ZG/time/YR2018;YR2019;YR2020;YR2021;YR2022;YR2023;YR2024;YR2025/version/{version}/data?format=json&per_page=1000'
        return save('cpi_'+version+'.json',url)[1]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(archive,v):v for v in versions}
        for future in as_completed(futures):
            try: manifest.append(future.result())
            except Exception as error: errors.append(dict(source='CPI',version=futures[future],error=str(error)))
    print('CPI archive versions:',len(versions),flush=True)
    # Follow source-stated next-release dates. Verify each page contains unemployment.
    current=datetime.fromisoformat(sys.argv[1]) if len(sys.argv)>1 else datetime(2024,3,1)
    kind=sys.argv[2] if len(sys.argv)>2 else 'unemployment'
    expected='Job vacancy rates' if kind=='vacancies' else 'Seasonally adjusted unemployment'
    seen=set()
    while current.year<=2025 and current not in seen:
        seen.add(current)
        raw=None
        for suffix in ('ap','bp'):
            url='https://ec.europa.eu/eurostat/en/web/products-euro-indicators/w/3-'+current.strftime('%d%m%Y')+'-'+suffix
            try:
                candidate,meta=save(kind+'_'+current.strftime('%Y%m%d')+'_'+suffix+'.html',url)
                text=plain(candidate)
                if expected not in text:
                    raise ValueError('Not a matching unemployment release')
                raw=candidate
                manifest.append(meta)
                break
            except Exception: continue
        if raw is None:
            errors.append(dict(source=kind,date=str(current.date()),error='No matching ap/bp release'))
            break
        print(kind+' release:',current.date(),flush=True)
        match=re.search(r'Next release:\s*(\d{1,2}\s+[A-Za-z]+\s+20\d{2})',text)
        if not match:
            errors.append(dict(source='unemployment',date=str(current.date()),error='Next release date missing'))
            break
        current=datetime.strptime(match[1],'%d %B %Y')
    manifest=list({r['file']:r for r in manifest}.values())
    (OUT/'manifest.json').write_text(json.dumps({'files':sorted(manifest,key=lambda r:r['file']),'errors':errors},indent=2)+'\n',encoding='utf-8')
    print('Complete:',len(manifest),'files;',len(errors),'reported gaps',flush=True)


if __name__=='__main__': main()
