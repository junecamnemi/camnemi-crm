# Full Supabase Backend Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Move every CRM store (customers, agencies, wiki, universities, calendar, finance, list settings) into Supabase Postgres so GitHub Pages is only the UI.

**Architecture:** Keep the existing GitHub Pages app. Stop using one giant `crm_data.payload` blob as the long-term store. Add real tables + REST reads/writes. Universities stay a catalog (mostly read-only, ~316 rows from `data.js`). Operational data (students, wiki, agencies) becomes editable rows. Drive folders stay in Google Drive; only `folder_id` / `folder_url` live in Postgres.

**Tech Stack:** Supabase Postgres + PostgREST (already wired for `crm_data`), static `index.html`, one-time SQL imports. No auto-deploy until the user says deploy.

---

## Current context / assumptions

- Customers already imported: **171** in `crm_data.payload` (verified `jsonb_array_length = 171`).
- App already serializes most ops data in `exportAllData()` (`index.html` ~5513–5555).
- Wiki is **split**: `camnemi_wiki` localStorage (`WIKI_NOTES`, `WIKI_DOCS`, `WIKI_CATS`) plus optional `wikiNotes`/`wikiDocs` in the blob. Categories often never leave the browser.
- Universities live in `data.js` (`window.UNIV_KNOWLEDGE` + `window.UNIV_GUIDES`, ~1.1MB). Not in the Sheet.
- GKS / Marketing / Korea Life are mostly static HTML/PDFs on GitHub Pages, not CRM records.
- Service Fee / Partner / Recommendation nav is disabled in UI but data arrays still exist.
- Apps Script / Sheet remains fallback until Supabase is confirmed.
- Do **not** put DB password or service role in the website. Anon key only.

### What lives where today

| Domain | In-memory | Cloud today | Size / shape |
|---|---|---|---|
| Customers | DOM cards | Sheet / `crm_data.payload.customers` | 171 rows; flags, payments JSON, Drive folder |
| Agencies | `AGENCIES` | payload / Sheet tab | `{name, commission, policy, note}` |
| Service fees | `FEES` | payload | `{name, amount, policy}` |
| Partners | `PARTNERS` | payload | `{name, note}` |
| Tasks / calendar | `TASKS` | payload | `{date, type, title, note}` |
| Profit / expense | `TRANS` | payload | `{date, type, cat, amount, note}` |
| Recommendations | `RECS` | payload | `{col, title, note}` |
| Wiki notes | `WIKI_NOTES` | localStorage (+ payload if present) | `{id, cat, subj, body, replies[], updated}` |
| Wiki docs | `WIKI_DOCS` | localStorage | file metadata |
| Wiki cats | `WIKI_CATS` | localStorage only | `{id, icon, title}` |
| List view prefs | `LIST_*` | payload | custom cols / hidden / order |
| Activity log | `ACTIVITY_LOG` | payload | `{time, user, student, action}` |
| Universities | `UNIV_KNOWLEDGE` | `data.js` only | ~316 univ+junior; majors, tuition, reqs, logo path |
| Guides | `UNIV_GUIDES` | `data.js` + Drive PDFs | `{ba, ma, lang}` URLs |
| GKS / Marketing / Korea Life | static views | GitHub files | not a table yet |

---

## Proposed approach

**Phase A — normalize ops data (do this first).**  
Replace the blob for everything the team edits daily.

**Phase B — university catalog.**  
Import `data.js` into `universities` + `university_guides`. App loads from REST instead of the 1.1MB JS file (keep `data.js` as offline fallback).

**Phase C — tighten security.**  
Google login `@camnemi.com` via Supabase Auth; RLS `authenticated` only. Not required to start.

Keep `crm_data` as a compatibility mirror until every client is on tables.

---

## Target schema (Postgres)

### Operational

