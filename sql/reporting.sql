CREATE TABLE audit (
 metric TEXT NOT NULL, employee_id TEXT NOT NULL, country TEXT, business_unit TEXT,
 hire_year TEXT, status TEXT NOT NULL, employee_days INTEGER NOT NULL CHECK(employee_days>=0),
 PRIMARY KEY(metric,employee_id));
CREATE TABLE objective(metric TEXT PRIMARY KEY,target REAL NOT NULL,calendar_days INTEGER);
CREATE TABLE external_match(metric TEXT NOT NULL,employee_id TEXT NOT NULL,indicator TEXT NOT NULL,
 status TEXT NOT NULL,value REAL,period_end TEXT,available_on TEXT,evidence_url TEXT,
 PRIMARY KEY(metric,employee_id,indicator),
 FOREIGN KEY(metric,employee_id) REFERENCES audit(metric,employee_id));
CREATE TABLE input_lineage(path TEXT PRIMARY KEY,sha256 TEXT NOT NULL);
CREATE VIEW retention_cohorts AS
 SELECT metric,country,business_unit,hire_year,COUNT(*) records,
 SUM(status IN ('retained','left_before_milestone')) eligible,
 SUM(status='retained') retained,
 1.0*SUM(status='retained')/NULLIF(SUM(status IN ('retained','left_before_milestone')),0) rate
 FROM audit WHERE metric!='regretted_turnover' GROUP BY metric,country,business_unit,hire_year;
CREATE VIEW kpi_components AS
 SELECT a.metric,SUM(a.status='retained') numerator,
 SUM(a.status IN ('retained','left_before_milestone')) denominator,0 unknown_departures,o.target
 FROM audit a JOIN objective o USING(metric) WHERE a.metric!='regretted_turnover' GROUP BY a.metric
 UNION ALL
 SELECT a.metric,SUM(a.status='confirmed_regretted_departure'),
 1.0*SUM(a.employee_days)/o.calendar_days,SUM(a.status='potentially_regretted_unknown'),o.target
 FROM audit a JOIN objective o USING(metric) WHERE a.metric='regretted_turnover' GROUP BY a.metric;
CREATE VIEW kpis AS SELECT *,1.0*numerator/NULLIF(denominator,0) rate,
 1.0*(numerator+unknown_departures)/NULLIF(denominator,0) classification_upper_rate,
 CASE WHEN denominator=0 THEN 'unavailable'
 WHEN metric!='regretted_turnover' THEN CASE WHEN 1.0*numerator/denominator>=target THEN 'met' ELSE 'below_target' END
 WHEN 1.0*numerator/denominator>target THEN 'above_target'
 WHEN 1.0*(numerator+unknown_departures)/denominator<=target THEN 'met_under_classification_scenarios'
 ELSE 'uncertain_due_to_classification' END target_status FROM kpi_components;
CREATE VIEW quality_counts AS SELECT metric,status,COUNT(*) records FROM audit GROUP BY metric,status;
CREATE VIEW external_coverage AS SELECT e.metric,e.indicator,e.status,COUNT(*) records,
 SUM(a.employee_days) employee_days FROM external_match e JOIN audit a USING(metric,employee_id)
 WHERE (a.metric='regretted_turnover' AND a.employee_days>0)
 OR (a.metric!='regretted_turnover' AND a.status IN ('retained','left_before_milestone'))
 GROUP BY e.metric,e.indicator,e.status;
