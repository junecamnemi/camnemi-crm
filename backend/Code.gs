/**
 * Camnemi CRM — Google Drive Backend + Google Sheet Mirror
 * =========================================================
 * Stores CRM data in a JSON file AND mirrors it into a Google Sheet
 * so you can edit data directly in a spreadsheet (much friendlier
 * than raw JSON). Two-way:
 *   - App pushes data  -> backend saves JSON + updates the Sheet
 *   - You edit the Sheet -> app can pull via ?action=readSheet
 *
 * DEPLOY:
 *   1. https://script.google.com → New project
 *   2. Paste this file into Code.gs
 *   3. Save → Deploy → New deployment → Web app
 *   4. Execute as: Me ; Who has access: Anyone
 *   5. Approve the Google Drive + Sheets permissions.
 */

var FILE_NAME = 'camnemi_crm_data.json';
var FILE_ID_KEY = 'CAMNEMI_DRIVE_FILE_ID';
var SHEET_NAME = 'Camnemi CRM';
var SHEET_ID_KEY = 'CAMNEMI_SHEET_ID';

function doGet(e) {
  return handle(e, false);
}
function doPost(e) {
  return handle(e, true);
}

function handle(e, isPost) {
  try {
    var body = {};
    if (isPost) body = JSON.parse(e.postData.contents);

    // ACTION: pull data back from the Sheet (after manual edits)
    if (body.action === 'importFromSheet') {
      return importFromSheet(body);
    }
    if (body.action === 'readSheet') {
      return jsonOut(readSheetToData());
    }
    // ACTION: return the Google Sheet URL + ID (so the user can open/edit it)
    if (body.action === 'getSheetInfo') {
      var ss = getSheet();
      return jsonOut({ sheetUrl: 'https://docs.google.com/spreadsheets/d/' + ss.getId() + '/edit', sheetId: ss.getId(), name: ss.getName() });
    }
    // ACTION: list files in a student's folder (find by name under root)
    if (body.action === 'listStudentFolderFiles') {
      return listStudentFolderFiles(body);
    }
    // ACTION: rename a student's folder (find by old name, rename to new name)
    if (body.action === 'renameStudentFolder') {
      return renameStudentFolder(body);
    }
    // ACTION: rename a file inside a student's folder
    if (body.action === 'renameStudentFile') {
      return renameStudentFile(body);
    }
    // ACTION: find a student's docs (recursive) and copy them into a clean per-student folder
    if (body.action === 'copyStudentDocs') {
      return copyStudentDocs(body);
    }
    // ACTION: get/create the shared Agency Submissions spreadsheet
    if (body.action === 'getAgencySubmissions') {
      return getAgencySubmissions();
    }
    // ACTION: pull agency submissions from the shared sheet into customers
    if (body.action === 'pullAgencySubmissions') {
      return pullAgencySubmissions();
    }
    // ACTION: add an agency-submitted contact directly to the Sheet (reliable cross-browser)
    if (body.action === 'addAgencyContact') {
      return addAgencyContact(body);
    }
    // ACTION: upload a guide PDF to a Drive folder
    if (body.action === 'upload') {
      return uploadGuide(body);
    }
    // ACTION: get/create the shared Wiki document folder
    if (body.action === 'getWikiFolder') {
      return getWikiFolderBackend();
    }
    // ACTION: create a per-customer document folder (called when customer reaches Registration)
    if (body.action === 'createFolder') {
      return createCustomerFolder(body);
    }
    // ACTION: upload a file into a customer's folder
    if (body.action === 'uploadCustomerFile') {
      return uploadCustomerFile(body);
    }

    var data = getDataFile().getBlob().getDataAsString('UTF-8');
    if (isPost && body.data !== undefined) {
      saveData(JSON.stringify(body.data, null, 2));
      data = JSON.stringify(body.data);
    }
    return jsonOut(JSON.parse(data));
  } catch (err) {
    return jsonOut({ error: String(err) });
  }
}

/** Save data to JSON file AND update the mirror Sheet. */
/** Import students from an external source Sheet into the CRM customers.
 *  Expects source Sheet: Students Name | Enter | School | Program | Status | Loan | Illegal | Agency
 *  Status: Approved -> korea/welcome, Accepted -> new/visa, Denied -> new/archived
 */
