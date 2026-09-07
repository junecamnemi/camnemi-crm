const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json" };

async function tryWrite(name, fn) {
  try { await fn(); console.log("OK   ", name); }
  catch (e) { console.log("FAIL ", name, "->", e.message); }
}

(async () => {
  // 1) transactions upsert
  await tryWrite("transactions upsert", () =>
    fetch(SB + "/rest/v1/transactions", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ date: "2026-08-31", type: "income", category: "test", amount: 1, note: "__probe__" }]) }));
  // 2) recs delete+upsert
  await tryWrite("recs delete", () =>
    fetch(SB + "/rest/v1/recs?title=neq.", { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } }));
  await tryWrite("recs upsert", () =>
    fetch(SB + "/rest/v1/recs", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ col: "problems", title: "__probe__", note: "" }]) }));
  // 3) wikiNotes upsert
  await tryWrite("wiki_notes upsert", () =>
    fetch(SB + "/rest/v1/wiki_notes?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ id: "__probe__", cat: "x", subj: "x", body: "", replies: [], updated: "" }]) }));
  // 4) wikiDocs upsert
  await tryWrite("wiki_docs upsert", () =>
    fetch(SB + "/rest/v1/wiki_docs?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ id: "__probe__", note_id: "", cat: "", name: "", url: "" }]) }));
  // 5) wiki_cats upsert
  await tryWrite("wiki_cats upsert", () =>
    fetch(SB + "/rest/v1/wiki_cats?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ id: "__probe__", icon: "", title: "", sort: 0 }]) }));
  // 6) app_settings upsert
  await tryWrite("app_settings upsert", () =>
    fetch(SB + "/rest/v1/app_settings?on_conflict=key", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ key: "__probe__", value: {} }]) }));
  // 7) customers upsert (probe)
  await tryWrite("customers upsert", () =>
    fetch(SB + "/rest/v1/customers?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ id: "__probe__", pipe: "new", stage: "registration", name: "__probe__" }]) }));
})().catch(e => console.error("FATAL", e.message));
