# Camnemi CRM → Supabase (full backend)

GitHub Pages stays the **website**. Supabase is the **database**.
The old Google Sheet stays as a fallback until you confirm.

Do **not** put the database password in the CRM. Only Project URL + anon key.

## Already done
- `crm_data` has **171** students (`jsonb_array_length = 171`).

## Run these SQL files in order (SQL Editor)

1. `backend/supabase.sql` — customers blob (if not already run)
2. `backend/import_customers_171.sql` — 171 students into the blob (if not already run)
3. **`backend/supabase_full.sql`** — agencies, wiki, universities, calendar, finance
4. **`backend/seed_ops.sql`** — 7 agencies, 4 fees, 3 wiki notes
5. **`backend/import_universities.sql`** — 316 universities + 413 guide links  
   (file is ~1.2MB; open in an editor, copy all, paste. Or run `python backend/import_universities.py` to regenerate.)
6. **`backend/backfill_customers.sql`** — copy 171 students into the `customers` table

Check:

```sql
select count(*) from customers;        -- 171
select count(*) from agencies;         -- 7
select count(*) from wiki_notes;       -- 3+
select count(*) from universities;     -- 316
select count(*) from university_guides; -- 413
```

## Point the CRM at Supabase (after you say deploy)

1. Open the live CRM.
2. **Data & Google Sheets**.
3. Paste **Project URL** + **anon public** key → **Save Supabase & Sync**.
4. Hard-refresh.

The app then:
- Reads/writes **tables** (customers, agencies, wiki, tasks, …)
- Loads universities from Postgres (falls back to `data.js` if empty)
- Still mirrors the old JSON blob once (safety)

## What stays on GitHub
`index.html`, `data.js` (offline fallback), logos, GKS PDFs.
No student records, no `.env`.
