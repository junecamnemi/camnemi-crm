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
    if (body.action === 'readSheet') {
      return jsonOut(readSheetToData());
    }
    // ACTION: return the Google Sheet URL + ID (so the user can open/edit it)
    if (body.action === 'getSheetInfo') {
      var ss = getSheet();
      return jsonOut({ sheetUrl: 'https://docs.google.com/spreadsheets/d/' + ss.getId() + '/edit', sheetId: ss.getId(), name: ss.getName() });
    }
    // ACTION: upload a guide PDF to a Drive folder
    if (body.action === 'upload') {
      return uploadGuide(body);
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
function writeSheetFromData(data) {
  var ss = getSheet();
  var tabs = [
    { name: 'Customers', cols: ['id','pipe','stage','name','age','agency','program','school','appdate','contact','email','loan','topik','ielts','notes','birthdate'], rows: data.customers || [] },
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
  data.customers = readTab('Customers', ['id','pipe','stage','name','age','agency','program','school','appdate','contact','email','loan','topik','ielts','notes','birthdate'], function(o){
    var notes = [];
    try { if (o.notes) notes = JSON.parse(o.notes); } catch(e){ if(o.notes) notes=[{text:String(o.notes),time:''}]; }
    return {
      id: String(o.id||('c'+Date.now())), pipe: String(o.pipe||'new'), stage: String(o.stage||'contact'),
      name: String(o.name||''), age: String(o.age||''), agency: String(o.agency||''),
      program: String(o.program||''), school: String(o.school||''), appdate: String(o.appdate||''),
      contact: String(o.contact||''), email: String(o.email||''), loan: String(o.loan||''),
      topik: String(o.topik||''), ielts: String(o.ielts||''), notes: notes, birthdate: String(o.birthdate||'')
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

/** ============ CUSTOMER DOCUMENT FOLDERS ============ */

// Root folder in Drive that holds all customer document folders.
var CUSTOMER_ROOT_NAME = 'Camnemi Customer Docs';
var CUSTOMER_ROOT_KEY = 'CAMNEMI_CUSTOMER_ROOT_ID';

function getCustomerRoot() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(CUSTOMER_ROOT_KEY);
  var folder = null;
  if (id) { try { folder = DriveApp.getFolderById(id); } catch(err){ folder=null; } }
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

  var root = getCustomerRoot();
  // avoid duplicates: find existing folder with same name under root
  var existing = root.getFoldersByName(label);
  var folder = existing.hasNext() ? existing.next() : root.createFolder(label);
  return jsonOut({
    ok: true, folderId: folder.getId(), name: folder.getName(),
    folderUrl: 'https://drive.google.com/drive/folders/' + folder.getId()
  });
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
