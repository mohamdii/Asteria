"""Explicit online acquisition of reviewed PDF releases."""
import hashlib
import json
from datetime import datetime, timezone
from asteria.paths import ROOT
from asteria.acquisition.http_client import get_bytes

FOLDER=ROOT/'data/external/historical_pdfs'

def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    manifest_path=FOLDER/'manifest.json'
    previous = {r['file']:r for r in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}
    records = []
    for item in json.loads((ROOT/'config/historical_pdf_candidates.json').read_text())['sources']:
        name = item['indicator']+'_'+item['reported_release_date']+'.pdf'
        path = FOLDER/name
        if name in previous and path.exists():
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != previous[name]['sha256']:
                raise ValueError('Cached PDF hash mismatch')
            record = previous[name]
        else:
            raw = get_bytes(item['url'])
            if not raw.startswith(b'%PDF'):
                raise ValueError('Expected PDF')
            path.write_bytes(raw)
            record = dict(item, file=name, sha256=hashlib.sha256(raw).hexdigest(), retrieved_at=datetime.now(timezone.utc).isoformat())
        records.append(record)
        manifest_path.write_text(json.dumps(records,indent=2)+'\n')

if __name__ == "__main__":
    main()
