// One-time, auditable recovery for this fictional assessment only.
// Replay the unchanged generator first; capture rows before intentional defects.
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const sourceName = 'agentic_engineering_assessment 1.html';
const sourceBytes = fs.readFileSync(path.join(root, sourceName));
const html = sourceBytes.toString('utf8');
const start = html.indexOf('    var SEED =');
const end = html.indexOf('    function buildArtifacts()', start);
if (start < 0 || end < 0) throw Error('Generator boundaries missing');
const code = html.slice(start, end);
const marker = '      [44, 388, 722, 1055, 1399, 1744, 2111].forEach';
if (code.split(marker).length !== 2) throw Error('Defect boundary changed');
const ctx = vm.createContext({});
vm.runInContext(code.replace(marker, '      globalThis.pristine = JSON.parse(JSON.stringify(rows));\n' + marker) + '\nglobalThis.generated = generateEvents();', ctx, {timeout: 5000});
const fields = Object.keys(ctx.generated[0]);
ctx.fields = fields;
const replay = Buffer.from(vm.runInContext('toCsv(fields, generated)', ctx));
const raw = fs.readFileSync(path.join(root, 'data/raw/employee_lifecycle_events.csv'));
if (!replay.equals(raw)) throw Error('Generator does not reproduce raw CSV byte for byte');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const pristine = new Map(ctx.pristine.map(row => [row.employee_id, row]));
const corrections = [];
for (const row of ctx.generated.slice(0, ctx.pristine.length)) {
  for (const field of fields) {
    const value = pristine.get(row.employee_id)[field];
    if (row[field] !== value) corrections.push({employee_id:row.employee_id, field, original:row[field], corrected:value});
  }
}
const report = {mode:'verified_synthetic_generator_recovery', source:sourceName,
  source_sha256:hash(sourceBytes), raw_sha256:hash(raw), generator_reproduces_raw:true,
  note:'User-requested recovery of pre-defect synthetic values. Not an inference or a technique for real employee data. Raw inputs remain unchanged.', corrections};
fs.writeFileSync(path.join(root, 'config/synthetic_source_corrections.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`Verified raw replay; recovered ${corrections.length} cells for ${new Set(corrections.map(r=>r.employee_id)).size} employees.`);
