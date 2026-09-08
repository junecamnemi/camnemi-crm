const test = require('node:test');
const assert = require('node:assert/strict');
const {fixture} = require('./customer-sync-harness.cjs');
const a = {id:'fixture-a',name:'SAME NAME',pipe:'new',stage:'registration',notes:[],docs:[]};
const b = {...a,id:'fixture-b',name:'OTHER NAME'};
test('explicit delete survives failed write and reload, then deletes remotely without resurrecting',async()=>{
  const f=fixture([a,b]);
  await f.context.syncPull();
  f.setFail(true);
  f.delete(a.id);
  assert.equal(await f.context.syncPush(),false);
  const reloaded=fixture([a,b],f.storage,f.session);
  await reloaded.context.syncPull();
  assert.deepEqual(reloaded.cards().map(c=>c.id),[b.id]);
  assert.equal(await reloaded.context.syncPush(),true);
  assert.deepEqual(reloaded.remote().map(c=>c.id),[b.id]);
  assert.ok(reloaded.calls.some(c=>c.method==='DELETE' && c.url.includes('id=eq.fixture-a')));
  await reloaded.context.syncPull();
  assert.deepEqual(reloaded.cards().map(c=>c.id),[b.id]);
});
test('pending field edits survive failed write, reload and pull without overwriting remote unrelated fields',async()=>{
  const f=fixture([a]);
  await f.context.syncPull();
  f.edit(a.id,{stage:'visa',passport:'LOCAL-PASSPORT',notes:JSON.stringify([{text:'pending'}]),payments:JSON.stringify([{amount:12}]),loanFlag:'true'});
  f.setFail(true);
  assert.equal(await f.context.syncPush(),false);
  const g=fixture([{...a,email:'remote@example.invalid'}],f.storage,f.session);
  await g.context.syncPull();
  assert.equal(g.cards()[0].dataset.stage,'visa');
  assert.equal(g.cards()[0].dataset.passport,'LOCAL-PASSPORT');
  assert.equal(g.cards()[0].dataset.loanFlag,'true');
  assert.deepEqual(JSON.parse(g.cards()[0].dataset.payments),[{amount:12}]);
  assert.equal(g.cards()[0].dataset.email,'remote@example.invalid');
  assert.equal(await g.context.syncPush(),true,g.warnings.join('\n'));
  assert.equal(g.remote()[0].stage,'visa');
  assert.equal(g.remote()[0].email,'remote@example.invalid');
  assert.equal(g.remote()[0].loan_flag,'true');
});
test('saveNow uses Supabase without Apps Script and serializes edits arriving during a write',async()=>{
  const f=fixture([a]); await f.context.syncPull();
  f.edit(a.id,{stage:'visa'});
  assert.equal(await f.context.saveNow(),true,'saveNow must await Supabase completion without an Apps Script URL');
  assert.equal(f.remote()[0].stage,'visa');
  let release, started;
  const barrier=new Promise(r=>{release=r;});
  const reached=new Promise(r=>{started=r;});
  let patches=0;
  f.setBeforeRequest(async req=>{if(req.method==='PATCH' && ++patches===1){started();await barrier;}});
  f.edit(a.id,{stage:'admission'});
  const first=f.context.saveNow(); await reached;
  f.edit(a.id,{stage:'archived'});
  const second=f.context.saveNow();
  await new Promise(r=>setImmediate(r));
  assert.equal(patches,1,'no second request may overlap the first');
  release();
  assert.equal(await first,true); assert.equal(await second,true);
  assert.equal(f.remote()[0].stage,'archived');
});
test('only a deliberate new ID may insert; same-name people stay separate and stale cache cannot insert',async()=>{
  const f=fixture([a]); await f.context.syncPull();
  const intentional={...a,id:'intentional-new'};
  f.setCards([a,intentional,{...a,id:'stale-cache'}]);
  assert.equal(typeof f.context.customerQueueCreate,'function','explicit create intent is required');
  f.context.customerQueueCreate(intentional.id);
  f.edit(intentional.id,{stage:'admission'});
  assert.equal(await f.context.syncPush(),true,f.warnings.join('\n'));
  assert.deepEqual(f.remote().map(c=>c.id),[a.id,intentional.id]);
  assert.equal(f.remote()[1].stage,'admission');
  const post=f.calls.find(c=>c.method==='POST');
  assert.ok(post); assert.ok(!post.headers.Prefer.includes('merge-duplicates'));
});
test('authoritative empty pull removes the last cached card and never writes it back',async()=>{
  const f=fixture([a]); f.setRemote([]);
  assert.equal(await f.context.syncPull(),true);
  assert.equal(f.cards().length,0);
  assert.equal(await f.context.syncPush(),true);
  assert.equal(f.calls.filter(c=>c.method!=='GET').length,0);
});
test('cloud boot never seeds, pulls before saving, and unload only records durable intent',async()=>{
  const f=fixture([]); f.bootSetup();
  let seeds=0; f.context.seed=()=>{seeds++;}; f.context.seedKoreaStudents=()=>{seeds++;};
  await f.context.bootApp();
  assert.equal(seeds,0,'cloud boot must not seed customer rows');
  await f.timers.find(t=>t.delay===100).fn();
  assert.equal(seeds,0,'empty cloud must remain empty');
  assert.equal(f.calls.filter(c=>c.method!=='GET').length,0);
  assert.ok(!f.timers.some(t=>t.delay===4000),'historical agency submissions cannot auto-import on boot');
  f.setCards([a]); f.edit(a.id,{stage:'visa',recent:String(Date.now())});
  f.calls.length=0; f.events.get('beforeunload')();
  await new Promise(r=>setImmediate(r));
  assert.equal(f.calls.length,0,'unload must not race or POST/upsert customer rows');
  assert.ok(Array.from(f.storage.values()).some(v=>v.includes('visa')),'unload must persist pending edit');
});
test('archive and batch moves explicitly persist without a MutationObserver',async()=>{
  const f=fixture([a]); await f.context.syncPull();
  f.loadFunction('bumpCardRecent'); f.loadFunction('archiveCustomer'); f.setOverlay({_card:f.cards()[0]});
  f.context.archiveCustomer(); await f.run('__customerSyncQueue');
  assert.equal(f.remote()[0].stage,'archived');
  f.context.updateBatchBar=()=>{}; f.loadFunction('batchMove');
  f.context.batchMove('visa'); await f.run('__customerSyncQueue');
  assert.equal(f.remote()[0].stage,'visa');
});
test('pending deliberate insert stays visible across pull and offline reload',async()=>{
  const f=fixture([]); f.setCards([a]); f.context.customerQueueCreate(a.id);
  await f.context.syncPull();
  assert.deepEqual(f.cards().map(c=>c.id),[a.id]);
  const g=fixture([],f.storage,f.session); await g.context.syncPull();
  assert.deepEqual(g.cards().map(c=>c.id),[a.id]);
  assert.equal(await g.context.syncPush(),true);
  assert.equal(g.remote()[0].id,a.id);
});
test('lost insert acknowledgement is reconciled by ID, never retried as an upsert',async()=>{
  const f=fixture([]); f.setCards([a]); f.context.customerQueueCreate(a.id);
  f.setBeforeRequest(req=>{if(req.method==='POST'){f.setRemote(req.body);throw new Error('response lost after commit');}});
  assert.equal(await f.context.syncPush(),false);
  f.setBeforeRequest(null);
  assert.equal(await f.context.syncPush(),true,f.warnings.join('\n'));
  assert.equal(f.calls.filter(c=>c.method==='POST').length,1);
  assert.equal(f.remote().length,1);
});
test('editing a new customer during INSERT becomes a PATCH after acknowledgement',async()=>{
  const f=fixture([]); f.setCards([a]); f.context.customerQueueCreate(a.id);
  let release, started;
  const barrier=new Promise(r=>{release=r;});const reached=new Promise(r=>{started=r;});
  f.setBeforeRequest(async req=>{if(req.method==='POST'){started();await barrier;}});
  const first=f.context.saveNow();await reached;
  f.edit(a.id,{stage:'visa'});const second=f.context.saveNow();release();
  assert.equal(await first,true);assert.equal(await second,true,f.warnings.join('\n'));
  assert.equal(f.remote()[0].stage,'visa');
  assert.equal(f.calls.filter(c=>c.method==='POST').length,1);
  assert.deepEqual(f.calls.find(c=>c.method==='PATCH').body,{stage:'visa'});
});
test('new-customer form creates an explicit durable insert without observer assistance',async()=>{
  const f=fixture([]);await f.context.syncPull();
  Object.assign(f.context,{caps:s=>s,disambiguateName:s=>s,nowStr:()=>'',currentUserName:()=>'',normalizeAgency:s=>s,nextCamnemiId:()=>'',camnemiYear:()=>2026});
  f.setOverlay({dataset:{pipe:'new'},querySelector:selector=>({value:({'#f-name':'FORM CUSTOMER','#f-contact':'555','#f-age':'20','#f-stage':'registration'})[selector]||''})});
  f.loadFunction('saveNewCustomer'); f.context.saveNewCustomer();await f.run('__customerSyncQueue');
  assert.equal(f.remote().length,1);
  assert.equal(f.remote()[0].name,'FORM CUSTOMER');
});
test('quick add registers a new ID before immediate save',async()=>{
  const f=fixture([]); await f.context.syncPull();
  Object.assign(f.context,{caps:s=>s,disambiguateName:s=>s,nowStr:()=>'',currentUserName:()=>'',normalizeAgency:s=>s,nextCamnemiId:()=>'',camnemiYear:()=>2026,pickedValue:()=>'',reorderAllByRecent(){}});
  f.setOverlay({querySelector:selector=>({value:({'#q-name':'QUICK CUSTOMER','#q-contact':'555'})[selector]||''})});
  f.loadFunction('bumpCardRecent'); f.loadFunction('saveQuickAdd');f.context.saveQuickAdd();await f.run('__customerSyncQueue');
  assert.equal(f.remote().length,1);assert.equal(f.remote()[0].name,'QUICK CUSTOMER');
});
test('manual submission import uses stable IDs across pipelines and respects local deletions',async()=>{
  const f=fixture([{...a,pipe:'korea'},b]); await f.context.syncPull();
  f.delete(b.id);await f.run('__customerSyncQueue');
  const originalSelect=f.context.sbSelect;
  f.context.sbSelect=(table,q)=>table==='agency_submissions' ? Promise.resolve([{id:a.id,name:'OLD NAME'},{id:b.id,name:b.name},{id:'submission-new',name:'AGENCY NEW'}]) : originalSelect(table,q);
  f.context.renderPipeline=()=>{};
  f.loadFunction('pullAgencySubmissionsApp');await f.context.pullAgencySubmissionsApp();await f.run('__customerSyncQueue');
  assert.deepEqual(f.cards().map(c=>c.id).sort(),[a.id,'submission-new'].sort());
  assert.equal(f.remote().find(c=>c.id===a.id).pipe,'korea');
  assert.ok(f.remote().some(c=>c.id==='submission-new'));
});
test('CSV import registers deliberate inserts rather than treating restored rows as stale cache',async()=>{
  const f=fixture([]); await f.context.syncPull();
  f.context.FileReader=class{readAsText(){this.onload({target:{result:'name,contact,stage\nCSV CUSTOMER,555,registration'}});}};
  f.context.nowStr=()=>'';f.loadFunction('parseCSVLine');f.loadFunction('importCustomersFromCSV');
  f.context.importCustomersFromCSV({target:{files:[{}],value:''}});
  await f.context.syncPush();assert.equal(f.remote().length,1);assert.equal(f.remote()[0].name,'CSV CUSTOMER');
});
test('pull refreshes an already-open list after authoritative customer removal',async()=>{
  const f=fixture([a]);f.context.currentView='list';let renders=0;
  f.context.renderList=()=>{renders++;};f.setRemote([]);
  await f.context.syncPull();assert.equal(f.cards().length,0);assert.ok(renders>0);
});
test('custom fields round-trip through restore without losing unconfigured keys',async()=>{
  const f=fixture([{...a,custom_fields:{'Case notes':'existing','Invisible':'keep'}}]);
  await f.context.syncPull();
  assert.equal(f.context.exportAllData().customers[0].customFields.Invisible,'keep');
  f.run("LIST_CUSTOM_COLS=['Case notes']"); f.edit(a.id,{casenotes:'edited'});
  assert.equal(await f.context.syncPush(),true);
  assert.deepEqual(f.remote()[0].custom_fields,{'Case notes':'edited','Invisible':'keep'});
});
test('custom fields cannot replace core fields during restore, export, display or editing',async()=>{
  const customFields={Stage:'custom stage',Pipe:'custom pipe',ID:'custom id',Passport:'custom passport',Payments:'custom payments','Loan Flag':'custom loan','Case notes':'legacy safe',Invisible:'keep'};
  const f=fixture([{...a,passport:'CORE-PASSPORT',payments:[],loan_flag:'true',custom_fields:customFields}]);
  assert.equal(await f.context.syncPull(),true,f.warnings.join('\n'));
  const card=f.cards()[0];
  assert.equal(card.dataset.stage,a.stage,'custom Stage must never replace core stage');
  assert.equal(card.dataset.pipe,a.pipe);
  assert.equal(card.id,a.id);
  assert.equal(card.dataset.passport,'CORE-PASSPORT');
  assert.equal(card.dataset.payments,'[]');
  assert.equal(card.dataset.loanFlag,'true');
  assert.equal(card.dataset.id,undefined,'custom ID must stay out of core dataset');
  f.run(`LIST_CUSTOM_COLS=${JSON.stringify(Object.keys(customFields))}`);
  f.loadFunction('listCustomValue');
  for(const [key,value] of Object.entries(customFields)) {
    assert.equal(f.context.listCustomValue(card,key),value,'display custom '+key);
  }
  let row=f.context.exportAllData().customers[0];
  assert.equal(row.stage,a.stage);
  assert.deepEqual(JSON.parse(JSON.stringify(row.customFields)),customFields);
  f.edit(a.id,{casenotes:'legacy edit'});
  assert.equal(f.context.listCustomValue(card,'Case notes'),'legacy edit');
  assert.equal(f.context.exportAllData().customers[0].customFields['Case notes'],'legacy edit');
  f.loadFunction('editListField');
  const create=f.context.document.createElement;
  let handlers;
  f.context.document.createElement=tag=>tag==='input' ? {value:'',style:{},focus(){},addEventListener:(event,fn)=>{handlers[event]=fn;}} : create(tag);
  for(const [key,value] of [['Stage','edited custom stage'],['Case notes','edited safe field']]) {
    handlers={};let input;
    const td={dataset:{colkey:key,cardid:a.id},appendChild:el=>{input=el;}};
    f.context.editListField(td);input.value=value;handlers.blur();await f.run('__customerSyncQueue');
    assert.equal(JSON.parse(card.dataset.customFields)[key],value,'editor stores exact custom name');
    assert.equal(f.context.listCustomValue(card,key),value);
  }
  row=f.context.exportAllData().customers[0];
  assert.equal(row.stage,a.stage);
  assert.equal(row.customFields.Stage,'edited custom stage');
  assert.equal(f.remote()[0].stage,a.stage);
  assert.equal(f.remote()[0].custom_fields.Stage,'edited custom stage');
  assert.equal(f.remote()[0].custom_fields['Case notes'],'edited safe field');
  assert.equal(f.remote()[0].custom_fields.Invisible,'keep');
  const patches=f.calls.filter(c=>c.method==='PATCH');
  assert.ok(patches.length>0);
  assert.ok(patches.every(c=>!Object.hasOwn(c.body,'stage') && !Object.hasOwn(c.body,'pipe')));
});
test('legacy agency contact form creates its intended customer through the same outbox',async()=>{
  const f=fixture([]);await f.context.syncPull();
  Object.assign(f.context,{disambiguateName:s=>s,pickedValue:()=>'',nextCamnemiId:()=>'',camnemiYear:()=>2026});
  const get=f.context.document.getElementById;
  f.context.document.getElementById=id=>id==='agency-page' ? {querySelector:selector=>({value:selector==='#ap-name'?'AGENCY FORM':''})} : get(id);
  f.loadFunction('submitAgencyContact');f.context.submitAgencyContact();await f.run('__customerSyncQueue');
  assert.equal(f.remote().length,1);assert.equal(f.remote()[0].name,'AGENCY FORM');
});
test('one rejected customer operation cannot block another customer stage edit',async()=>{
  const f=fixture([a]);await f.context.syncPull();
  f.setCards([a,{...b,id:'poison-create'}]);f.context.customerQueueCreate('poison-create');
  f.edit(a.id,{stage:'visa'});
  f.setBeforeRequest(req=>{if(req.method==='POST')throw new Error('fixture insert rejected');});
  assert.equal(await f.context.syncPush(),false);
  assert.equal(f.remote()[0].stage,'visa');
  assert.ok(f.run("__customerOps.has('poison-create')"));
  assert.ok(!f.run("__customerOps.has('fixture-a')"));
});
test('in-place task additions and nested edits each emit only task writes', async()=>{
  const f=fixture([a]);
  assert.equal(await f.context.syncPull(),true);
  f.calls.length=0;
  f.run("TASKS.push({date:'2026-09-08',type:'todo',title:'NEW TASK',note:'original'})");
  assert.equal(await f.context.saveNow(),true,f.warnings.join('\n'));
  let writes=f.calls.filter(c=>c.method!=='GET');
  assert.deepEqual(writes.map(c=>[c.method,c.url.split('?')[0]]),[
    ['DELETE','/rest/v1/tasks'],['POST','/rest/v1/tasks']
  ],'TASKS.push must not mutate the observed baseline');
  assert.equal(writes[1].body[0].title,'NEW TASK');
  f.calls.length=0;
  f.run("TASKS[0].note='edited existing task'");
  assert.equal(await f.context.saveNow(),true,f.warnings.join('\n'));
  writes=f.calls.filter(c=>c.method!=='GET');
  assert.deepEqual(writes.map(c=>[c.method,c.url.split('?')[0]]),[
    ['DELETE','/rest/v1/tasks'],['POST','/rest/v1/tasks']
  ],'nested task edits must not mutate the post-save baseline');
  assert.equal(writes[1].body[0].note,'edited existing task');
  f.calls.length=0;
  assert.equal(await f.context.saveNow(),true);
  assert.equal(f.calls.filter(c=>c.method!=='GET').length,0,'unchanged tasks stay clean');
});
test('moving one card PATCHes only that ID and leaves untouched customers and ancillary tables alone', async()=>{
  const f=fixture([a,b]);
  assert.equal(await f.context.syncPull(),true);
  f.context.restoreCustomers();
  f.calls.length=0;
  f.edit(a.id,{stage:'visa'});
  assert.equal(await f.context.syncPush(),true, f.warnings.join('\n'));
  assert.equal(f.remote().find(c=>c.id===a.id).stage,'visa');
  const writes=f.calls.filter(c=>c.method!=='GET');
  assert.equal(writes.length,1,JSON.stringify(writes));
  assert.equal(writes[0].method,'PATCH');
  assert.deepEqual(writes[0].body,{stage:'visa'});
  assert.ok(writes[0].url.includes('id=eq.fixture-a'));
});
test('login after booting unauthenticated re-boots the app instead of blank screen', async()=>{
  // Boot once while NOT authenticated: bootApp must stop at the auth gate but
  // must NOT permanently mark the app as booted.
  const f=fixture([]);
  f.bootSetup(false); // initAuth() -> false (login required)
  assert.equal(f.context.renderPipeline.calls||0,0,'bootApp stopped before rendering when logged out');
  // Simulate successful login: auth now passes, then hideLogin() re-invokes bootApp.
  f.context.__setAuthed(true);
  f.context.authUser={email:'j@camnemi.com',name:'J',hd:'camnemi.com'};
  f.context.renderPipeline=()=>{ f.context.renderPipeline.calls=(f.context.renderPipeline.calls||0)+1; };
  f.context.updateAuthBadge=()=>{};
  f.loadFunction('hideLogin');
  f.context.hideLogin();
  assert.ok((f.context.renderPipeline.calls||0)>0,'hideLogin must re-boot the app after login (no blank screen)');
});
test('signOut clears the prior account cache but keeps shared Supabase settings', async()=>{
  const f=fixture([a]);
  await f.context.syncPull();
  f.storage.set('camnemi_auth','{"email":"j@camnemi.com","hd":"camnemi.com"}');
  f.storage.set('camnemi_customer_outbox_v1:w1','[]');
  f.storage.set('camnemi_customer_deleted_v1:abc','true');
  f.storage.set('camnemi_supabase_url','https://zjdvzpylxazfbazioxto.supabase.co');
  f.storage.set('camnemi_supabase_key','fake-anon');
  f.context.location={reload(){ this._reloaded=true; }};
  f.loadFunction('signOut');
  f.context.signOut();
  assert.ok(!f.storage.get('camnemi_auth'),'auth cleared');
  assert.ok(!f.storage.get('camnemi_db_v1'),'customer db cache cleared');
  assert.ok(!f.storage.get('camnemi_customer_outbox_v1:w1'),'pending outbox cleared');
  assert.ok(!f.storage.get('camnemi_customer_deleted_v1:abc'),'deleted markers cleared');
  assert.equal(f.storage.get('camnemi_supabase_url'),'https://zjdvzpylxazfbazioxto.supabase.co','supabase url kept');
  assert.equal(f.storage.get('camnemi_supabase_key'),'fake-anon','supabase key kept');
});
test('deleted agency does not resurrect from DEFAULT_AGENCIES on merge', async()=>{
  // DB (source of truth) no longer contains an agency the user deleted.
  // mergeAgencies must NOT re-add hardcoded DEFAULT agencies that were removed.
  const f=fixture([]);
  f.loadFunction('mergeAgencies');
  const loaded=[
    {name:'CAMNEMI',commission:'—'},
    {name:'Kimsous',commission:'—'},
    {name:'Global Study',commission:'0.12'}
  ];
  const merged=f.context.mergeAgencies(loaded);
  const names=merged.map(a=>a.name);
  // CAMNEMI must stay (in-house default), but deleted DEFAULT agencies must NOT return.
  assert.ok(names.includes('CAMNEMI'),'CAMNEMI always present');
  assert.ok(!names.includes('COSTA'),'deleted COSTA must not resurrect');
  assert.ok(!names.includes('Khema'),'deleted Khema must not resurrect');
  assert.ok(!names.includes('JK'),'deleted JK must not resurrect');
  assert.ok(!names.includes('Din Lina'),'deleted Din Lina must not resurrect');
  assert.ok(names.includes('Kimsous'),'existing loaded agency kept');
  assert.ok(names.includes('Global Study'),'existing loaded agency kept');
});
test('deleteAgency sends a server DELETE and persists locally', async()=>{
  const f=fixture([]);
  // Seed the in-vm AGENCIES array with two agencies.
  f.run("AGENCIES=[{name:'CAMNEMI'},{name:'Sunrise Edu'}];");
  f.context.renderAgencies=()=>{};
  f.context.syncAgencies=()=>{};
  f.context.confirm=()=>true;
  f.context.saveDatabase=()=>{ f.context.__saved=true; };
  f.context.sbDelete=async (table, q)=>{ f.context.__deleted.push({table,q}); return []; };
  f.context.__deleted=[];
  f.loadFunction('deleteAgency');
  f.context.deleteAgency(1); // delete 'Sunrise Edu'
  assert.deepEqual(JSON.parse(JSON.stringify(f.run("AGENCIES.map(a=>a.name)"))),['CAMNEMI'],'removed locally');
  assert.equal(f.context.__deleted.length,1,'issued a DB delete');
  assert.ok(f.context.__deleted[0].table==='agencies','deletes from agencies table');
  assert.ok(f.context.__deleted[0].q.includes('Sunrise'),'targets the right agency');
  assert.ok(f.context.__saved,'persisted');
});
