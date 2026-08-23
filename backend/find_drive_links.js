const fs = require("fs");
const students = JSON.parse(fs.readFileSync("backend/_students_for_drive.json", "utf8"));
const URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec";

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function one(s) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const r = await fetch(URL, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({ action: "listStudentFolderFiles", name: s.name })
      });
      const j = await r.json();
      if (j && j.ok) return { ...s, found: j.found, folderUrl: j.folderUrl || "", folderId: j.folderId || "", fileCount: (j.files||[]).length };
      return { ...s, found: false, folderUrl: "", folderId: "", fileCount: 0, err: "not ok" };
    } catch (e) {
      if (attempt === 2) return { ...s, found: false, folderUrl: "", folderId: "", fileCount: 0, err: e.message };
      await sleep(1500);
    }
  }
}

(async () => {
  const results = [];
  const uniq = {};
  for (const s of students) {
    const key = (s.name||"").toLowerCase().trim();
    if (!key || uniq[key]) continue; // skip dupes by name
    uniq[key] = 1;
    results.push(await one(s));
    if (results.length % 25 === 0) { console.log("...", results.length); await sleep(2000); }
  }
  fs.writeFileSync("backend/_drive_links.json", JSON.stringify(results, null, 1));
  const withFolder = results.filter(r => r.found && r.folderUrl);
  const noFolder = results.filter(r => !r.found);
  console.log("UNIQUE students queried:", results.length);
  console.log("WITH drive folder:", withFolder.length);
  console.log("NO folder:", noFolder.length);
})().catch(e => { console.error("FATAL", e); process.exit(1); });
