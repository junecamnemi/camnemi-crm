/**
 * Camnemi CRM — Google Drive Backend
 * ===================================
 * A Google Apps Script web app that stores the CRM's data in a single
 * JSON file in the owner's Google Drive, AND hosts university admission
 * guide PDFs uploaded to a specified Drive folder.
 *
 * DEPLOY:
 *   1. https://script.google.com → New project
 *   2. Paste this whole file into Code.gs
 *   3. Save → Deploy → New deployment → Web app
 *   4. Execute as: Me ; Who has access: Anyone
 *   5. Copy the Web app URL → paste into the app's Backend settings.
 */

var FILE_NAME = 'camnemi_crm_data.json';
var FILE_ID_KEY = 'CAMNEMI_DRIVE_FILE_ID';

function doGet(e) {
  return handle(e, false);
}
function doPost(e) {
  return handle(e, true);
}

function handle(e, isPost) {
  try {
    var output = ContentService.createTextOutput();
    var body = {};
    if (isPost) {
      var raw = e.postData.contents;
      body = JSON.parse(raw);
    }

    // --- ACTION: upload a PDF to a Drive folder ---
    if (body.action === 'upload') {
      return uploadGuide(body);
    }

    // --- DATA get/set ---
    var data = getDataFile().getBlob().getDataAsString('UTF-8');
    if (isPost && body.data !== undefined) {
      saveToFile(JSON.stringify(body.data, null, 2));
      data = JSON.stringify(body.data);
    }
    output.setContent(data);
    output.setMimeType(ContentService.MimeType.JSON);
    return output;
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Upload a single guide PDF to the target Drive folder.
 * POST body: { action:'upload', folderId:'...', filename:'...', contentBase64:'...' }
 * Returns: { ok:true, fileId, name, link, viewLink }
 */
function uploadGuide(body) {
  var folderId = body.folderId;
  var filename = body.filename;
  var b64 = body.contentBase64;
  if (!folderId || !filename || !b64) {
    return jsonOut({ error: 'Missing folderId/filename/contentBase64' });
  }
  var folder = DriveApp.getFolderById(folderId);
  var bytes = Utilities.base64Decode(b64, Utilities.Charset.UTF_8);
  // Create with the correct MIME so Drive renders it as a PDF
  var blob = Utilities.newBlob(bytes, 'application/pdf', filename);
  var file = folder.createFile(blob);
  // Make anyone-with-link readable (so the public site can open it)
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  file.setDescription('Camnemi admission guide');
  return jsonOut({
    ok: true,
    fileId: file.getId(),
    name: file.getName(),
    link: 'https://drive.google.com/uc?export=download&id=' + file.getId(),
    viewLink: 'https://drive.google.com/file/d/' + file.getId() + '/view',
    size: bytes.length
  });
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
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
  getDataFile().setContent(json);
}

function seedData(jsonString) {
  saveToFile(jsonString);
  return 'Seeded.';
}
