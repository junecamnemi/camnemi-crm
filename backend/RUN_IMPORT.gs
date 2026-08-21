/** ============================================================
 *  ONE-TIME IMPORT — run ONCE in the Apps Script editor
 *  ============================================================
 *  1. Open your "camnemi crm" Apps Script project
 *  2. Click the file "Code.gs" in the left panel
 *  3. Paste THIS WHOLE FILE's content at the END of Code.gs
 *  4. Click the Run ▷ button with the function name "RUN_IMPORT"
 *  5. Authorize if asked (SpreadsheetApp + DriveApp permissions)
 *  6. Check the log (View → Logs) for the result
 *  This imports students from your external sheet into the CRM backend.
 * ============================================================
 */
function RUN_IMPORT() {
  // Source sheet (the one you shared for this import):
  var SRC_ID = '1vfzCRuHi-VviCj3z8BXTg76kw7wK1xJlSw-yCVSavec';

  var ss = SpreadsheetApp.openById(SRC_ID);
  Logger.log('Sheets in source: ' + ss.getSheets().map(function(s){return s.getName();}).join(', '));
  // Find the tab that has the data (look for the one containing 'Students Name' header, else first)
  var sheet = null;
  var all = ss.getSheets();
  for (var si = 0; si < all.length; si++) {
    var test = all[si].getDataRange().getValues();
    if (test.length > 0 && String(test[0][0] || '').toLowerCase().indexOf('students') !== -1) { sheet = all[si]; break; }
  }
  if (!sheet) sheet = all[0];
  var values = sheet.getDataRange().getValues();
  Logger.log('Using tab: ' + sheet.getName() + ', rows=' + values.length);
  if (values.length < 2) { Logger.log('No data rows in tab'); }

  // School / program / agency maps
  var schoolMap = { 'KWU':'경운대학교','JBNU':'전북대학교','DDWU':'동덕여자대학교' };
  var progMap   = { 'D2':'BA','D4':'D4','MA':'MA','D-2':'BA','D-4':'D4' };
  var agencyCanon = {
    'camnemi':'CAMNEMI','costa':'COSTA','khema':'Khema','kimsous':'Kimsous',
    'senchao':'Sen Chao','jk':'JK','dinlina':'Din Lina'
  };
  var monthMap = { jan:'01',feb:'02',mar:'03',apr:'04',may:'05',jun:'06',
                   jul:'07',aug:'08',sep:'09',oct:'10',nov:'11',dec:'12' };

  if (values.length > 1) { Logger.log('Header: ' + values[0].join(' | ')); Logger.log('Row1: ' + values[1].join(' | ')); }
  var imported = [];
  for (var r = 1; r < values.length; r++) {
    var name = String(values[r][0] || '').trim();
    if (!name) continue;
    var enter   = String(values[r][1] || '').trim();  // e.g. 2026/Sep
    var school  = String(values[r][2] || '').trim();  // KWU / JBNU / DDWU
    var program = String(values[r][3] || '').trim();  // D2 / D4 / MA
    var status  = String(values[r][4] || '').trim().toLowerCase(); // Approved/Accepted/Denied
    var loan    = String(values[r][5] || '').trim().replace(/[$,\s]/g, '');
    var illegal = String(values[r][6] || '').trim().toLowerCase();
    var agency  = String(values[r][7] || '').trim();

    // Enter -> appdate (YYYYMM)
    var appdate = '202609';
    var parts = enter.split('/');
    if (parts.length === 2) {
      var mo = monthMap[String(parts[1]).toLowerCase().slice(0,3)] || '01';
      appdate = parts[0] + mo;
    }

    // status mapping
    var pipe, stage, denied;
    if (status === 'approved')      { pipe='korea'; stage='welcome'; denied=''; }
    else if (status === 'denied')   { pipe='new';   stage='archived'; denied='true'; }
    else                            { pipe='new';   stage='visa';     denied=''; } // Accepted

    imported.push({
      id: 'imp_' + name.replace(/[^a-z0-9]/gi,'').toLowerCase() + '_' + r,
      pipe: pipe, stage: stage, name: name,
      school: schoolMap[String(school).toUpperCase()] || school,
      program: progMap[String(program).toUpperCase()] || program,
      appdate: appdate,
      agency: agencyCanon[String(agency).toLowerCase().replace(/\s+/g,'')] || (agency || 'CAMNEMI'),
      loan: loan,
      illegal: (illegal === 'illegal') ? 'true' : '',
      denied: denied, noqr: '', contact: '', email: '', notes: [], birthdate: ''
    });
  }

  // Merge into current CRM data (remove old imp_ rows so re-runs are safe)
  var data = readSheetToData();
  var customers = data.customers || [];
  customers = customers.filter(function(c){ return String(c.id||'').indexOf('imp_') !== 0; });
  imported.forEach(function(s){ customers.push(s); });
  data.customers = customers;
  saveData(JSON.stringify(data));

  Logger.log('IMPORTED ' + imported.length + ' students. Total in CRM now: ' + customers.length);
  return imported.length;
}
