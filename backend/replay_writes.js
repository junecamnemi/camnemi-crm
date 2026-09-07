const fs = require("fs");
const key = fs.readFileSync("index.html", "utf8").match(/DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'/)[1];
const SB = "https://zjdvzpylxazfbazioxto.supabase.co";
const H = { apikey: key, Authorization: "Bearer " + key, "Content-Type": "application/json" };

// Replicate supabaseWriteTables order EXACTLY with the real payload shapes.
// We'll use EMPTY arrays (like the real app often has) and see which step throws.
async function step(name, fn) {
  try { const r = await fn(); console.log("OK   ", name, "->", r.status); }
  catch (e) { console.log("FAIL ", name, "->", e.message.slice(0,200)); }
}

(async () => {
  // payload with EMPTY arrays (common when lists are empty) + 1 customer
  const payload = {
    customers: [{ id: "imp_anratana_5", pipe: "korea", stage: "stay", name: "AN RATANA" }],
    tasks: [], transactions: [], recs: [], wikiNotes: [], wikiDocs: [],
    listCustomCols: [], hiddenListCols: [], listColOrder: []
  };
  const WIKI_CATS = [];

  await step("tasks (empty skip)", () => fetch(SB + "/rest/v1/tasks", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([]) }));
  await step("transactions DELETE all", () => fetch(SB + "/rest/v1/transactions?date=neq.", { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } }));
  await step("transactions upsert empty", () => fetch(SB + "/rest/v1/transactions", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([]) }));
  await step("recs DELETE all", () => fetch(SB + "/rest/v1/recs?title=neq.", { method: "DELETE", headers: { ...H, Prefer: "return=minimal" } }));
  await step("recs upsert empty", () => fetch(SB + "/rest/v1/recs", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([]) }));
  await step("wiki_notes upsert empty", () => fetch(SB + "/rest/v1/wiki_notes?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([]) }));
  await step("wiki_docs upsert empty", () => fetch(SB + "/rest/v1/wiki_docs?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([]) }));
  await step("wiki_cats (WIKI_CATS empty skip)", () => Promise.resolve({ status: "skip" }));
  await step("app_settings upsert", () => fetch(SB + "/rest/v1/app_settings?on_conflict=key", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ key: "list_view", value: { listCustomCols: [], hiddenListCols: [], listColOrder: [] } }]) }));
  await step("customers upsert", () => fetch(SB + "/rest/v1/customers?on_conflict=id", { method: "POST", headers: { ...H, Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ id: "imp_anratana_5", pipe: "korea", stage: "stay", name: "AN RATANA" }]) }));
})().catch(e => console.error("FATAL", e.message));
