const URL = "https://script.google.com/macros/s/AKfycbwJ7QxDviSojjDJrRHJokneMebb46aS19ooqYiIuyYQsXdxzcZmyzPDleJXr-7JCnonAQ/exec";

const names = [
  "CHIV DANE", "DUCH NARETH", "E SOKUN", "KIT DARAROTH", "KOEM RA",
  "MENG KIMSENG", "NHEN SIVEY", "NOEUN SULEANG", "PE PISETH", "PHEN NARITH",
  "PHON SREYLY", "PHORN PRAKSOMPHORS", "PRORUM SOKMOEUN", "SANH SOKSAN", "SAO CHEAN",
  "SAY SOK OUN", "SORM CHANCHUM POU", "SOUN PICHIRITA", "THUON VANNCHHOEURNG"
];

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function createOne(name) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const r = await fetch(URL, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({ action: "createFolder", name: name })
      });
      const j = await r.json();
      return { name, ...j };
    } catch (e) {
      if (attempt === 2) return { name, error: e.message };
      await sleep(1500);
    }
  }
}

(async () => {
  const results = [];
  for (const n of names) {
    const r = await createOne(n);
    results.push(r);
    console.log(r.ok ? `✅ ${r.name} -> ${r.folderUrl}` : `❌ ${r.name} -> ${r.error || JSON.stringify(r)}`);
    await sleep(1200);
  }
  require("fs").writeFileSync("backend/_created_folders.json", JSON.stringify(results, null, 1));
  const ok = results.filter(r => r.ok);
  console.log(`\nDONE: ${ok.length}/${names.length} created`);
})().catch(e => { console.error("FATAL", e); process.exit(1); });
