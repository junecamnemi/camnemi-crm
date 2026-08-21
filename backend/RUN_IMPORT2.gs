/** ============================================================
 *  RUN_IMPORT2 — direct, verifiable import into the CRM Sheet
 *  ============================================================
 *  Run this in the SAME project where your app's /exec lives.
 *  It reads the source sheet, builds the 62 students, merges with
 *  the CURRENT CRM customers, and writes ALL rows straight to the
 *  "Customers" tab. Then it LOGS the actual sheet row count so we
 *  can confirm it persisted (the previous run's write got overwritten).
 * ============================================================
 */
function RUN_IMPORT2() {
  var SRC_ID = '1vfzCRuHi-VviCj3z8BXTg76kw7wK1xJlSw-yCVSavec';
  var ss = SpreadsheetApp.openById(SRC_ID);
  Logger.log('Source tabs: ' + ss.getSheets().map(function(s){return s.getName();}).join(', '));
  // Find the tab containing the 'Students Name' header, else first
  var sheet = null;
  var all = ss.getSheets();
  for (var si = 0; si < all.length; si++) {
    var t = all[si].getDataRange().getValues();
    if (t.length > 0 && String(t[0][0] || '').toLowerCase().indexOf('students') !== -1) { sheet = all[si]; break; }
  }
  if (!sheet) sheet = all[0];
  var values = sheet.getDataRange().getValues();
  Logger.log('Using tab: ' + sheet.getName() + ', rows=' + values.length);

  var schoolMap = { 'KWU':'경운대학교','JBNU':'전북대학교','DDWU':'동덕여자대학교' };
  var progMap   = { 'D2':'BA','D4':'D4','MA':'MA','D-2':'BA','D-4':'D4' };
  var agencyCanon = {
    'camnemi':'CAMNEMI','costa':'COSTA','khema':'Khema','kimsous':'Kimsous',
    'senchao':'Sen Chao','jk':'JK','dinlina':'Din Lina'
  };
  var monthMap = { jan:'01',feb:'02',mar:'03',apr:'04',may:'05',jun:'06',
                   jul:'07',aug:'08',sep:'09',oct:'10',nov:'11',dec:'12' };

  var imported = [];
  for (var r = 1; r < values.length; r++) {
    var name = String(values[r][0] || '').trim();
    if (!name) continue;
    var enter   = String(values[r][1] || '').trim();
    var school  = String(values[r][2] || '').trim();
    var program = String(values[r][3] || '').trim();
    var status  = String(values[r][4] || '').trim().toLowerCase();
    var loan    = String(values[r][5] || '').trim().replace(/[$\s,]/g, '');
    var illegal = String(values[r][6] || '').trim().toLowerCase();
    var agency  = String(values[r][7] || '').trim();

    var appdate = '202609';
    // Enter may be a Date object (e.g. Sep 1 2026) or string "2026/Sep"
    if (enter instanceof Date) {
      appdate = enter.getFullYear() + ('0' + (enter.getMonth()+1)).slice(-2);
    } else {
      var parts = enter.split('/');
      if (parts.length === 2) {
        var mo = monthMap[String(parts[1]).toLowerCase().slice(0,3)] || '01';
        appdate = parts[0] + mo;
      }
    }

    var pipe, stage, denied;
    if (status === 'approved')      { pipe='korea'; stage='welcome'; denied=''; }
    else if (status === 'denied')   { pipe='new';   stage='archived'; denied='true'; }
    else                            { pipe='new';   stage='visa';     denied=''; }

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
  Logger.log('Parsed ' + imported.length + ' students from source.');

  // Read CURRENT CRM customers from the actual sheet
  var crm = getSheet();
  var crmCustomers = readSheetToData().customers || [];
  Logger.log('CRM had ' + crmCustomers.length + ' customers.');

  // Merge: drop old imp_ rows, add new
  crmCustomers = crmCustomers.filter(function(c){ return String(c.id||'').indexOf('imp_') !== 0; });
  imported.forEach(function(s){ crmCustomers.push(s); });

  // Write ALL directly to the sheet Customers tab
  var data = { version:1, customers: crmCustomers, agencies:[], partners:[], tasks:[], transactions:[], recs:[] };
  writeSheetFromData(data);
  // ALSO persist to JSON file
  saveData(JSON.stringify(data));

  // VERIFY by reading back the sheet
  var sh = crm.getSheetByName('Customers');
  var finalRows = sh.getLastRow();
  var check = readSheetToData().customers || [];
  Logger.log('FINAL Customers tab rows (incl header): ' + finalRows);
  Logger.log('FINAL customers read back: ' + check.length);
  Logger.log('Has MAO NITA: ' + check.some(function(c){ return (c.name||'').toUpperCase()==='MAO NITA'; }));
  return imported.length;
}
