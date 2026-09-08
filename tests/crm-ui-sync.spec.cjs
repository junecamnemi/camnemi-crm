'use strict';
/**
 * Isolated real-browser CRM persistence regressions (no test runner dependency).
 * node tests/crm-ui-sync.spec.cjs [--baseline | --source=absolute/path/index.html]
 * PLAYWRIGHT_MODULE=/path/to/playwright CHROME_PATH=/path/to/chrome overrides.
 *
 * Safety/fixture boundary: reads the source ONCE (SHA printed), serves only that
 * in-memory HTML on 127.0.0.1, replaces embedded backend defaults with a local
 * fake endpoint/key and strips DNS/preconnect hints. No business functions are
 * replaced. The application's existing localhost auth bypass is used; synthetic
 * camnemi_auth is also seeded locally. Never loads the user's browser profile.
 * Empty/non-HTML assets return local stubs. Supabase REST is fulfilled by the
 * in-memory fake below. All other requests abort; CSP, blocked service workers,
 * closed WebSockets and a dead outbound proxy provide defense in depth.
 * Synthetic initial localStorage prevents the app's built-in student seed.
 * Each scenario has fresh browser storage + fake database; reload preserves both.
 * No credentials, real customer data, network API clients, commits or deployment.
 */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const assert = require('node:assert/strict');
