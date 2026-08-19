/**
 * Camnemi CRM — Google Drive Backend
 * ===================================
 * A Google Apps Script web app that stores the CRM's data in a single
 * JSON file in the owner's Google Drive. The static HTML site calls this
 * API to pull / push data, so all users share one cloud database.
 *
 * DEPLOY:
 *   1. Go to https://script.google.com → New project
 *   2. Paste this whole file into Code.gs
 *   3. Save → Deploy → New deployment → Web app
 *   4. Execute as: Me ; Who has access: Anyone
 *   5. Copy the Web app URL (https://script.google.com/macros/s/...)
 *   6. Paste it into the HTML (BACKEND_URL constant)
 */

var FILE_NAME = 'camnemi_crm_data.json';
var FILE_ID_KEY = 'CAMNEMI_DRIVE_FILE_ID'; // script property holding the data file's ID

function doGet(e) {
  return handle(e, false);
}
function doPost(e) {
  return handle(e, true);
}

function handle(e, isPost) {
  try {
    // CORS headers so the static site can call this
    var output = ContentService.createTextOutput();
    var data = getDataFile().getBlob().getDataAsString('UTF-8');

    if (isPost) {
      var body = JSON.parse(e.postData.contents);
      var newData = body.data;
      if (newData === undefined) throw new Error('Missing "data" field');
      // optional merge of customers by id (union), then overwrite
      saveToFile(JSON.stringify(newData, null, 2));
      data = JSON.stringify(newData);
    }
    output.setContent(data);
    output.setMimeType(ContentService.MimeType.JSON);
    output.append('\n');
    return output;
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      error: String(err)
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/** Get (or create) the JSON data file in Drive. */
function getDataFile() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty(FILE_ID_KEY);
  var file = null;
  if (id) {
    try { file = DriveApp.getFileById(id); } catch (err) { file = null; }
  }
  if (!file) {
    var files = DriveApp.getFilesByName(FILE_NAME);
    while (files.hasNext()) {
      var candidate = files.next();
      if (candidate.getMimeType() === 'application/json') { file = candidate; break; }
    }
  }
  if (!file) {
    file = DriveApp.createFile(FILE_NAME, '{}', 'application/json');
    props.setProperty(FILE_ID_KEY, file.getId());
  }
  return file;
}

function saveToFile(json) {
  var file = getDataFile();
  file.setContent(json);
}

/**
 * Optional: seed the file with the app's default data the first time.
 * Run this function once from the Apps Script editor after deploying,
 * passing the JSON string of your current data.
 */
function seedData(jsonString) {
  saveToFile(jsonString);
  return 'Seeded.';
}
