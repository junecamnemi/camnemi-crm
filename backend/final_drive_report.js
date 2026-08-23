const fs = require("fs");
const rows = JSON.parse(fs.readFileSync("backend/_drive_links.json", "utf8"));
const created = JSON.parse(fs.readFileSync("backend/_created_folders.json", "utf8"));

// Merge: any student with no folder now has a created one
const createdMap = {};
created.forEach(r => { if (r.ok) createdMap[r.name.toLowerCase().trim()] = r; });

const withFolder = [];
const noFolder = [];
rows.forEach(r => {
  const key = (r.name || "").toLowerCase().trim();
  if (r.found && r.folderUrl) {
    withFolder.push(r);
  } else if (createdMap[key]) {
    withFolder.push({ ...r, found: true, folderUrl: createdMap[key].folderUrl, folderId: createdMap[key].folderId, fileCount: 0, createdNow: true });
  } else {
    noFolder.push(r);
  }
});

let csv = "Student,Pipeline,Stage,Files,FolderLink\n";
withFolder.forEach(r => { csv += `${r.name},${r.pipe},${r.stage},${r.fileCount},${r.folderUrl}\n`; });
fs.writeFileSync("backend/drive_links_report.csv", csv);

let md = `# Google Drive Links — Students (${withFolder.length} with folders, ${noFolder.length} without)\n\n`;
md += `## Students WITH Drive folder (${withFolder.length})\n\n| Student | Pipeline | Stage | Files | Link |\n|---|---|---|---|---|\n`;
withFolder.forEach(r => { md += `| ${r.name} | ${r.pipe} | ${r.stage} | ${r.fileCount} | [open](${r.folderUrl}) |\n`; });
if (noFolder.length) {
  md += `\n## Students WITHOUT folder (${noFolder.length})\n\n`;
  noFolder.forEach(r => { md += `- ${r.name} (${r.pipe} / ${r.stage})\n`; });
}
fs.writeFileSync("backend/drive_links_report.md", md);

console.log("With folder:", withFolder.length, "| Without:", noFolder.length);
if (noFolder.length) noFolder.forEach(r => console.log("  NO FOLDER:", r.name));