```sql
agencies (name text pk, commission text, policy text, note text, updated_at timestamptz)
fees (id uuid pk, name text, amount text, policy text, sort int, updated_at)
partners (id uuid pk, name text, note text, updated_at)
tasks (id uuid pk, date text, type text, title text, note text, updated_at)
transactions (id uuid pk, date text, type text, category text, amount numeric, note text, updated_at)
recs (id uuid pk, col text, title text, note text, updated_at)
wiki_cats (id text pk, icon text, title text, sort int)
wiki_notes (id text pk, cat text, subj text, body text, replies jsonb, updated text)
wiki_docs (id text pk, cat text, name text, url text, meta jsonb, updated_at)
activity_log (id bigserial, time text, user_name text, student text, action text)
app_settings (key text pk, value jsonb)  -- listCustomCols, hiddenListCols, listColOrder
```

`customers` already exists (from `supabase.sql`). Add missing columns if needed: `hidden`, `siemreap`, `custom_fields` (already in schema).

### Knowledge catalog

```sql
universities (
  id text pk,          -- Korean official name `n`
  name_kr text,
  name_en text,
  short_en text,       -- es (KWU, JBNU…)
  loc text,
  type text,           -- univ | junior
  logo text,
  students int,
  rank int,
  tuition jsonb,       -- {ba, ma, lang}
  req jsonb,           -- {topik, ielts, kiip, sejong, selftest, english}
  cert jsonb,
  majors_ba jsonb,
  majors_ma jsonb,
  extra jsonb
);
university_guides (
  univ_id text references universities(id),
  track text,          -- ba | ma | lang
  url text,
  primary key (univ_id, track)
);
```

Logos/PDFs stay on GitHub Pages / Drive. DB stores paths and URLs only.

---

### Task 1: Write `backend/supabase_full.sql`

**Objective:** Add all ops + catalog tables and anon RLS next to existing `crm_data` / `customers`.

**Files:**
- Create: `C:\Users\USER\camnemi-crm\backend\supabase_full.sql`

**Step 1:** Add `create table if not exists` for every table in Target schema. Include indexes on `customers(pipe,stage)`, `universities(short_en)`, `wiki_notes(cat)`.

**Step 2:** Enable RLS; `anon` select+write on ops tables (same “Anyone” model as Apps Script). Catalog tables: `anon` select; write optional for later editor.

**Step 3:** Do not drop `crm_data`. Leave it until cutover.

**Step 4:** User runs the SQL in Supabase SQL Editor. Verify with `\dt` / Table Editor.

---

### Task 2: Seed agencies / fees / wiki defaults

**Objective:** Insert current in-app defaults so a fresh DB is not empty.

**Files:**
- Create: `C:\Users\USER\camnemi-crm\backend\seed_ops.sql`

Seed:
- 7 agencies (CAMNEMI, COSTA, Khema, Kimsous, Sen Chao, JK, Din Lina)
- 4 default fees
- 3 default wiki cats + 3 seed wiki notes from `seedWiki()`

Verify: `select count(*) from agencies;` → 7.

---

### Task 3: Import universities from `data.js`

**Objective:** Load ~316 universities + guides into Postgres.

**Files:**
- Create: `C:\Users\USER\camnemi-crm\backend\import_universities.py` (or generate `import_universities.sql`)
- Read: `C:\Users\USER\camnemi-crm\data.js`

**Step 1:** Parse `window.UNIV_KNOWLEDGE` and `window.UNIV_GUIDES` with Python.

**Step 2:** Upsert into `universities` / `university_guides`.

**Step 3:** Verify `select count(*) from universities;` matches `data.js` length (expect ~316).

Do **not** commit a huge generated SQL to git if it is >1MB; keep a generator script + optional local SQL.

---

### Task 4: App REST helpers

**Objective:** One small client for table CRUD.

**Files:**
- Modify: `C:\Users\USER\camnemi-crm\index.html` (near existing `supabaseFetch`)

Add:
```javascript
async function sbSelect(table, query) { /* GET /rest/v1/table?query */ }
async function sbUpsert(table, rows, onConflict) { /* POST Prefer: resolution=merge-duplicates */ }
async function sbDelete(table, query) { /* DELETE */ }
```

Keep `useSupabase()` gate. If keys missing, keep current Apps Script / localStorage path.

---

### Task 5: Load/save agencies, fees, partners, tasks, trans, recs from tables

**Objective:** Stop relying on the blob for policy + calendar + finance.

