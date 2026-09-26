"""Retrieve dated release evidence; preserves raw material without inventing vintages."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from check_external_coverage import ROOT
from http_client import fetch

SOURCES = {
 'unemployment_2024_03_01.html': 'https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-01032024-bp',
 'vacancies_2024_06_14.html': 'https://ec.europa.eu/eurostat/web/products-euro-indicators/w/3-14062024-bp',
 'wdi_cpi_2024_03.json': 'https://api.worldbank.org/v2/sources/57/country/GRC;ROU;POL;ITA;IRL;BGR/series/FP.CPI.TOTL.ZG/time/YR2020;YR2021;YR2022;YR2023/version/202403/data?format=json&per_page=1000',
 'wdi_versions.json': 'https://api.worldbank.org/v2/sources/57/version/data?format=json&per_page=1000',
}


def main():
    out = ROOT/'data/external/historical_releases'
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch,item): item for item in SOURCES.items()}
        for future, (name,url) in futures.items():
            try:
                _, _, payload = future.result()
                (out/name).write_bytes(payload)
                if name.endswith('.json'):
                    decoded = json.loads(payload)
                    if 'source' not in decoded:
                        raise ValueError('Not an archive dataset response')
                manifest.append(dict(file=name,url=url,sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),retrieved_at=datetime.now(timezone.utc).isoformat(),status='downloaded'))
            except Exception as error:
                manifest.append(dict(file=name,url=url,status='failed',error=str(error)))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    main()