function importFromSheet(body) {
  var srcId = String(body.sheetId || '').trim();
  if (!srcId) return { ok:false, error:'sheetId required' };
  var ss = SpreadsheetApp.openById(srcId);
  var sheet = ss.getSheets()[0];
  var values = sheet.getDataRange().getValues();
  if (values.length < 2) return { ok:true, imported:0, error:'no data rows' };
  var headers = values[0].map(function(h){ return String(h).toLowerCase().replace(/\s+/g,'_'); });
  var schoolMap = { 'KWU':'경운대학교','JBNU':'전북대학교','DDWU':'동덕여자대학교' };
  var progMap = { 'D2':'BA','D4':'D4','MA':'MA','D-2':'BA','D-4':'D4' };
  var agencyCanon = { 'camnemi':'CAMNEMI','costa':'COSTA','khema':'Khema','kimsous':'Kimsous','senchao':'Sen Chao','jk':'JK','dinlina':'Din Lina' };
  var monthMap = { jan:'01',feb:'02',mar:'03',apr:'04',may:'05',jun:'06',jul:'07',aug:'08',sep:'09',oct:'10',nov:'11',dec:'12' };
  var imported = [];
  for (var r=1; r<values.length; r++) {
    var name = String(values[r][0] || '').trim();
    if (!name) continue;
    var enter = String(values[r][1] || '').trim();
    var school = String(values[r][2] || '').trim();
    var program = String(values[r][3] || '').trim();
    var status = String(values[r][4] || '').trim().toLowerCase();
    var loan = String(values[r][5] || '').trim().replace(/[$\s,]/g,'');
    var illegal = String(values[r][6] || '').trim().toLowerCase();
    var agency = String(values[r][7] || '').trim();
    var appdate = '202609';
    var parts = enter.split('/');
    if (parts.length === 2) {
      var mo = monthMap[String(parts[1]).toLowerCase().slice(0,3)] || '01';
      appdate = parts[0] + mo;
    }
    var sch = schoolMap[String(school).toUpperCase()] || school;
    var prog = progMap[String(program).toUpperCase()] || program;
    var ag = agencyCanon[String(agency).toLowerCase().replace(/\s+/g,'')] || (agency || 'CAMNEMI');
    var pipe, stage, denied;
    if (status === 'approved') { pipe='korea'; stage='welcome'; denied=''; }
    else if (status === 'denied') { pipe='new'; stage='archived'; denied='true'; }
    else { pipe='new'; stage='visa'; denied=''; }
    imported.push({
      id:'imp_'+name.replace(/[^a-z0-9]/gi,'').toLowerCase() + '_' + r,
      pipe:pipe, stage:stage, name:name,
      school:sch, program:prog, appdate:appdate,
      agency:ag, loan:loan, illegal:(illegal==='illegal')?'true':'',
      denied:denied, noqr:'', contact:'', email:'', notes:[], birthdate:''
    });
  }
  var data = readSheetToData();
  var customers = data.customers || [];
  customers = customers.filter(function(c){ return String(c.id||'').indexOf('imp_') !== 0; });
  imported.forEach(function(s){ customers.push(s); });
  data.customers = customers;
  saveData(JSON.stringify(data));
  return { ok:true, imported: imported.length, total: customers.length };
}

function saveData(jsonString) {
  var data = JSON.parse(jsonString);
  getDataFile().setContent(jsonString);
  writeSheetFromData(data);
  return true;
}

/** ============ GOOGLE SHEET MIRROR ============ */

function getSheet() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(SHEET_ID_KEY);
  var ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (err) { ss = null; } }
  if (!ss) {
    var files = DriveApp.getFilesByName(SHEET_NAME);
    while (files.hasNext()) {
      var c = files.next();
      if (c.getMimeType() === 'application/vnd.google-apps.spreadsheet') { ss = SpreadsheetApp.open(c); break; }
    }
  }
  if (!ss) {
    ss = SpreadsheetApp.create(SHEET_NAME);
    props.setProperty(SHEET_ID_KEY, ss.getId());
  }
  return ss;
}

