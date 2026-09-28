"""Left-join point-in-time context to metric audits without changing KPI rows."""
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from asteria.external.temporal import select_observation

from asteria.paths import ROOT
INDICATORS = ('unemployment','inflation','vacancies','vacancies_bf_supplementary')


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    if len({r['employee_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate employee key: '+str(path))
    return rows


def enrich(audit, employees, observations, turnover_start=None):
    result=[]; evidence=[]
    for original in audit:
        employee=employees[original['employee_id']]
        row=dict(original)
        if 'country_code' in row and row['country_code'] != employee['country_code']:
            raise ValueError('Country mismatch')
        row['country_code']=employee['country_code']
        cutoff=turnover_start or original['hire_date']
        row['external_cutoff']=cutoff
        included=(int(original['employee_days'])>0 if turnover_start else original['status'] in ('retained','left_before_milestone'))
        row['in_metric_population']='true' if included else 'false'
        for indicator in INDICATORS:
            selected={'status':'outside_metric_population','observation':None}
            if included:
                selected=select_observation(observations,employee['country_code'],indicator,date.fromisoformat(cutoff))
            obs=selected['observation'] or {}
            row[indicator+'_status']=selected['status']
            for field in ('value','period_start','period_end','available_on','vintage_id','evidence_url','unit','frequency','sector','source_file','source_sha256','source_page'):
                row[indicator+'_'+field]=obs.get(field,'')
            row[indicator+'_age_days']=selected.get('age_days','')
            evidence.append(dict(employee_id=original['employee_id'],indicator=indicator,cutoff=cutoff,**selected))
        # Every original field survives the left join exactly.
        if any(row[k]!=v for k,v in original.items()):
            raise ValueError('Metric audit changed')
        result.append(row)
    return result,evidence


def main():
    folder=ROOT/'analysis'
    workforce_path=ROOT/'data/curated/employee_lifecycle_curated.csv'
    observations_path=ROOT/'data/external/historical_expanded/canonical_observations.json'
    employees={r['employee_id']:r for r in read_csv(workforce_path)}
    observations=json.loads(observations_path.read_text())
    turnover_path=folder/'regretted_turnover_summary.json'
    turnover=json.loads(turnover_path.read_text())
    summaries={}; sources=[workforce_path,observations_path,turnover_path]
    for metric in ('new_hire_6m','senior_hire_12m','regretted_turnover'):
        source=folder/(metric+'_employee_audit.csv'); sources.append(source)
        audit=read_csv(source)
        is_turnover=metric=='regretted_turnover'
        joined,evidence=enrich(audit,employees,observations,turnover['window_start'] if is_turnover else None)
        with (folder/(metric+'_with_external.csv')).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(joined[0])); writer.writeheader(); writer.writerows(joined)
        (folder/(metric+'_external_lineage.json')).write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
        population=[r for r in joined if r['in_metric_population']=='true']
        summary=dict(audit_rows=len(audit),metric_population_records=len(population),
            cutoff='window_start' if is_turnover else 'hire_date',
            indicators={})
        for indicator in INDICATORS:
            matched=[r for r in population if r[indicator+'_status']=='matched']
            item=dict(statuses=dict(Counter(r[indicator+'_status'] for r in population)),matched_records=len(matched),
                matched_pct=100*len(matched)/len(population) if population else None)
            if is_turnover:
                item.update(matched_employee_days=sum(int(r['employee_days']) for r in matched),
                    matched_confirmed_departures=sum(r['status']=='confirmed_regretted_departure' for r in matched))
            else:
                item['matched_outcomes']=dict(Counter(r['status'] for r in matched))
            summary['indicators'][indicator]=item
        if is_turnover:
            assert sum(int(r['employee_days']) for r in joined)==turnover['employee_days']
            assert sum(r['status']=='confirmed_regretted_departure' for r in joined)==turnover['confirmed_regretted_departures']
        summaries[metric]=summary
    report=dict(metrics=summaries,inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        notes=['All original audit rows and fields are preserved. External status outside_metric_population means not attempted, not missing source evidence.',
               'Retention coverage is among mature retained/left cohorts. Turnover coverage is among employees contributing positive employee-days; its KPI denominator remains average daily headcount.',
               'Turnover context uses window start even for hires later in the window; it is baseline country context, not a prediction for a fixed baseline employee cohort.',
               'B-N vacancies are preferred; B-F remains supplementary and never substitutes. Repeated economic observations are not independent samples.',
               'No association or causal analysis is performed. Existing headline KPIs are not overwritten.'])
    (folder/'metric_external_coverage.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# External coverage within metric populations','', '| Metric | Population records | Unemployment | CPI | Preferred B-N | Supplementary B-F |','|---|---:|---:|---:|---:|---:|']
    for metric,s in summaries.items():
        counts=[str(s['indicators'][i]['matched_records']) for i in INDICATORS]
        lines.append('| '+ ' | '.join([metric,str(s['metric_population_records'])]+counts)+' |')
    lines+=['']+report['notes']
    (folder/'metric_external_coverage.md').write_text('\n\n'.join(lines[0:2])+'\n'+'\n'.join(lines[2:])+'\n',encoding='utf-8')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__': main()
