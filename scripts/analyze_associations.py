"""Exploratory cohort associations, selection diagnostics and sensitivity checks."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDICATORS=('unemployment','inflation','vacancies_bf_supplementary')


def rate(rows):
    n=len(rows); retained=sum(r['status']=='retained' for r in rows)
    return dict(n=n,retained=retained,rate=retained/n if n else None)


def correlation(points):
    if len(points)<3: return None
    x=[p[0] for p in points]; y=[p[1] for p in points]
    mx=sum(x)/len(x); my=sum(y)/len(y)
    xx=sum((v-mx)**2 for v in x); yy=sum((v-my)**2 for v in y)
    return sum((a-mx)*(b-my) for a,b in points)/math.sqrt(xx*yy) if xx and yy else None


def analyze(rows,indicator):
    eligible=[r for r in rows if r['in_metric_population']=='true']
    matched=[r for r in eligible if r[indicator+'_status']=='matched']
    unmatched=[r for r in eligible if r[indicator+'_status']!='matched']
    groups=defaultdict(list)
    for r in matched:
        period=r['hire_date'][:4] if indicator=='inflation' else r['hire_date'][:4]+'Q'+str((int(r['hire_date'][5:7])-1)//3+1)
        groups[(r['country_code'],period)].append(r)
    cohorts=[]
    for (country,period),group in sorted(groups.items()):
        observations={(r[indicator+'_period_end'],r[indicator+'_vintage_id']) for r in group}
        cohorts.append(dict(country=country,hire_period=period,**rate(group),
            exposure_mean=sum(float(r[indicator+'_value']) for r in group)/len(group),
            distinct_vintages=len(observations),age_days_min=min(int(r[indicator+'_age_days']) for r in group),
            age_days_max=max(int(r[indicator+'_age_days']) for r in group)))
    points=lambda cs:[(c['exposure_mean'],c['rate']) for c in cs]
    centered=[]
    for country in sorted({c['country'] for c in cohorts}):
        cs=[c for c in cohorts if c['country']==country]
        mx=sum(c['exposure_mean'] for c in cs)/len(cs); my=sum(c['rate'] for c in cs)/len(cs)
        centered.extend((c['exposure_mean']-mx,c['rate']-my) for c in cs)
    breakdown={}
    for field in ('country_code','hire_year','business_unit'):
        breakdown[field]=[{field:key,'matched':rate([r for r in matched if r[field]==key]),'unmatched':rate([r for r in unmatched if r[field]==key])} for key in sorted({r[field] for r in eligible})]
    return dict(matched=rate(matched),unmatched=rate(unmatched),breakdown=breakdown,
        distinct_country_reference_periods=len({(r['country_code'],r[indicator+'_period_end']) for r in matched}),
        distinct_country_period_vintages=len({(r['country_code'],r[indicator+'_period_end'],r[indicator+'_vintage_id']) for r in matched}),
        cohort_count=len(cohorts),cohorts_below_10=sum(c['n']<10 for c in cohorts),cohorts=cohorts,
        descriptive_pearson=correlation(points(cohorts)),within_country_centered_pearson=correlation(centered),
        min10_cohort_pearson=correlation(points([c for c in cohorts if c['n']>=10])),
        leave_one_country_out={country:correlation(points([c for c in cohorts if c['country']!=country])) for country in sorted({c['country'] for c in cohorts})})


def main():
    metrics={}; inputs={}
    for metric in ('new_hire_6m','senior_hire_12m'):
        path=ROOT/'analysis'/(metric+'_with_external.csv')
        inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open(encoding='utf-8',newline='') as stream: rows=list(csv.DictReader(stream))
        metrics[metric]={i:analyze(rows,i) for i in INDICATORS}
    report=dict(inputs=inputs,metrics=metrics,method={
        'scope':'Exploratory descriptive associations; no hypothesis tests, p-values, prediction or causal estimates.',
        'grain':'Country x hire quarter for unemployment/B-F; country x hire year for CPI.',
        'exposure':'Mean of employee-specific as-of values among matched mature hires; a cohort exposure summary, not a newly measured economic period value. Source frequency/period/vintage remain in joined audit.',
        'weighting':'Each cohort receives equal weight in correlations; exposure means within cohorts are employee-weighted.',
        'dependence':'Cohorts can reuse source periods/vintages. Neither employee count nor cohort count is an independent economic sample size.',
        'uncertainty':'No inferential intervals because repeated observations and only six countries make naive independence assumptions inappropriate. Report leave-one-country-out and minimum-size sensitivity, not confidence intervals.',
        'confounding':'Within-country centering removes country mean differences only; calendar trends, composition, selection, and omitted factors remain. Breakdown tables expose country/year/business-unit selection.',
        'multiple_comparisons':'All three preselected available indicators and both required retention populations are reported, including weak/unstable patterns. No significance-based selection.',
        'turnover':'Deferred relationship estimation: one annual window and six country contexts do not support a credible repeated-period analysis. Snapshot KPI/coverage remain valid.',
        'threshold':'Minimum 10 mature matched hires is an exploratory stability check, not a guarantee of reliability.',
        'vacancies':'B-F supplementary sector measure only. Preferred B-N has no verified historical matches.'})
    (ROOT/'analysis/association_analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Exploratory external-signal analysis','',*report['method'].values(),'','| Population | Indicator | Matched | Unmatched | Cohorts | Cohorts <10 | Pooled r | Within-country r | Min-10 r |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    fmt=lambda v:'unavailable' if v is None else f'{v:.3f}'
    for metric,indicators in metrics.items():
        for indicator,r in indicators.items():
            lines.append(f"| {metric} | {indicator} | {r['matched']['n']} | {r['unmatched']['n']} | {r['cohort_count']} | {r['cohorts_below_10']} | {fmt(r['descriptive_pearson'])} | {fmt(r['within_country_centered_pearson'])} | {fmt(r['min10_cohort_pearson'])} |")
    lines+=['','## Interpretation guardrails','','A correlation describes co-movement in this synthetic matched subset. Compare pooled, centered and sensitivity results before describing a pattern. Small or sign-changing results are not stable evidence. Higher correlation does not establish practical importance or causality. Inspect the JSON breakdowns before generalizing beyond matched hires.']
    (ROOT/'analysis/association_analysis.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines[-15:]))
if __name__=='__main__': main()