/** Write all data arrays into the Sheet tabs. */
function addAgencyContact(body) {
  // body.student = { id, pipe, stage, name, agency, program, contact, school, appdate, notes }
  var s = body.student || {};
  if (!s.name || !s.id) return { ok:false, error:'name and id required' };
  var ss = getSheet();
  // Read current customers from the Sheet (stable, no cache issue)
  var data = readSheetToData();
  var customers = data.customers || [];
  // dedupe by id
  customers = customers.filter(function(c){ return c.id !== s.id; });
  customers.push({
    id: s.id, pipe: s.pipe || 'new', stage: s.stage || 'contact',
    name: s.name, age: s.age || '', agency: s.agency || 'CAMNEMI',
    program: s.program || 'Not Yet', school: s.school || 'Not Yet Specified',
    appdate: s.appdate || 'Not Specified', contact: s.contact || '',
    email: s.email || '', loan: s.loan || '', topik: s.topik || '', ielts: s.ielts || '',
    notes: s.notes || [], birthdate: s.birthdate || ''
  });
  data.customers = customers;
  // write back to the JSON file (which saveData also mirrors to Sheet)
  saveData(JSON.stringify(data));
  return { ok:true, total: customers.length, added: s.name };
}

function writeSheetFromData(data) {
  var ss = getSheet();
  var tabs = [
    { name: 'Customers', cols: ['id','pipe','stage','name','age','agency','program','school','appdate','contact','email','loan','topik','ielts','notes','birthdate','noqr','illegal','denied','loanFlag','payments','recent','folderId','folderUrl'], rows: data.customers || [] },
    { name: 'Agencies',  cols: ['name','commission','policy'], rows: data.agencies || [] },
    { name: 'Partners',  cols: ['name','note'], rows: (data.partners||[]).map(p => [p.name, p.note||p.policy||'']) },
    { name: 'Tasks',     cols: ['date','type','title','note'], rows: data.tasks || [] },
    { name: 'Transactions', cols: ['date','type','category','amount','note'], rows: (data.transactions||[]).map(t => [t.date, t.type, t.cat, t.amount, t.note]) },
    { name: 'Recs',      cols: ['col','title','note'], rows: (data.recs||[]).map(r => [r.col, r.title, r.note]) }
  ];
  tabs.forEach(function(t) {
    var sh = ss.getSheetByName(t.name);
    if (!sh) sh = ss.insertSheet(t.name);
    sh.clear();
    // header
    sh.getRange(1,1,1,t.cols.length).setValues([t.cols]).setFontWeight('bold').setBackground('#1E293B').setFontColor('#FFFFFF');
    // rows
    var values = t.rows.map(function(r){
      if (Array.isArray(r)) return r.map(cellStr);
      return t.cols.map(function(c){ return cellStr(r[c]); });
    });
    if (values.length) sh.getRange(2,1,values.length,t.cols.length).setValues(values);
    sh.autoResizeColumns(1, t.cols.length);
  });
  return true;
}

/** Read data back from the Sheet (source of truth when user edits). */
function readSheetToData() {
  var ss = getSheet();
  var data = { version:1, customers:[], agencies:[], partners:[], tasks:[], transactions:[], recs:[] };
  function readTab(name, cols, mapRow) {
    var sh = ss.getSheetByName(name); if (!sh) return [];
    var last = sh.getLastRow(); if (last < 2) return [];
    var width = cols.length;
    var vals = sh.getRange(2,1,last-1,width).getValues();
    var out = [];
    for (var i=0;i<vals.length;i++) {
      var row = vals[i];
      if (!row[0] && !row[1]) continue;  // skip blank
      var obj = {};
      cols.forEach(function(c,idx){ obj[c] = row[idx]; });
      out.push(mapRow ? mapRow(obj) : obj);
    }
    return out;
  }
  data.customers = readTab('Customers', ['id','pipe','stage','name','age','agency','program','school','appdate','contact','email','loan','topik','ielts','notes','birthdate','noqr','illegal','denied','loanFlag','payments','recent','folderId','folderUrl'], function(o){
    var notes = [];
    try { if (o.notes) notes = JSON.parse(o.notes); } catch(e){ if(o.notes) notes=[{text:String(o.notes),time:''}]; }
    var payments = [];
    try { if (o.payments) payments = JSON.parse(o.payments); } catch(e){}
    return {
      id: String(o.id||('c'+Date.now())), pipe: String(o.pipe||'new'), stage: String(o.stage||'contact'),
      name: String(o.name||''), age: String(o.age||''), agency: String(o.agency||''),
      program: String(o.program||''), school: String(o.school||''), appdate: String(o.appdate||''),
      contact: String(o.contact||''), email: String(o.email||''), loan: String(o.loan||''),
      topik: String(o.topik||''), ielts: String(o.ielts||''), notes: notes, birthdate: String(o.birthdate||''),
      noqr: String(o.noqr||''), illegal: String(o.illegal||''), denied: String(o.denied||''),
      loanFlag: String(o.loanFlag||''), payments: payments, recent: String(o.recent||''),
      folderId: String(o.folderId||''), folderUrl: String(o.folderUrl||'')
    };
  });
  data.agencies = readTab('Agencies', ['name','commission','policy']);
  data.partners = readTab('Partners', ['name','note'], function(o){ return {name:o.name, note:o.note}; });
  data.tasks = readTab('Tasks', ['date','type','title','note']);
  data.transactions = readTab('Transactions', ['date','type','category','amount','note'], function(o){
    return { date:String(o.date||''), type:String(o.type||''), cat:String(o.category||''), amount:Number(o.amount)||0, note:String(o.note||'') };
  });
  data.recs = readTab('Recs', ['col','title','note'], function(o){ return { col:String(o.col||'problems'), title:String(o.title||''), note:String(o.note||'') }; });
  return data;
}


