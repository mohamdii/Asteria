"""Offline assessment replay; optionally verify byte-identical repeated builds."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STAGES=['validate_assessment.py','calculate_retention.py','calculate_senior_retention.py',
        'calculate_regretted_turnover.py','build_expanded_historical_features.py',
        'report_external_coverage.py','join_metric_external.py','build_sql_reporting.py','analyze_associations.py','build_dashboard.py']
OUTPUT_PATTERNS=['analysis/association_analysis.json','analysis/association_analysis.md','analysis/dashboard.html','analysis/reporting.sqlite','analysis/sql_reporting.json','analysis/schema_validation.json',
    'data/curated/*.csv','data/curated/*.json','analysis/new_hire_6m_*',
    'analysis/senior_hire_12m_*','analysis/regretted_turnover_*',
    'analysis/expanded_historical_*','analysis/historical_match_coverage_by_year.csv',
    'analysis/external_coverage_report.*','analysis/metric_external_coverage.*',
    'data/external/historical_pdfs/canonical_observations.json',
    'data/external/historical_expanded/canonical_observations.json']


def hashes(paths):
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths)) if p.is_file()}


def outputs():
    return hashes(p for pattern in OUTPUT_PATTERNS for p in ROOT.glob(pattern))


def run(command):
    print('Running: '+' '.join(command),flush=True)
    completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if completed.returncode:
        raise RuntimeError(completed.stdout+'\n'+completed.stderr)


def build():
    for script in STAGES:
        run([sys.executable,'scripts/'+script])
    run([sys.executable,'-m','unittest','discover','-s','tests'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-reproducibility',action='store_true',help='Build twice and compare every pipeline output hash')
    args=parser.parse_args()
    marker=ROOT/'analysis/pipeline_manifest.json'
    if marker.exists(): marker.unlink()  # A failed run must not retain an old success marker.
    if sys.version_info < (3,11): raise RuntimeError('Python 3.11+ is required')
    sys.path.insert(0,str(ROOT/'.tools/pdf'))
    try:
        import pypdf
    except ImportError as error:
        raise RuntimeError('Run: python -m pip install --target .tools/pdf -r requirements-historical.txt') from error
    pinned=(ROOT/'requirements-historical.txt').read_text().strip().split('==')[1]
    if pypdf.__version__ != pinned: raise RuntimeError('PDF dependency differs from requirements-historical.txt')
    for name in ('historical_pdfs','historical_expanded'):
        manifest=ROOT/'data/external'/name/'manifest.json'
        if not manifest.exists(): raise RuntimeError('Saved evidence manifest missing: '+str(manifest))
        payload=json.loads(manifest.read_text())
        records=payload if isinstance(payload,list) else payload['files']
        for row in records:
            path=manifest.parent/row['file']
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
                raise RuntimeError('Saved evidence missing or modified: '+str(path))
    inputs=list((ROOT/'data/raw').glob('*'))+list((ROOT/'config').glob('*.json'))
    inputs+=list((ROOT/'scripts').glob('*.py'))+list((ROOT/'tests').glob('*.py'))
    inputs+=[ROOT/'dashboard/template.html',ROOT/'requirements-historical.txt']+list((ROOT/'sql').glob('*.sql'))
    for name in ('historical_pdfs','historical_expanded'):
        inputs += [p for p in (ROOT/'data/external'/name).iterdir() if p.name!='canonical_observations.json' and p.is_file()]
    before=hashes(inputs)
    (ROOT/'analysis').mkdir(exist_ok=True)
    build(); first=outputs()
    if args.verify_reproducibility:
        build()
        if first != outputs(): raise RuntimeError('Repeated builds produced different output hashes')
    if before != hashes(inputs): raise RuntimeError('Replay changed an input file')
    report=dict(status='success',mode='offline_saved_evidence',cleaning_policy='conservative_supplied_data',repeat_verified=args.verify_reproducibility,
        python=sys.version.split()[0],
        pypdf=pypdf.__version__,inputs=before,outputs=first,
        limitations='Repeat verification uses the same environment; it is not a cross-platform or clean-environment certification. Historical coverage remains partial.')
    marker.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Complete: {len(first)} output files. Repeat verified: {args.verify_reproducibility}. See analysis/pipeline_manifest.json')


if __name__=='__main__': main()
