"""Download/replay the reviewed list of Eurostat PDF release candidates."""
import calendar
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from asteria.paths import ROOT
FOLDER = ROOT/'data/external/historical_pdfs'
COUNTRIES = {'Greece':'GR','Ireland':'IE','Italy':'IT','Poland':'PL','Romania':'RO','Bulgaria':'BG'}


def parse_pages(pages, meta):
    match = re.search(r'\b(\d{1,2}\s+[A-Za-z]+\s+20\d{2})\b', pages[0])
    if not match:
        raise ValueError('Missing publication date')
    released = datetime.strptime(match[1], '%d %B %Y').date().isoformat()
    if released != meta['reported_release_date']:
        raise ValueError('Publication date mismatch')
    vacancy = meta['indicator'] == 'vacancies'
    title = 'Job vacancy rates by main economic activity branches' if vacancy else 'Seasonally adjusted unemployment, totals'
    found = [(i, t) for i, t in enumerate(pages) if title in t]
    if len(found) != 1:
        raise ValueError('Expected exactly one target table page')
    index, table = found[0]
    table = table[table.index(title):]
    if vacancy:
        if 'section B to F' not in table or 'not seasonally adjusted' not in table:
            raise ValueError('Wrong vacancy series')
        header = next(line for line in table.splitlines() if len(re.findall(r'20\d{2}Q[1-4]', line)) == 10)
        keys = re.findall(r'20\d{2}Q[1-4]', header)
        periods = [(int(k[:4]), int(k[-1])*3) for k in keys[:5]]
        if keys[:5] != keys[5:]:
            raise ValueError('Mismatched sector period headers')
    else:
        if 'Rates (%)' not in table:
            raise ValueError('Rate unit missing')
        pattern = r'\b([A-Za-z]{3,4})\s+(\d{2})\b'
        header = next(line for line in table.splitlines() if len(re.findall(pattern, line)) == 10)
        keys = re.findall(pattern, header)
        if keys[:5] != keys[5:]:
            raise ValueError('Mismatched rate/count headers')
        periods = [(2000+int(y), datetime.strptime(m[:3], '%b').month) for m,y in keys[:5]]
    rows = []; seen = set()
    for line in table.splitlines():
        match = re.match(r'\s*(Greece|Ireland|Italy|Poland|Romania|Bulgaria)(\*?)\s+(.+)', line)
        if not match:
            continue
        country, flag, values = match.groups()
        if country in seen:
            raise ValueError('Duplicate country row')
        seen.add(country)
        cells = re.split(r'\s{2,}', values.strip())
        if len(cells) != 10:
            raise ValueError('Unexpected table width: '+country)
        for (year, month), value in zip(periods, cells[:5]):
            if not re.fullmatch(r'(\d+(\.\d+)?\*?|:)', value):
                raise ValueError('Unrecognized value: '+value)
            end = f'{year}-{month:02}-{calendar.monthrange(year,month)[1]}'
            if end > released:
                raise ValueError('Reference period after release')
            rows.append(dict(country=COUNTRIES[country], indicator='vacancies_bf_supplementary' if vacancy else 'unemployment',
                value=None if value==':' else float(value.rstrip('*')), source_value_text=value,
                source_flags='missing' if value==':' else ('release_footnote' if flag or '*' in value else ''),
                period_start=f'{year}-{month-2 if vacancy else month:02}-01', period_end=end,
                frequency='Q' if vacancy else 'M', unit='percent_total_posts' if vacancy else 'percent_labour_force',
                sector='B-F' if vacancy else '', seasonal_adjustment='NSA' if vacancy else 'SA',
                available_on=released, vintage_id='Eurostat-'+released, vintage_verified=True,
                evidence_url=meta['url'], availability_basis='dated_release', source_file=meta['file'],
                source_sha256=meta['sha256'], source_page=index+1))
    if len(seen) != 6:
        raise ValueError('Missing country rows')
    return rows


def main():
    FOLDER.mkdir(exist_ok=True)
    manifest_path = FOLDER/'manifest.json'
    sys.path.insert(0,str(ROOT/'.tools/pdf'))
    from pypdf import PdfReader
    observations = []
    manifest = json.loads(manifest_path.read_text())
    for meta in manifest:
        raw = (FOLDER/meta['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta['sha256']:
            raise ValueError('PDF hash mismatch')
        reader = PdfReader(io.BytesIO(raw))
        # Only target table pages require layout extraction (avoid rotated charts).
        pages = []
        for page in reader.pages:
            plain = page.extract_text()
            pages.append(page.extract_text(extraction_mode='layout') if 'main economic activity branches' in plain or 'Seasonally adjusted unemployment, totals' in plain else plain)
        observations.extend(parse_pages(pages, meta))
    (FOLDER/'canonical_observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    print(json.dumps(dict(releases=len(manifest),cells=len(observations),non_null=sum(r['value'] is not None for r in observations))))
    return observations


if __name__ == '__main__':
    main()