const repo = path.resolve(__dirname, '..');
const modulePath = process.env.PLAYWRIGHT_MODULE || 'C:/Users/USER/AppData/Local/Temp/crm-sync-test/node_modules/playwright';
let playwright;
try { playwright = require(modulePath); } catch { playwright = require('playwright'); }
const baseline = process.argv.includes('--baseline');
const sourceArg = process.argv.find(x => x.startsWith('--source='));
const raw = baseline ? execFileSync('git', ['show', 'HEAD:index.html'], { cwd: repo, encoding: 'utf8', maxBuffer: 10e6 }) : fs.readFileSync(sourceArg ? sourceArg.slice(9) : path.join(repo, 'index.html'), 'utf8');
const sha256 = crypto.createHash('sha256').update(raw).digest('hex');
const source = baseline ? 'git HEAD:index.html' : (sourceArg ? sourceArg.slice(9) : 'working index.html');
const clone = x => JSON.parse(JSON.stringify(x));
const fixtures = [
  { id: 'fixture_process', name: 'SYNTHETIC ALPHA', pipe: 'new', stage: 'registration' },
  { id: 'fixture_archive', name: 'SYNTHETIC BETA', pipe: 'consulting', stage: 'archived' },
  { id: 'fixture_korea', name: 'SYNTHETIC GAMMA', pipe: 'korea', stage: 'stay' },
  { id: 'fixture_consult', name: 'SYNTHETIC DELTA', pipe: 'consulting', stage: 'consult' }
].map(c => ({ ...c, school: 'SYNTHETIC UNIVERSITY', program: 'BA', age: '21', agency: '', contact: '', notes: [], payments: [], docs: [], recent: '1000', hidden: '' }));
function makeDB() {
  return { customers: clone(fixtures), universities: [{ id: 'fixture_school', name: 'SYNTHETIC UNIVERSITY', name_en: 'SYNTHETIC UNIVERSITY' }], agency_submissions: [] };
}
function matches(row, params) {
  for (const [key, value] of params) {
    if (['select', 'order', 'limit', 'offset', 'on_conflict'].includes(key)) continue;
    const str = String(row[key] ?? '');
    if (value.startsWith('eq.') && str !== value.slice(3)) return false;
    if (value.startsWith('neq.') && str === value.slice(4)) return false;
    if (value.startsWith('in.(') && !value.slice(4, -1).split(',').map(x => x.replace(/^"|"$/g, '')).includes(str)) return false;
    if (value.startsWith('ilike.') && str.toLowerCase() !== value.slice(6).replaceAll('*', '').toLowerCase()) return false;
  }
  return true;
}
const report = { source, sha256, fixture: 'local backend defaults + removed DNS hints; real localhost auth/boot/UI/sync', scenarios: [] };
let browser, server, origin;
async function scenario(name, run) {
  const result = { name, checks: [], errors: [], warnings: [], requests: [], blocked: [] };
  report.scenarios.push(result);
  const db = makeDB();
  const context = await browser.newContext({ viewport: { width: 1700, height: 1100 }, serviceWorkers: 'block' });
  context.setDefaultTimeout(5000);
  if (context.routeWebSocket) await context.routeWebSocket('**/*', socket => socket.close());
  await context.route('**/*', async route => {
    const req = route.request(), url = new URL(req.url());
    if (url.origin !== origin) { result.blocked.push(req.url()); return route.abort('blockedbyclient'); }
    if (!url.pathname.startsWith('/rest/v1/')) return route.continue();
    const table = url.pathname.split('/')[3], method = req.method();
    const body = req.postData() ? JSON.parse(req.postData()) : null;
    result.requests.push({ table, method, query: url.search, body });
    let rows = db[table] || (db[table] = []), answer = [];
    if (method === 'GET') answer = rows.filter(r => matches(r, url.searchParams));
    else if (method === 'POST') {
      const keys = (url.searchParams.get('on_conflict') || 'id').split(',');
      for (const row of (Array.isArray(body) ? body : [body])) {
        const at = rows.findIndex(r => keys.every(k => row[k] != null && r[k] === row[k]));
        if (at < 0) rows.push(clone(row)); else rows[at] = { ...rows[at], ...clone(row) };
      }
      answer = body;
    } else if (method === 'DELETE') db[table] = rows.filter(r => !matches(r, url.searchParams));
    else if (method === 'PATCH') { answer = rows.filter(r => matches(r, url.searchParams)); for (const row of answer) Object.assign(row, body); }
    else if (method !== 'OPTIONS') throw Error('Unhandled synthetic REST method ' + method);
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(answer), headers: { 'access-control-allow-origin': origin } });
  });
  await context.addInitScript(({ origin, customers }) => {
    if (location.origin !== origin) return;
    localStorage.setItem('camnemi_supabase_url', origin);
    localStorage.setItem('camnemi_supabase_key', 'synthetic-no-privileges');
    localStorage.setItem('camnemi_backend_url', origin + '/fake-apps-script');
    localStorage.setItem('camnemi_auth', JSON.stringify({ email: 'synthetic@camnemi.com', name: 'SYNTHETIC LOCAL USER', hd: 'camnemi.com', t: Date.now() }));
    if (!localStorage.getItem('crm_ui_fixture_seeded')) {
      localStorage.setItem('camnemi_db_v1', JSON.stringify({ version: 1, customers, agencies: [], fees: [], partners: [], tasks: [], transactions: [], recs: [], wikiNotes: [], wikiDocs: [], wikiCats: [], listCustomCols: [], hiddenListCols: [], listColOrder: [] }));
      localStorage.setItem('crm_ui_fixture_seeded', 'yes');
    }
  }, { origin, customers: fixtures });
  const newPage = async () => {
    const page = await context.newPage();
    page.on('pageerror', e => result.errors.push(e.message));
    page.on('console', msg => { if (msg.type() === 'warning') result.warnings.push(msg.text()); });
    page.on('dialog', dialog => dialog.type() === 'confirm' ? dialog.accept() : dialog.dismiss());
    await page.goto(origin + '/#/pipeline-new');
    await settle(page);
    return page;
  };
  const check = (label, value) => { result.checks.push({ label, pass: Boolean(value) }); };
  try {
    const page = await newPage();
    assert.equal(await page.locator('#login-overlay').isVisible(), false, 'Local fixture must bypass login');
    await run({ page, newPage, db, check, result });
    check('no uncaught page JavaScript errors', result.errors.length === 0);
  } catch (e) { result.errors.push(e.stack || String(e)); check('scenario executed completely', false); }
  finally { await context.close(); }
  result.pass = result.checks.every(x => x.pass);
  console.log((result.pass ? 'PASS ' : 'FAIL ') + name);
  for (const c of result.checks) console.log(`  ${c.pass ? 'ok' : 'NOT OK'} ${c.label}`);
  for (const e of result.errors) console.log('  ERROR ' + e);
  const relevant = [...new Set(result.warnings.filter(w => /push|pull|remoteCust/i.test(w)))];
  for (const w of relevant) console.log('  WARN ' + w);
}
async function settle(page) {
  await page.waitForFunction(() => typeof __bootDone !== 'undefined' && __bootDone);
  // Exercise the real debounce/boot timers, not mocked scheduling or save calls.
  await page.waitForTimeout(1600);
  await page.waitForFunction(() => typeof __syncing !== 'undefined' && !__syncing);
}
async function openPipe(page, pipe) {
  await page.locator(`.pipe-item[data-pipe="${pipe}"]`).click();
}
async function list(page) { await page.locator('#toggle-list').click(); }
async function rowPresent(page, name) { return (await page.locator('#list-body tr').filter({ hasText: name }).count()) > 0; }
async function stageOf(page, id) { return page.locator('#' + id).getAttribute('data-stage'); }
async function selectCard(page, id) { await page.locator('#' + id + ' .card-select').check(); }
async function reload(page) { await page.reload(); await settle(page); }
async function main() {
  server = http.createServer((req, res) => {
    const pathname = new URL(req.url, 'http://127.0.0.1').pathname;
    if (pathname === '/') {
      const html = raw.replace(/<link\b[^>]*rel=["'](?:preconnect|dns-prefetch)["'][^>]*>/gi, '')
        .replace(/(var DEFAULT_SUPABASE_URL\s*=\s*)'[^']*'/, `$1'${origin}'`)
        .replace(/(var DEFAULT_SUPABASE_KEY\s*=\s*)'[^']*'/, "$1'synthetic-no-privileges'");
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Content-Security-Policy': "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; frame-src 'none'; object-src 'none'; base-uri 'none'" }); res.end(html);
    } else if (pathname === '/fake-apps-script') { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end('{"ok":true,"found":false,"files":[]}'); }
    else { res.writeHead(200, { 'Content-Type': pathname.endsWith('.js') ? 'application/javascript' : 'text/plain' }); res.end(''); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  origin = 'http://127.0.0.1:' + server.address().port;
  const executablePath = process.env.CHROME_PATH || ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find(p => fs.existsSync(p));
  browser = await playwright.chromium.launch({ executablePath, headless: true, args: ['--disable-background-networking', '--disable-component-update', '--disable-domain-reliability', '--no-first-run', '--proxy-server=http://127.0.0.1:9', '--proxy-bypass-list=127.0.0.1;localhost', '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE localhost'] });
  console.log(JSON.stringify({ source, sha256, origin, executablePath }));
  await scenario('Process rich modal stage Save -> list -> cloud -> reload', async ({ page, db, check }) => {
    await page.locator('#fixture_process').click();
    await page.locator('#korea-edit-modal .kstage-btn[data-stage="visa"]').click();
    await page.locator('#korea-edit-modal button[onclick="saveKoreaEdit()"]').click();
    await settle(page);
    check('card moved to VISA', await stageOf(page, 'fixture_process') === 'visa');
    await list(page);
    const row = page.locator('#list-body tr').filter({ hasText: 'SYNTHETIC ALPHA' });
    check('list reflects VISA', /VISA/.test(await row.innerText()));
    check('fake cloud stage persisted', db.customers.find(c => c.id === 'fixture_process')?.stage === 'visa');
    await reload(page);
    check('stage survives reload/pull', await stageOf(page, 'fixture_process') === 'visa');
    await list(page); check('list stage survives reload', /VISA/.test(await page.locator('#list-body tr').filter({ hasText: 'SYNTHETIC ALPHA' }).innerText()));
  });
  await scenario('Archived Delete button -> list absence -> cloud deletion -> reload', async ({ page, db, check, result }) => {
    await openPipe(page, 'consulting'); await list(page);
    await page.locator('#list-body tr').filter({ hasText: 'SYNTHETIC BETA' }).click();
    await page.locator('#e-archive-btn').click(); await settle(page);
    check('deleted row gone immediately from list', !(await rowPresent(page, 'SYNTHETIC BETA')));
    check('fake cloud row actually deleted', !db.customers.some(c => c.id === 'fixture_archive'));
    check('DELETE customers request was sent', result.requests.some(r => r.table === 'customers' && r.method === 'DELETE'));
    await reload(page); await openPipe(page, 'consulting'); await list(page);
    check('deleted row does not resurrect after reload', !(await rowPresent(page, 'SYNTHETIC BETA')));
    check('unrelated customer retained', db.customers.some(c => c.id === 'fixture_consult'));
  });
  await scenario('Cloud deletion absent on pull in second preloaded tab', async ({ page, newPage, db, check }) => {
    const second = await newPage(); await list(second);
    check('second tab started with customer', await rowPresent(second, 'SYNTHETIC ALPHA'));
    // Simulates another authorized device deleting a row, only in fake DB.
    db.customers = db.customers.filter(c => c.id !== 'fixture_process');
    await second.evaluate(() => syncPull());
    check('pull removes remotely deleted card', await second.locator('#fixture_process').count() === 0);
    check('already-open list updates without toggling', !(await rowPresent(second, 'SYNTHETIC ALPHA')));
    await second.evaluate(() => syncPush());
    check('stale second tab does not reinsert cloud deletion', !db.customers.some(c => c.id === 'fixture_process'));
    await reload(page);
    check('first stale tab reload does not resurrect deletion', await page.locator('#fixture_process').count() === 0);
  });
  await scenario('Batch Hide preserves DB row but excludes kanban/list after refresh', async ({ page, db, check }) => {
    await selectCard(page, 'fixture_process');
    await page.locator('button[onclick="batchDelete()"]').click(); await settle(page);
    check('hidden customer not visible in kanban', !(await page.locator('#fixture_process').isVisible()));
    await list(page); check('hidden customer excluded from list', !(await rowPresent(page, 'SYNTHETIC ALPHA')));
    check('hide persisted, not DELETE', db.customers.find(c => c.id === 'fixture_process')?.hidden === 'true');
    await reload(page);
    check('hidden customer remains nonvisible after reload', !(await page.locator('#fixture_process').isVisible()));
    await list(page); check('hidden customer excluded from reloaded list', !(await rowPresent(page, 'SYNTHETIC ALPHA')));
  });
  await scenario('Archive customer via modal explicitly persists and reloads', async ({ page, db, check }) => {
    await openPipe(page, 'consulting'); await page.locator('#fixture_consult').click();
    await page.locator('#e-archive-btn').click(); await settle(page);
    check('archive persisted to fake DB', db.customers.find(c => c.id === 'fixture_consult')?.stage === 'archived');
    await reload(page); await openPipe(page, 'consulting');
    check('archive survives reload', await stageOf(page, 'fixture_consult') === 'archived');
  });
  await scenario('Batch archive moves persist through reload', async ({ page, db, check }) => {
    await selectCard(page, 'fixture_process'); await page.locator('button[onclick="batchArchive()"]').click(); await settle(page);
    check('batch archive persisted to fake DB', db.customers.find(c => c.id === 'fixture_process')?.stage === 'archived');
    await reload(page); check('batch archive survives reload', await stageOf(page, 'fixture_process') === 'archived');
  });
  await scenario('Agency submission already in Korea must not reimport into Process', async ({ page, db, check }) => {
    db.agency_submissions = [{ id: 'fixture_korea', name: 'SYNTHETIC GAMMA', program: 'BA', agency: '', contact: '', note: '' }];
    await page.evaluate(() => autoPullAgencySubmissions()); await settle(page);
    check('single card across all pipelines', await page.locator('.customer-card[data-name="SYNTHETIC GAMMA"]').count() === 1);
    check('Korea customer not recreated in Process', await page.locator('.customer-card[data-name="SYNTHETIC GAMMA"][data-pipe="new"]').count() === 0);
    check('fake cloud retains Korea pipeline', db.customers.find(c => c.id === 'fixture_korea')?.pipe === 'korea');
  });
  await scenario('Deleted customer is not recreated from retained agency submission', async ({ page, db, check }) => {
    // Retained inbox row can outlive its corresponding archived customer.
    db.agency_submissions = [{ id: 'fixture_archive', name: 'SYNTHETIC BETA', program: 'BA', agency: '', contact: '', note: '' }];
    await openPipe(page, 'consulting'); await page.locator('#fixture_archive').click();
    await page.locator('#e-archive-btn').click(); await settle(page);
    await page.evaluate(() => autoPullAgencySubmissions()); await settle(page);
    check('agency poll does not resurrect deleted customer', await page.locator('.customer-card[data-name="SYNTHETIC BETA"]').count() === 0);
    check('fake cloud customer stays deleted', !db.customers.some(c => c.id === 'fixture_archive'));
    await reload(page); await page.evaluate(() => autoPullAgencySubmissions()); await settle(page);
    check('agency poll after reload still cannot resurrect customer', await page.locator('.customer-card[data-name="SYNTHETIC BETA"]').count() === 0);
  });
  await scenario('Program Any filter stays active on boot, pipeline switch and reload', async ({ page, db, check }) => {
    const programAny = () => page.locator('.click-filter[data-ftype="program"][data-fval=""]').evaluate(el => el.classList.contains('active'));
    check('Program Any active after boot', await programAny());
    await openPipe(page, 'korea');
    check('Program Any active after pipeline switch', await programAny());
    await reload(page);
    check('Program Any active after reload', await programAny());
    // selecting a program value deactivates Any, and clearing re-activates it
    await page.locator('.click-filter[data-ftype="program"][data-fval="D4"]').click();
    await settle(page);
    check('Program D4 active when selected', await page.locator('.click-filter[data-ftype="program"][data-fval="D4"]').evaluate(el => el.classList.contains('active')));
    check('Program Any inactive when a value is selected', !(await programAny()));
    await page.locator('.click-filter[data-ftype="program"][data-fval=""]').click();
    await settle(page);
    check('Program Any re-activated after clearing', await programAny());
  });
  const passed = report.scenarios.filter(s => s.pass).length;
  console.log(`SUMMARY ${passed}/${report.scenarios.length} scenarios passed; ${report.scenarios.reduce((n, s) => n + s.checks.filter(c => !c.pass).length, 0)} failed checks; source SHA256 ${sha256}`);
  if (process.env.CRM_UI_REPORT) { fs.writeFileSync(process.env.CRM_UI_REPORT, JSON.stringify(report, null, 2)); console.log('REPORT ' + process.env.CRM_UI_REPORT); }
  process.exitCode = passed === report.scenarios.length ? 0 : 1;
}
main().catch(e => { console.error(e); process.exitCode = 1; }).finally(async () => { if (browser) await browser.close(); if (server) await new Promise(resolve => server.close(resolve)); });
