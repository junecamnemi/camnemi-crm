/** ============================================================
 *  VERIFY — run this FIRST to confirm you are in the RIGHT project
 *  ============================================================
 *  It prints which CRM sheet this project will write to.
 *  It MUST print sheetId = 1olxzowcUja0qfGNDL-El2I6JVkhR_ZvSLHwjLlWGPm8
 *  (that is the "Camnemi CRM" sheet your app reads).
 *  If it prints a DIFFERENT sheetId, you are in the WRONG project.
 * ============================================================
 */
function VERIFY_TARGET() {
  var ss = getSheet();
  Logger.log('CRM SHEET ID: ' + ss.getId());
  Logger.log('CRM SHEET NAME: ' + ss.getName());
  var sh = ss.getSheetByName('Customers');
  if (sh) {
    Logger.log('Customers tab last row: ' + sh.getLastRow());
  } else {
    Logger.log('Customers tab NOT FOUND');
  }
  var dataFile = getDataFile();
  Logger.log('DATA FILE: ' + (dataFile ? dataFile.getName() + ' (' + dataFile.getId() + ')' : 'none'));
}
