"""Coverage probe, not a production ingestion pipeline. Saves official responses."""
import csv
from http_client import fetch
import hashlib
import itertools
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
GEO = ['EL','RO','PL','IT','IE','BG']


def euro_url(code, filters):
    return BASE+code+'?'+urlencode([('lang','EN'),('sinceTimePeriod','2021'),('untilTimePeriod','2025')]+list(filters.items())+[('geo',g) for g in GEO])


REQUESTS = {
    'unemployment': euro_url('une_rt_m', {'freq':'M','s_adj':'SA','age':'TOTAL','sex':'T','unit':'PC_ACT'}),
    'vacancies': euro_url('jvs_q_nace2', {'freq':'Q','s_adj':'NSA','nace_r2':'B-N','sizeclas':'TOTAL','indic_em':'JVR'}),
    'inflation': 'https://api.worldbank.org/v2/country/GR;RO;PL;IT;IE;BG/indicator/FP.CPI.TOTL.ZG?date=2021:2025&format=json&per_page=100',
}


def main():
    out = ROOT/'data/external/coverage_probe'
    out.mkdir(parents=True, exist_ok=True)
    report, provenance = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(fetch, item) for item in REQUESTS.items()]
        for future in futures:
            try:
                name, url, raw = future.result()
            except Exception as error:
                print('FETCH FAILED:', repr(error))
                raise
            (out/(name+'.json')).write_bytes(raw)
            payload = json.loads(raw)
            provenance.append(dict(indicator=name,url=url,retrieved_at=datetime.now(timezone.utc).isoformat(),sha256=hashlib.sha256(raw).hexdigest()))
            groups = {}
            if name == 'inflation':
                if payload[0]['pages'] != 1:
                    raise ValueError('Unexpected World Bank pagination')
                for row in payload[1]:
                    groups.setdefault(row['country']['id'], {})[row['date']] = row['value']
                expected = [str(y) for y in range(2021,2026)]
            else:
                print(name, 'dimensions:', payload.get('id'), payload.get('size'))
                if not payload.get('size') or 0 in payload['size']:
                    raise ValueError('Empty dimension selection: '+name)
                dimensions = []
                for dim in payload['id']:
                    index = payload['dimension'][dim]['category']['index']
                    dimensions.append(index if isinstance(index,list) else sorted(index,key=index.get))
                values = payload.get('value', {})
                for i, coordinates in enumerate(itertools.product(*dimensions)):
                    coord = dict(zip(payload['id'], coordinates))
                    geo = 'GR' if coord['geo']=='EL' else coord['geo']
                    value = values[i] if isinstance(values,list) else values.get(str(i))
                    groups.setdefault(geo,{})[coord['time']] = value
                expected = [f'{y}-{m:02}' for y in range(2021,2026) for m in range(1,13)] if name=='unemployment' else [f'{y}-Q{q}' for y in range(2021,2026) for q in range(1,5)]
            for geo in ['GR','RO','PL','IT','IE','BG']:
                observations = groups.get(geo,{})
                missing = [p for p in expected if observations.get(p) is None]
                report.append(dict(indicator=name,country=geo,expected=len(expected),available=len(expected)-len(missing),missing=';'.join(missing)))
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'analysis/external_coverage.csv').open('w',newline='',encoding='utf-8') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(report[0]))
        writer.writeheader()
        writer.writerows(report)
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