**Files:**
- Modify: `index.html` `syncPull` / `syncPush` / `applyDbToState` / `saveDatabase`

**Step 1:** `syncPull` when Supabase: `Promise.all` select those tables; assign `AGENCIES = mergeAgencies(...)`, etc.

**Step 2:** On save (`saveNow` / agency edit / fee edit): upsert the changed table only — do **not** rewrite all 171 customers.

**Step 3:** Manual test: add agency on PC A, refresh PC B, agency appears.

---

### Task 6: Wiki to Supabase

**Objective:** Wiki is shared across PCs, not `camnemi_wiki` only.

**Files:**
- Modify: `loadWiki`, `syncWiki`, `saveWikiNote`, `saveWikiReply` in `index.html`

**Step 1:** Load cats/notes/docs from tables.

**Step 2:** Each note save → upsert `wiki_notes` (including `replies` jsonb).

**Step 3:** Keep localStorage as cache only.

**Step 4:** Verify new wiki note appears after hard-refresh on another browser.

---

### Task 7: Customers stay row-based (already started)

**Objective:** Writes update `customers` by id instead of replacing the whole payload.

**Files:**
- Modify: `syncPush` / card save / hide / stage move

**Step 1:** On card change, `PATCH /rest/v1/customers?id=eq.{id}`.

**Step 2:** On new card, `POST` one row.

**Step 3:** Hide = `hidden='true'` update, never delete Drive folder.

**Step 4:** Keep payload sync as optional mirror for one release.

---

### Task 8: Universities from REST

**Objective:** Knowledge panel works without waiting on `data.js` when online.

**Files:**
- Modify: `loadDataFile` / `openUniversities` / `koreaSchoolShort`

**Step 1:** If Supabase: `select * from universities` (+ guides). Map to current `UNIV_KNOWLEDGE` field names (`n`, `en`, `es`, `ek`, `req`, `tuition`…).

**Step 2:** If offline or empty: fall back to `data.js`.

**Step 3:** Verify school short names on cards still resolve (KWU, JBNU, SJU, KMU, DDWU).

---

### Task 9: List prefs + activity log

**Objective:** Column hide/order and activity log follow the user across PCs.

**Files:**
- Modify: list-settings save + `ACTIVITY_LOG` append

Store in `app_settings` (`list_view`) and `activity_log`.

---

### Task 10: Cut over + verify (no auto-deploy)

**Objective:** Prove every section is cloud-backed before turning off Sheet.

**Verification:**
1. Customers: 171, PICHRITA only, no PICHIRITA.
2. Agencies: 7 defaults + any new ones persist after refresh.
3. Wiki: create note → other PC sees it.
4. Universities: count ≈ 316; 경운대 short name KWU.
5. Tasks + one transaction persist.
6. Empty browser does **not** wipe cloud (no full-payload replace of empty local).
7. Drive folder links still open.

**Deploy:** only when user says `deploy`. Do not commit `.env`.

---

## Files likely to change

- `backend/supabase_full.sql` (new)
- `backend/seed_ops.sql` (new)
- `backend/import_universities.py` (new)
- `index.html` (sync + wiki + univ load)
- `backend/SUPABASE_SETUP.md` (update steps)
- `data.js` (keep as fallback; later optional)

## Risks / tradeoffs

- **One blob is simpler but slow and unsafe** (empty browser can overwrite). Tables fix that.
- **Anon RLS is open** until Auth is added — same as current Apps Script “Anyone”.
- **Universities are large** — load once, cache in memory; don’t refetch every card render.
- **Wiki replies as jsonb** matches current UI; normalize later if needed.
- **GKS/Marketing/Korea Life** can stay files until they become editable CMS pages.

## Open questions

1. Should universities be **editable in the CRM** (tuition/reqs) or remain a catalog you refresh from `data.js`?
2. When to add **@camnemi.com Supabase Auth** (now vs after tables work)?
3. Keep Google Sheet as a **read-only export** (nightly dump) or drop it after cutover?

---

Plan complete. Ready to execute task-by-task. Shall I proceed with Task 1 (`supabase_full.sql`)?
