const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'agentic_engineering_assessment 1.html'), 'utf8');
// Execute only the supplied deterministic data functions, without browser actions.
const source = html.split('<script>')[1].split('    function saveFile')[0];
const context = { Blob };
vm.createContext(context);
vm.runInContext(source + '\n globalThis.pack = {files: FILES, artifacts: buildArtifacts(), rows: generateEvents()}; pack.manifest = buildManifest(pack.artifacts); }());', context, {timeout: 5000});
const {pack} = context;
const out = path.join(root, 'data', 'raw');
fs.mkdirSync(out, {recursive:true});
for (const [key, value] of Object.entries({...pack.artifacts, manifest:pack.manifest})) {
  const dest = path.join(out, pack.files[key]);
  if (fs.existsSync(dest) && fs.readFileSync(dest, 'utf8') !== value) throw Error('Refusing to overwrite different data: '+dest);
  fs.writeFileSync(dest, value);
}
const manifest = JSON.parse(pack.manifest);
const checks = manifest.files.map(f => {
  const bytes = fs.readFileSync(path.join(out, f.name));
  const hash = crypto.createHash('sha256').update(bytes).digest('hex');
  const rows = bytes.toString('utf8').trimEnd().split('\r\n').length - 1;
  if (hash !== f.sha256 || bytes.length !== f.bytes || rows !== f.data_rows) throw Error('Manifest mismatch: '+f.name);
  return {file:f.name, rows, bytes:bytes.length, verified:true};
});
const raw = Array.from(pack.rows);
const unique = [...new Map(raw.map(r=>[JSON.stringify(r),r])).values()];
const count = (field, rows=unique) => rows.reduce((a,r)=>{const k=r[field]||'(blank)';a[k]=(a[k]||0)+1;return a;},{});
const issues = {
  missing_country:r=>!r.country_code,
  noncanonical_country:r=>r.country_code && !['GR','RO','PL','IT','IE','BG'].includes(r.country_code),
  missing_hire_date:r=>!r.hire_date,
  termination_before_hire:r=>r.hire_date && r.termination_date && r.termination_date<r.hire_date,
  termination_after_snapshot:r=>r.termination_date>'2025-12-31',
  termination_without_type:r=>r.termination_date && !r.termination_type,
  voluntary_without_regretted_flag:r=>r.termination_type==='Voluntary' && !r.regretted_exit,
  nonstandard_career_level:r=>r.career_level==='Sr Mgmt',
  termination_without_regretted_flag:r=>r.termination_date && !r.regretted_exit,
};
const issueDetails = Object.fromEntries(Object.entries(issues).map(([k,fn])=>[k,{count:unique.filter(fn).length,employee_ids:unique.filter(fn).map(r=>r.employee_id)}]));
const dates = f => {const values=unique.map(r=>r[f]).filter(Boolean).sort();return {min:values[0],max:values.at(-1)};};
const profile = {
  as_of:manifest.workforce_as_of_date, seed:manifest.deterministic_seed, manifest_checks:checks,
  raw_rows:raw.length, distinct_employee_ids:new Set(raw.map(r=>r.employee_id)).size,
  exact_duplicate_excess:raw.length-unique.length, unique_rows:unique.length,
  note:'All distributions and issue counts below use exact-deduplicated records for inspection only. Raw files remain unchanged. Issue counts may overlap.',
  columns:Object.keys(raw[0]), missing_values:Object.fromEntries(Object.keys(raw[0]).map(f=>[f,unique.filter(r=>!r[f]).length])),
  countries:count('country_code'), business_units:count('business_unit'), career_levels:count('career_level'), employment_types:count('employment_type'),
  termination_types:count('termination_type'), regretted_exit:count('regretted_exit'),
  hire_dates:dates('hire_date'), termination_dates:dates('termination_date'),
  hire_years:count('year',unique.map(r=>({year:r.hire_date.slice(0,4)}))),
  issues:issueDetails, records_with_any_listed_issue:unique.filter(r=>Object.values(issues).some(fn=>fn(r))).length,
  examples:unique.slice(0,3)
};
fs.mkdirSync(path.join(root,'analysis'),{recursive:true});
fs.writeFileSync(path.join(root,'analysis','assessment_profile.json'),JSON.stringify(profile,null,2)+'\n');
console.log(JSON.stringify(profile,null,2));
