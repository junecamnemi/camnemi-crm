const fs = require("fs");
const line = fs.readFileSync("backend/find_drive_links.js", "utf8");
const URL = line.match(/https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec/)[0];
const names = ["TRY LONGNY", "NOEUN SULEANG"];
(async () => {
  for (const name of names) {
    try {
      const r = await fetch(URL, { method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({ action: "listStudentFolderFiles", name }) });
      const j = await r.json();
      console.log(`[${name}] ok=${j.ok} found=${j.found} files=${(j.files||[]).length} folderId=${(j.folderId||"").substring(0,12)}`);
    } catch (e) { console.log(`[${name}] FETCH_ERR ${e.message.slice(0,80)}`); }
    await new Promise(r => setTimeout(r, 1000));
  }
})();