/** ============ AGENCY SUBMISSIONS SPREADSHEET ============ */
var AGENCY_SHEET_ID_KEY = 'AGENCY_SUBMISSIONS_SHEET_ID';
var AGENCY_SHEET_ID = '17sY2zMI9L30_0gQWrwFCnUEXc3H79IwtsSrYBGfj4dE';  // user's Agency Submissions sheet
var AGENCY_SHEET_NAME = 'Camnemi Agency Submissions';
var AGENCY_COLS = ['name','contact','agency','program','note','date'];

// Get the dedicated agency submissions spreadsheet (uses the user's sheet).
function getAgencySheet() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(AGENCY_SHEET_ID_KEY) || AGENCY_SHEET_ID;
  var ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch(err){ ss=null; } }
  if (!ss) {
    // fall back to creating a new one with the right headers + sharing
    ss = SpreadsheetApp.create(AGENCY_SHEET_NAME);
    props.setProperty(AGENCY_SHEET_ID_KEY, ss.getId());
    var sh = ss.getSheetByName('Sheet1'); if (sh) sh.setName('Agency Submissions');
    var sh2 = ss.getSheetByName('Agency Submissions'); if(!sh2) sh2 = ss.insertSheet('Agency Submissions');
    sh2.getRange(1,1,1,AGENCY_COLS.length).setValues([AGENCY_COLS]).setFontWeight('bold').setBackground('#1E293B').setFontColor('#FFFFFF');
    sh2.autoResizeColumns(1, AGENCY_COLS.length);
    ss.getViewers().forEach(function(u){ try{ ss.addEditor(u); }catch(e){} });
  }
  // make sure the 'Agency Submissions' tab has headers
  var sh = ss.getSheetByName('Agency Submissions');
  if (sh && sh.getLastRow() < 1) {
    sh.getRange(1,1,1,AGENCY_COLS.length).setValues([AGENCY_COLS]).setFontWeight('bold').setBackground('#1E293B').setFontColor('#FFFFFF');
  }
  return ss;
}
// ACTION handler: get agency submissions link + data
function getAgencySubmissions() {
  var ss = getAgencySheet();
  return { ok:true, sheetUrl:'https://docs.google.com/spreadsheets/d/'+ss.getId()+'/edit', sheetId: ss.getId() };
}
// ACTION handler: pull agency submissions from the sheet into customers
function pullAgencySubmissions() {
  var ss = getAgencySheet();
  var sh = (ss.getSheetByName('Agency Submissions')) || ss.getSheets()[0];
  var data = { customers: [] };
  if (!sh) return data;
  var last = sh.getLastRow();
  if (last < 2) return data;
  var vals = sh.getRange(2,1,last-1,AGENCY_COLS.length).getValues();
  for (var i=0;i<vals.length;i++) {
    var r = vals[i];
    var name = String(r[0]||'').trim();
    if (!name) continue;
    data.customers.push({
      id:'c'+Date.now()+Math.floor(Math.random()*1000),
      pipe:'new', stage:'contact', name:name.toUpperCase(),
      age:'', agency:String(r[2]||'CAMNEMI').trim()||'CAMNEMI',
      program:String(r[3]||'Not Yet')||'Not Yet',
      school:'Not Yet Specified', appdate:'Not Specified',
      contact:String(r[1]||''), email:'', loan:'', topik:'', ielts:'',
      notes: r[4] ? JSON.stringify([{text:String(r[4]),time:''}]) : '[]',
      birthdate:''
    });
  }
  return data;
}
/** ============ GUIDE PDF UPLOAD ============ */

