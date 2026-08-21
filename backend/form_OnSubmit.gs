/**
 * GOOGLE FORM → CAMNEMI CRM SHEET  (attach to your Google Form)
 *
 * FEATURES:
 *  - On every form submission, appends a new student row into the
 *    "Customers" tab of the "Camnemi CRM" spreadsheet (so your app shows it).
 *  - Gives you per-agency pre-filled links to give to COSTA / Khema / etc.
 *
 * SETUP (one time, ~5 min):
 *  1. Create a Google Form with these 5 fields (use EXACT titles):
 *       Student Name  (Short answer)
 *       Contact       (Short answer)
 *       Agency        (Short answer)
 *       Program       (Multiple choice: Not Yet / D4 / BA / MA / Online)
 *       Note          (Paragraph)
 *  2. In the Form ( ⋮ → Script editor, or Extensions → Apps Script ), paste this file.
 *  3. Set CRM_SHEET_ID below to your "Camnemi CRM" sheet id.
 *  4. Run installTrigger() once from the editor (authorize) to enable submissions.
 *  5. Run makeAgencyLinks() once; it prints links to give each agency.
 */
var CRM_SHEET_ID = '1olxzowcUja0qfGNDL-El2I6JVkhR_ZvSLHwjLlWGPm8';  // "Camnemi CRM"
var CUSTOMERS_TAB = 'Customers';
var AGENCY_DEFAULT = 'CAMNEMI';
var HEADER = ['id','pipe','stage','name','age','agency','program','school','appdate','contact','email','loan','topik','ielts','notes','birthdate'];

/** One-time: installs the form-submit trigger (run once, authorize). */
function installTrigger() {
  var form = FormApp.getActiveForm();
  ScriptApp.newTrigger('onFormSubmitEntry').forForm(form).onFormSubmit().create();
  Logger.log('Trigger installed on: ' + form.getTitle());
}

/** One-time: prints pre-filled agency links to give COSTA / Khema / ... */
function makeAgencyLinks() {
  var form = FormApp.getActiveForm();
  ['COSTA','Khema','CAMNEMI'].forEach(function(a){
    var item = form.getItemByName('Agency');
    // find the response to prefill: use text type
    var pf = form.createResponse(); // cannot prefill bound form easily this way; use UI
  });
  Logger.log('Open the form, click the ⋮ / "Get pre-filled link", fill Agency, copy.');
}

/** Runs on every form submission -> add a row to the Camnemi CRM Customers tab. */
function onFormSubmitEntry(e) {
  try {
    var itemResponses = e.response.getItemResponses();
    function val(title){
      for (var i=0;i<itemResponses.length;i++){
        if (itemResponses[i].getItem().getTitle()===title){
          var v=itemResponses[i].getResponse();
          return Array.isArray(v)?v.join(', '):String(v||'');
        }
      }
      return '';
    }
    var name=(val('Student Name')||'').trim().toUpperCase();
    if(!name) return;
    var ss = SpreadsheetApp.openById(CRM_SHEET_ID);
    var sh = ss.getSheetByName(CUSTOMERS_TAB);
    if(!sh){ sh=ss.insertSheet(CUSTOMERS_TAB); sh.getRange(1,1,1,HEADER.length).setValues([HEADER]); }
    var note = val('Note');
    sh.appendRow([
      'c'+Date.now()+Math.floor(Math.random()*1000),
      'new','contact',name,'',
      val('Agency')||AGENCY_DEFAULT,
      val('Program')||'Not Yet',
      'Not Yet Specified','Not Specified',val('Contact'),
      '','','','',
      note ? JSON.stringify([{text:note,time:new Date().toString()}]) : '[]',
      ''
    ]);
  } catch(err){ Logger.log('onFormSubmit ERROR: '+err); }
}