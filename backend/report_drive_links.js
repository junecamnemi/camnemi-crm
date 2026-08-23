const fs = require("fs");
const rows = JSON.parse(fs.readFileSync("backend/_drive_links.json", "utf8"));

const withFolder = rows.filter(r => r.found && r.folderUrl);
const noFolder = rows.filter(r => !r.found);

console.log("=== DRIVE LINK REPORT ===");
console.log("Unique students queried:", rows.length);
console.log("With Drive folder:", withFolder.length);
console.log("Without folder:", noFolder.length);
console.log("");
console.log("=== STUDENTS WITH DRIVE FOLDER ===");
withFolder.forEach(r => {
  console.log(`${r.name} | ${r.pipe} | ${r.stage} | ${r.fileCount} files | ${r.folderUrl}`);
});
console.log("");
console.log("=== STUDENTS WITHOUT FOLDER ===");
noFolder.forEach(r => {
  console.log(`${r.name} | ${r.pipe} | ${r.stage}`);
});