function uploadGuide(body) {
  var folderId = body.folderId, filename = body.filename, b64 = body.contentBase64;
  if (!folderId || !filename || !b64) return jsonOut({ error: 'Missing folderId/filename/contentBase64' });
  var folder = DriveApp.getFolderById(folderId);
  var blob = Utilities.newBlob(Utilities.base64Decode(b64, Utilities.Charset.UTF_8), 'application/pdf', filename);
  var file = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return jsonOut({ ok:true, fileId:file.getId(), name:file.getName(),
    link:'https://drive.google.com/uc?export=download&id='+file.getId(),
    viewLink:'https://drive.google.com/file/d/'+file.getId()+'/view', size:blob.getBytes().length });
}

/** ============ WIKI DOCUMENT FOLDER ============ */
var WIKI_FOLDER_KEY = 'CAMNEMI_WIKI_FOLDER_ID';
function getWikiFolderBackend() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(WIKI_FOLDER_KEY);
  var folder = null;
  if (id) { try { folder = DriveApp.getFolderById(id); } catch(err){ folder=null; } }
  if (!folder) {
    var files = DriveApp.getFoldersByName('Camnemi Wiki Documents');
    if (files.hasNext()) folder = files.next();
  }
  if (!folder) { folder = DriveApp.createFolder('Camnemi Wiki Documents'); props.setProperty(WIKI_FOLDER_KEY, folder.getId()); }
  return jsonOut({ ok:true, folderId:folder.getId(), folderUrl:'https://drive.google.com/drive/folders/'+folder.getId() });
}

/** ============ CUSTOMER DOCUMENT FOLDERS ============ */

// Root folder in Drive that holds all customer document folders.
var CUSTOMER_ROOT_NAME = 'Camnemi Customer Docs';
var CUSTOMER_ROOT_FIXED_ID = '1FB40aQQokZy2KDEl1AEHG3RHUzo5rd1S';  // user's real students-files parent folder
var CUSTOMER_ROOT_KEY = 'CAMNEMI_CUSTOMER_ROOT_ID';

function getCustomerRoot() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(CUSTOMER_ROOT_KEY);
  var folder = null;
  // Prefer the user's real students-files root folder (1FB40aQQ...)
  if (CUSTOMER_ROOT_FIXED_ID) { try { folder = DriveApp.getFolderById(CUSTOMER_ROOT_FIXED_ID); } catch(err){ folder=null; } }
  // Only fall back to the saved property if the fixed root is not usable
  if (!folder && id) { try { folder = DriveApp.getFolderById(id); } catch(err){ folder=null; } }
  if (!folder) {
    var files = DriveApp.getFoldersByName(CUSTOMER_ROOT_NAME);
    if (files.hasNext()) folder = files.next();
  }
  if (!folder) { folder = DriveApp.createFolder(CUSTOMER_ROOT_NAME); props.setProperty(CUSTOMER_ROOT_KEY, folder.getId()); }
  return folder;
}

/**
 * Create a folder for one customer.
 * POST: { action:'createFolder', name:'CHEA MONTHANRONGRATH', month:'202503', school:'Jeonbuk' }
 * Folder name is just the student's name (month/school ignored).
 */
