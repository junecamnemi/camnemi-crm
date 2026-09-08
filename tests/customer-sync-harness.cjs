const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
function sourceFunction(name) {
  const match = html.match(new RegExp('^  (?:async )?function ' + name + '\\([^]*?^  }', 'm'));
  if (!match) throw new Error('Missing source function ' + name);
  return match[0];
}
const clone = value => JSON.parse(JSON.stringify(value));
function fixture(initial = [], storage = new Map(), session = new Map()) {
  let cards = [], overlay = null;
  const calls = [], warnings = [], timers = [], events = new Map();
  let remote = clone(initial), fail = false, beforeRequest = null;
  const container = { appendChild(card) { if (!cards.includes(card)) cards.push(card); card.parentElement = this; }, getAttribute() { return 'registration'; } };
  const node = () => ({ _heading:{textContent:''}, id: '', dataset: {}, style: {}, classList: { add(){}, remove(){}, toggle(){} },
    querySelector(selector) { return selector === 'h4' ? this._heading : {checked:false}; }, querySelectorAll() { return []; },
    addEventListener(){}, setAttribute(){}, remove() { cards = cards.filter(c => c !== this); }, appendChild: container.appendChild });
  const document = {
    querySelectorAll(selector) { return selector.startsWith('.customer-card') ? cards.slice() : []; },
    querySelector(selector) { if (selector === '.modal-overlay') return overlay; if (selector.startsWith('.cards')) return container; return null; },
    getElementById(id) { return id === 'quick-add-modal' ? overlay : cards.find(c => c.id === id) || null; },
    createElement: node, body: { appendChild(){} }, addEventListener(){}
  };
  const local = map => ({ getItem:k=>map.get(k)||null, setItem:(k,v)=>map.set(k,String(v)), removeItem:k=>map.delete(k), get length(){return map.size;}, key:(i)=>Array.from(map.keys())[i]||null });
  const context = vm.createContext({ document, localStorage:local(storage), sessionStorage:local(session),
    console:{warn:(...args)=>warnings.push(args.map(String).join(' ')),log(){}}, Date, URLSearchParams,
    crypto:require('node:crypto').webcrypto, setTimeout:(fn,delay)=>{timers.push({fn,delay});return timers.length;},clearTimeout(){},
    currentView:'kanban', currentPipe:'new', STAGE_COLORS:{}, escapeHtml:s=>s,
    refreshCounts(){},refreshCardBody(){},applyCardBorder(){},attachCard(){},changeCount(){},renderList(){},
    logStudentName:c=>c.dataset.name,logAction(){},closeModal(){overlay=null;},mergeAgencies:a=>a,
    useSupabase:()=>true, backendUrl:()=>'', alert:m=>warnings.push(m),
    async supabaseFetch(url, options = {}) {
      const method = options.method || 'GET'; const body = options.body ? JSON.parse(options.body) : undefined;
      calls.push({url,method,body,headers:options.headers});
      if (beforeRequest) await beforeRequest({url,method,body});
      if (fail) throw new Error('offline fixture');
      const table = url.split('/rest/v1/')[1].split('?')[0];
      if (table !== 'customers') return [];
      const params = new URLSearchParams(url.split('?')[1]||'');
      const id = (params.get('id')||'').replace(/^eq\./,'');
      if (method === 'GET') return clone(id ? remote.filter(r=>r.id===id) : remote);
      if (method === 'DELETE') { remote=remote.filter(r=>r.id!==id); return []; }
      if (method === 'PATCH') { const row=remote.find(r=>r.id===id); if(row) Object.assign(row,body); return row ? [clone(row)] : []; }
      if (method === 'POST') { for(const r of Array.isArray(body)?body:[body]) {
        const old=remote.find(x=>x.id===r.id);
        if(old && !options.headers?.Prefer?.includes('merge-duplicates')) throw new Error('Supabase HTTP 409 duplicate');
        if(old) Object.assign(old,r); else remote.push(clone(r));
      } return clone(Array.isArray(body)?body:[body]); }
      throw new Error('Unexpected fixture request '+method+' '+url);
    }
  });
  context.window = context;
  vm.runInContext(`let __pushTimer=null; let __pendingPush=false; let __pendingPayload=null;
    const DB_KEY='camnemi_db_v1'; const ACTIVITY_KEY='camnemi_activity_log';
    let AGENCIES=[],FEES=[],PARTNERS=[],TASKS=[],TRANS=[],RECS=[],WIKI_NOTES=[],WIKI_DOCS=[],WIKI_CATS=[],ACTIVITY_LOG=[],LIST_CUSTOM_COLS=[],HIDDEN_LIST_COLS=[],LIST_COL_ORDER=[];`,context);
  const engine = html.match(/  \/\/ CUSTOMER SYNC OUTBOX START[^]*?  \/\/ CUSTOMER SYNC OUTBOX END/);
  if(engine) vm.runInContext(engine[0],context);
  const names=['sbSelect','sbUpsert','sbDelete','supabaseReadTables','supabaseWriteTables','exportAllData','applyDbToState','restoreCustomers','deleteCustomer','saveNow','saveDatabase','scheduleSyncPush','flushPendingPush'];
  vm.runInContext(names.map(sourceFunction).join('\n'),context);
  const syncStart=html.indexOf('  let __syncing = false;');
  vm.runInContext(html.slice(syncStart,html.indexOf('  // Pull data that was edited',syncStart)),context);
  vm.runInContext('__bootDone=true;',context);
  function setCards(rows) { context.__RESTORE_CUSTOMERS__=clone(rows); context.restoreCustomers(); }
  setCards(initial);
  return {context,calls,warnings,timers,events,storage,session,setCards,
    loadFunction:name=>vm.runInContext(sourceFunction(name),context),
    setOverlay:value=>{overlay=value;},
    bootSetup() {
      for(const name of ['loadActivityLog','loadActivityFromDb','normalizeAgencyData','loadWiki','syncWikiCount','syncAgencies','syncFees','initPartners','syncPartners','seedTasks','syncTasks','seedRecs','syncRecommendation','syncProfit','syncUniv','syncGksCount','syncMarketingCount','syncKoreaLifeCount','renderPipeline','reorderAllByRecent','rebuildFilterBar','onHashChange','routeFromHash','loadDataFile','autoPullAgencySubmissions']) context[name]=()=>{};
      Object.assign(context,{initAuth:()=>true,loadDatabase:()=>false,location:{hash:'',search:''},innerWidth:1200,addEventListener:(name,fn)=>events.set(name,fn),MutationObserver:class {observe(){}},ROUTES:{}});
      vm.runInContext(sourceFunction('bootApp'),context);
    },
    cards:()=>cards, remote:()=>clone(remote), setRemote:rows=>{remote=clone(rows);},
    setFail:v=>{fail=v;}, setBeforeRequest:fn=>{beforeRequest=fn;},
    edit(id, values) { Object.assign(cards.find(c=>c.id===id).dataset,values); },
    delete(id) { overlay={_card:cards.find(c=>c.id===id)}; context.deleteCustomer(); },
    run:code=>vm.runInContext(code,context), sourceFunction
  };
}
module.exports={fixture,sourceFunction,html};