function createCustomerFolder(body) {
  var name = String(body.name || '').trim();
  if (!name) return jsonOut({ error: 'Missing name' });
  var label = name.replace(/[\\/:*?"<>|]/g, '').trim();  // sanitize
  var labelLc = label.toLowerCase();

  var root = getCustomerRoot();
  // avoid duplicates: case-insensitive find existing folder with same name under root
  var folder = null;
  var fit = root.getFolders();
  while (fit.hasNext()) { var ff = fit.next(); if (ff.getName().trim().toLowerCase() === labelLc) { folder = ff; break; } }
  if (!folder) folder = root.createFolder(label);
  return jsonOut({
    ok: true, folderId: folder.getId(), name: folder.getName(),
    folderUrl: 'https://drive.google.com/drive/folders/' + folder.getId()
  });
}

/** List files inside a student's folder (finds folder by name under root). */
var STUDENT_INDEX_KEY = 'CAMNEMI_STUDENT_FOLDER_INDEX';
var STUDENT_INDEX_TS_KEY = 'CAMNEMI_STUDENT_INDEX_TS';

// Build (and cache) a map of studentName(lowercase) -> folderId by scanning the root once.
function getStudentFolderIndex(forceRebuild) {
  var props = PropertiesService.getScriptProperties();
  var ts = parseInt(props.getProperty(STUDENT_INDEX_TS_KEY) || '0', 10);
  var now = Date.now();
  // cache for 30 min, or force rebuild
  if (!forceRebuild && ts && (now - ts) < 30*60*1000) {
    var cached = props.getProperty(STUDENT_INDEX_KEY);
    if (cached) { try { return JSON.parse(cached); } catch(e){} }
  }
  var root = getCustomerRoot();
  var index = {};
  var stack = []; var it = root.getFolders(); while (it.hasNext()) stack.push(it.next());
  while (stack.length > 0) {
    var f = stack.pop();
    var nm = f.getName().replace(/[\\/:*?"<>|]/g,'').trim().toLowerCase();
    if (nm && !index[nm]) index[nm] = f.getId();
    var sub = f.getFolders(); while (sub.hasNext()) stack.push(sub.next());
  }
  props.setProperty(STUDENT_INDEX_KEY, JSON.stringify(index));
  props.setProperty(STUDENT_INDEX_TS_KEY, String(now));
  return index;
}

function listStudentFolderFiles(body) {
  var name = String(body.name || '').trim();
  if (!name) return jsonOut({ ok:false, error:'Missing name' });
  var label = name.replace(/[\\/:*?"<>|]/g, '').trim().toLowerCase();
  var index = getStudentFolderIndex(false);
  var folderId = index[label];
  if (!folderId) {
    // not in index: rebuild once in case folder is new
    index = getStudentFolderIndex(true);
    folderId = index[label];
  }
  if (!folderId) return jsonOut({ ok:true, found:false, files:[] });
  var folder = DriveApp.getFolderById(folderId);
  var files = [];
  var fIt = folder.getFiles();
  while (fIt.hasNext()) {
    var f = fIt.next();
    files.push({ name: f.getName(), mime: f.getMimeType(), size: f.getSize(), url: f.getUrl() });
  }
  return jsonOut({ ok:true, found:true, folderId: folder.getId(), folderUrl: folder.getUrl(), files: files });
}

/** Rename a student's folder (find by old name under root, rename to new name). */
function renameStudentFolder(body) {
  var oldName = String(body.oldName || '').trim();
  var newName = String(body.newName || '').trim();
  if (!oldName || !newName) return jsonOut({ ok:false, error:'oldName and newName required' });
  var oldLabel = oldName.replace(/[\\/:*?"<>|]/g,'').trim().toLowerCase();
  var newLabel = newName.replace(/[\\/:*?"<>|]/g,'').trim();
  var index = getStudentFolderIndex(false);
  var folderId = index[oldLabel];
  if (!folderId) return jsonOut({ ok:true, renamed:false, error:'Source folder not found' });
  var folder = DriveApp.getFolderById(folderId);
  folder.setName(newLabel);
  // invalidate cache so the index picks up the new name
  PropertiesService.getScriptProperties().deleteProperty(STUDENT_INDEX_KEY);
  return jsonOut({ ok:true, renamed:true, folderId:folder.getId(), folderUrl:folder.getUrl() });
}

/** Rename a file inside a student's folder. */
function renameStudentFile(body) {
  var folderId = String(body.folderId || '').trim();
  var oldName = String(body.oldName || '').trim();
  var newName = String(body.newName || '').trim();
  if (!folderId || !oldName || !newName) return jsonOut({ ok:false, error:'folderId, oldName, newName required' });
  var folder = DriveApp.getFolderById(folderId);
  var it = folder.getFilesByName(oldName);
  if (!it.hasNext()) return jsonOut({ ok:true, renamed:false, error:'File not found' });
  var file = it.next();
  file.setName(newName);
  return jsonOut({ ok:true, renamed:true, fileId:file.getId(), name:file.getName(), url:file.getUrl() });
}

/** Find a student's folder recursively, copy all its files into a clean per-student folder, return the new link. */
function copyStudentDocs(body) {
  var name = String(body.name || '').trim();
  if (!name) return jsonOut({ ok:false, error:'Missing name' });
  var label = name.replace(/[\\/:*?"<>|]/g, '').trim().toLowerCase();

  var root = getCustomerRoot();
  // 1. find the student's source folder recursively
  var stack = []; var it = root.getFolders(); while (it.hasNext()) stack.push(it.next());
  var src = null;
  while (stack.length) {
    var f = stack.pop();
    if (f.getName().replace(/[\\/:*?"<>|]/g,'').trim().toLowerCase() === label) { src = f; break; }
    var sub = f.getFolders(); while (sub.hasNext()) stack.push(sub.next());
  }
  if (!src) return jsonOut({ ok:false, error:'Source folder not found for ' + name });

  // 2. destination: per-student folder directly under root (clean)
  var dest = null;
  var dit = root.getFolders();
  while (dit.hasNext()) { var df = dit.next(); if (df.getName().trim().toLowerCase() === label) { dest = df; break; } }
  if (!dest) dest = root.createFolder(name);

  // 3. copy all files from source to dest (skip files already there by name)
  var copied = 0; var already = 0; var total = 0;
  var fit = src.getFiles();
  while (fit.hasNext()) {
    var file = fit.next();
    total++;
    // skip if dest already has a file with same name
    var existing = dest.getFilesByName(file.getName());
    if (existing.hasNext()) { already++; continue; }
    file.makeCopy(file.getName(), dest);
    copied++;
  }
  return jsonOut({ ok:true, found:true, copied:copied, already:already, total:total,
    folderId: dest.getId(), folderUrl: 'https://drive.google.com/drive/folders/' + dest.getId() });
}

/**
 * Upload a file into a customer's folder.
 * POST: { action:'uploadCustomerFile', folderId:'...', filename:'...', contentBase64:'...', mime:'application/pdf' }
 */
function uploadCustomerFile(body) {
  var folderId = body.folderId, filename = body.filename, b64 = body.contentBase64;
  if (!folderId || !filename || !b64) return jsonOut({ error: 'Missing folderId/filename/contentBase64' });
  var folder = DriveApp.getFolderById(folderId);
  var mime = body.mime || 'application/octet-stream';
  var blob = Utilities.newBlob(Utilities.base64Decode(b64, Utilities.Charset.UTF_8), mime, filename);
  var file = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return jsonOut({ ok:true, fileId:file.getId(), name:file.getName(), size:blob.getBytes().length,
    viewLink:'https://drive.google.com/file/d/'+file.getId()+'/view' });
}

/** ============ HELPERS ============ */

function cellStr(v) {
  if (v === null || v === undefined) return '';
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

function getDataFile() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(FILE_ID_KEY);
  var file = null;
  if (id) { try { file = DriveApp.getFileById(id); } catch(err){ file=null; } }
  if (!file) {
    var files = DriveApp.getFilesByName(FILE_NAME);
    while (files.hasNext()) { var c=files.next(); if(c.getMimeType()==='application/json'){ file=c; break; } }
  }
  if (!file) { file = DriveApp.createFile(FILE_NAME, '{}', 'application/json'); props.setProperty(FILE_ID_KEY, file.getId()); }
  return file;
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function seedData(jsonString) { saveData(jsonString); return 'Seeded.'; }

/**
 * RUN THIS in the Apps Script editor (no arguments) to create the Sheet
 * and trigger the Google Sheets permission grant.
 * Select this function in the toolbar dropdown, then press Run → Allow.
 */
function createSheetManual() {
  var ss = getSheet();
  writeSheetFromData({ version:1, customers:[], agencies:[], partners:[], tasks:[], transactions:[], recs:[] });
  return 'Sheet created: https://docs.google.com/spreadsheets/d/' + ss.getId() + '/edit';
}

function testSheet() {
  return createSheetManual();
}
