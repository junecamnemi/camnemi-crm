# Design C — Serving layer + migration for the Camnemi guide database

> Scope: how web apps, analytics, and reports read the **daily-refreshed** university
> data. This is the read side of the redesign. It assumes **Design A** (normalised DDL:
> schools → programs → colleges → departments → scholarships → periods → sources →
> provenance) and **Design B** (temporal/versioning + daily ETL pipeline) already exist.
> Where C depends on those, the dependency is named explicitly so the three can be read
> together.
>
> The one-sentence thesis: **Postgres is the single source of truth; every web app reads
> a small number of pre-shaped read models (views) through an anon key that is
> SELECT-only; private CRM data moves behind authentication; and `data.js`/JSON are
> build artifacts exported *from* Postgres, never written back.**

---

## 0. Consumer inventory (measured, not aspirational)

| Consumer | Runtime | Read path today | What it needs |
|---|---|---|---|
| **camnemi-crm** (`index.html`, GitHub Pages) | browser | Supabase anon (`supabaseLoadUniversities()`) → falls back to `data.js` (`window.UNIV_KNOWLEDGE`) | school cards, tuition min/max, req (TOPIK/IELTS/KIIP/자체시험), majors BA/MA, scholarships, per-college tuition; **plus private CRM tables** (171 customers, transactions, tasks, activity_log, wiki, app_settings) |
| **camnemi-apply** (Cloudflare Worker + static) | browser | PostgREST anon, `universities?select=id,name_kr,name_en,short_en,loc,type,logo,students,rank,tuition,req,majors_ba,majors_ma,scholarships,programs,website,documents,country_notes` and `university_guides?select=univ_id,track,year,url,en,en_url,period` | the full school card + guide links, filtered/sorted in JS |
| **camnemi-register-amc** (Worker) | server | anon key → `rpc()` (security-definer) + Storage | **write-only**: AMC-YYYY-NNNN customer insert, file upload, email. Does not read guides |
| **camnemi-topik / camnemi-medical / "game"** | static/Worker | own vocab/marketing data | do **not** read guide data (confirm below) |
| **Analytics / reports** (internal, 1–2 staff) | scripts / SQL editor / occasional PDF | service role / SQL editor | coverage, change-log, deadlines, provenance |
| **CRM advising** | browser | same as CRM | "English-track majors with IELTS≤X", tuition by college, scholarships by TOPIK/IELTS, deadlines next 30 days |

**Key finding that shapes the design:** the live `camnemi-apply` app already queries columns
that are **not** in `backend/supabase_full.sql` — `universities.scholarships, programs, website,
documents, country_notes` and `university_guides.year, en, en_url, period`. The production
schema has drifted ahead of the committed SQL. The migration must (a) treat the **live schema**
as the compatibility contract, not the committed file, and (b) emit the **superset** of both.

---

## 1. Read models

All read models live in the **`public` schema** (the only schema Supabase exposes over
PostgREST). The source tables live in a **`cat`** schema that PostgREST does **not** expose.
Read models are `security definer` views owned by the schema owner, with `GRANT SELECT …
TO anon` — this is the standard Supabase "expose a view, hide the table" boundary (see §2).

Rule of thumb: at ~330 current-cycle documents the catalog is a few thousand rows — **plain
views are fast enough for interactive query**. One materialised view (`mv_school_card`) is
kept because it is the **export snapshot** the `data.js` build reads from, and because it
gives reports a stable "as of yesterday" freeze. Everything else stays a live view.

### 1.1 Source skeleton (from Design A) that the views hang off

```sql
create schema if not exists cat;               -- source of truth, NOT exposed via PostgREST

create table cat.school (
  id            text primary key,              -- stable slug, e.g. 'jeonbuk'
  name_kr       text not null,
  name_en       text,  short_en text,
  aliases       text[] not null default '{}',
  loc           text,  region  text,
  type          text not null default 'univ',  -- univ | junior | lang-centre
  logo          text,  students int,  rank text,
  ieqas_certified bool, ieqas_level text, ieqas_course text, ieqas_year text,
  website       text,  documents  jsonb,  country_notes jsonb,
  student_count int,
  updated_at    timestamptz not null default now()
);

create table cat.program (
  id             uuid primary key default gen_random_uuid(),
  school_id      text not null references cat.school(id) on delete cascade,
  level          text not null check (level in ('ba','ma','junior','lang')),
  guide_year     int  not null,                -- 학년도 label (file name)
  effective_year int,                          -- corrected 학년도 (invariant #5)
  is_current     bool not null default true,
  apply_system   text,
  period_raw     text,
  fee_app        numeric, fee_admission numeric,
  tuition_min    numeric, tuition_max numeric,
  tuition_semester_by_dept jsonb,              -- genuinely open-ended: field→KRW map (invariant #2)
  req            jsonb,                        -- {topik,ielts,toefl,kiip,sejong,selftest,english}
  track_policy   text,                         -- per_department | unified
  -- provenance (invariant #6)
  source_pdf text, source_kind text,           -- pdf | page-render | hwp-converted (invariant #10)
  page_ref text, parse_run_id uuid, model text, tier text,
  evidence_score numeric,
  parsed_at timestamptz,
  unique (school_id, level, guide_year)
);

create table cat.college (
  id          uuid primary key default gen_random_uuid(),
  program_id  uuid not null references cat.program(id) on delete cascade,
  name        text not null,
  tuition_krw numeric,                          -- single semester figure
  tuition_first_sem numeric, tuition_later_sem numeric,   -- invariant #2 "first vs later"
  sort int not null default 0
);

create table cat.department (
  id           uuid primary key default gen_random_uuid(),
  college_id   uuid not null references cat.college(id) on delete cascade,
  major        text not null,
  major_en     text,
  korean_track bool, english_track bool,        -- invariant #3: two tracks per department
  topik int, ielts numeric, toefl int,
  source_pdf text, page_ref text, evidence text
);

create table cat.scholarship (
  id           uuid primary key default gen_random_uuid(),
  program_id   uuid not null references cat.program(id) on delete cascade,
  name         text,
  type         text not null check (type in ('enroll','existing')),   -- invariant #4 axis 1
  category     text check (category in ('academic','language','both','general')), -- axis 2
  benefit_kind text,      -- pct | amount | waiver | dorm
  benefit_value text,
  condition_raw text,
  source_pdf text, page_ref text
);

create table cat.scholarship_tier (
  id             uuid primary key default gen_random_uuid(),
  scholarship_id uuid not null references cat.scholarship(id) on delete cascade,
  score_type     text not null,                 -- TOPIK | IELTS | TOEFL | GPA
  score          text,                          -- keep text ('4급','5.5','3.0'); derivable numeric col below
  score_num      numeric,                       -- machine-comparable where possible
  amount         text                           -- '수업료 100%' | '70%' | '₩1,000,000'
);

create table cat.period (
  id          uuid primary key default gen_random_uuid(),
  program_id  uuid not null references cat.program(id) on delete cascade,
  round       int not null default 1,
  from_date   date, to_date date,
  note        text
);

create table cat.guide_source (                 -- replaces university_guides
  school_id  text not null references cat.school(id) on delete cascade,
  level      text not null check (level in ('ba','ma','junior','lang')),
  guide_year int  not null,
  url        text,  en text,  en_url text,  period text,
  kind       text,                              -- pdf | page-render | hwp-converted
  md5        text,
  primary key (school_id, level, guide_year)
);
```

### 1.2 The read models

#### `public.v_school` — the school card (feeds CRM cards, apply list, and the `data.js` export)

One row per school, **current-cycle only** (`is_current`), with the two `jsonb` shapes the
consumers already parse re-serialised so no consumer code changes at cut-over.

```sql
create or replace view public.v_school with (security_invoker = false) as
select
  s.id, s.name_kr, s.name_en, s.short_en, s.loc, s.region, s.type, s.logo,
  s.students, s.rank, s.ieqas_certified, s.ieqas_level, s.website,
  s.documents, s.country_notes, s.student_count,
  p.guide_year, p.effective_year,
  p.req,
  p.tuition_min, p.tuition_max,
  p.tuition_semester_by_dept,
  -- re-serialised for legacy consumers
  jsonb_build_object(
    'topik', p.req->'topik', 'ielts', p.req->'ielts', 'toefl', p.req->'toefl',
    'kiip', p.req->'kiip', 'sejong', p.req->'sejong', 'selftest', p.req->'selftest',
    'english', p.req->'english'
  ) as req_legacy,
  p.source_pdf, p.source_kind, p.page_ref, p.parse_run_id, p.model, p.tier,
  p.evidence_score, p.parsed_at, p.updated_at
from cat.school s
join cat.program p on p.school_id = s.id
where p.is_current and p.level = 'ba';          -- BA is the primary card; see mv_school_card for level fan-out
```

> Note: `v_school` is BA-scoped for the card. The **multi-level** card (tuition.ba / tuition.ma /
> majors_ba / majors_ma) that `data.js`'s `UNIV_KNOWLEDGE` actually ships is the
> **materialised** `mv_school_card` below, which does the per-school × level fan-out.

#### `public.v_major` — "English-track majors with IELTS ≤ X and their tuition"

The advising query, flattened one row per department so a PostgREST `?english_track=eq.true&ielts=lte.5.5`
(or SQL `WHERE`) is a plain indexed scan, **not** a JSON scrape (invariant #3).

```sql
create or replace view public.v_major as
select
  s.id as school_id, s.name_kr, s.name_en, s.loc, s.region, s.type, s.rank,
  p.level, p.guide_year, p.effective_year, p.is_current,
  c.name as college, c.tuition_krw as college_tuition_krw,
  d.major, d.major_en,
  d.korean_track, d.english_track,
  d.topik, d.ielts, d.toefl,
  p.req->>'topik' as school_topik, p.req->>'ielts' as school_ielts,
  d.source_pdf, d.page_ref, d.evidence
from cat.school s
join cat.program p      on p.school_id = s.id
join cat.college c      on c.program_id = p.id
join cat.department d   on d.college_id = c.id
where p.is_current;
```

Indexes that make this an index-only plan:

```sql
create index dept_english_ielts on cat.department (english_track, ielts)
  where english_track;
create index dept_korean_topik  on cat.department (korean_track, topik)
  where korean_track;
create index dept_college_fk    on cat.department (college_id);
create index college_program_fk on cat.college (program_id);
create index program_school_cur on cat.program (school_id, is_current, level);
```

#### `public.v_college_tuition` — "tuition comparison by college"

```sql
create or replace view public.v_college_tuition as
select
  s.id as school_id, s.name_kr, s.name_en, s.loc, s.region, s.type,
  p.level, p.guide_year, p.is_current,
  c.name as college, c.tuition_krw,
  c.tuition_first_sem, c.tuition_later_sem,
  p.tuition_min as school_min, p.tuition_max as school_max,
  c.source_pdf
from cat.school s
join cat.program p on p.school_id = s.id
join cat.college c on c.program_id = p.id
where p.is_current;

create index college_tuition_idx  on cat.college (name, tuition_krw);
create index college_name_lookup  on cat.college (name);
```

#### `public.v_scholarship_tier` — "scholarship tiers by TOPIK / IELTS"

Flattens the two-axis scholarship model (invariant #4) into one tier per row so
"which schools give ≥70% for TOPIK 5" is a filter, not a parser.

```sql
create or replace view public.v_scholarship_tier as
select
  s.id as school_id, s.name_kr, s.name_en, s.loc, s.type,
  p.level, p.guide_year, p.is_current,
  sch.name as scholarship_name, sch.type, sch.category,
  sch.benefit_kind, sch.benefit_value,
  t.score_type, t.score, t.score_num, t.amount,
  sch.source_pdf, sch.page_ref
from cat.school s
join cat.program p        on p.school_id = s.id
join cat.scholarship sch  on sch.program_id = p.id
join cat.scholarship_tier t on t.scholarship_id = sch.id
where p.is_current;

create index sch_tier_score on cat.scholarship_tier (score_type, score_num);
create index sch_prog_fk   on cat.scholarship (program_id);
```

#### `public.v_deadline` — "application deadlines in the next 30 days"

```sql
create or replace view public.v_deadline as
select
  s.id as school_id, s.name_kr, s.name_en, s.loc, s.type,
  p.level, p.guide_year, p.is_current,
  per.round, per.from_date, per.to_date, per.note,
  (per.to_date - current_date) as days_left,
  p.period_raw, p.source_pdf, p.page_ref
from cat.school s
join cat.program p on p.school_id = s.id
join cat.period per on per.program_id = p.id
where p.is_current and per.to_date is not null;

create index period_todate on cat.period (to_date)
  where to_date is not null;
create index period_prog_fk on cat.period (program_id);
```

PostgREST form of the consumer query:
`/v_deadline?days_left=gte.0&days_left=lte.30&level=eq.ba&order=to_date.asc`.

#### `public.v_provenance` — the "where did this number come from" read (invariant #6)

One row per school × level × field-group, so the UI can render "this tuition = PDF p.7,
parse run #1234, model pro, evidence 0.9" without a second fetch.

```sql
create or replace view public.v_provenance as
select
  s.id as school_id, s.name_kr, p.level, p.guide_year, p.effective_year,
  p.source_pdf, p.source_kind, p.page_ref, p.model, p.tier,
  p.evidence_score, p.parsed_at, p.parse_run_id,
  jsonb_build_object(
    'tuition_min', p.tuition_min, 'tuition_max', p.tuition_max,
    'req', p.req
  ) as values_snapshot
from cat.school s
join cat.program p on p.school_id = s.id
where p.is_current;
```

#### `public.mv_school_card` — the export snapshot (feeds `data.js` build + stable reports)

Materialised, rebuilt once a day, per school × level with the legacy JSON shapes.

```sql
create materialized view public.mv_school_card as
select
  s.id, s.name_kr, s.name_en, s.short_en, s.loc, s.region, s.type, s.logo,
  s.students, s.rank, s.ieqas_certified, s.ieqas_level, s.website,
  s.documents, s.country_notes,
  jsonb_object_agg(p.level, jsonb_build_object(
      'guide_year', p.guide_year, 'effective_year', p.effective_year,
      'req', p.req,
      'tuition_min', p.tuition_min, 'tuition_max', p.tuition_max,
      'tuition_semester_by_dept', p.tuition_semester_by_dept,
      'source_pdf', p.source_pdf, 'source_kind', p.source_kind,
      'model', p.model, 'tier', p.tier, 'evidence_score', p.evidence_score
    ) order by p.level
  ) filter (where p.is_current) as programs,
  -- legacy shapes consumed by data.js / apply today
  coalesce(jsonb_object_agg(p.level, jsonb_build_object('min', p.tuition_min, 'max', p.tuition_max)) filter (where p.is_current), '{}') as tuition,
  coalesce((jsonb_object_agg(p.level, p.req) filter (where p.is_current and p.level in ('ba','ma'))), '{}') as req,
  max(p.parsed_at) as parsed_at,
  count(*) filter (where p.is_current) as levels_present
from cat.school s
left join cat.program p on p.school_id = s.id
group by s.id;

-- unique index is REQUIRED before REFRESH ... CONCURRENTLY
create unique index mv_school_card_pk on public.mv_school_card (id);
```

`data.js`'s `majors_ba` / `majors_ma` arrays and `scholarships[]` are aggregated in the
**export script** (Python), not in SQL, because they need the exact minified field order
the consumers expect (invariant #8). The script reads `mv_school_card` + `v_major` +
`v_scholarship_tier` and emits the flat object.

---

## 2. Supabase access design — RLS that is actually safe

### 2.1 The three-tier model

| Tier | Credential | What it may touch | Policy |
|---|---|---|---|
| **`anon`** (public web) | anon key (ships in every browser) | **SELECT only** on the `public.v_*` / `public.mv_*` read models + `university_guides` compat view | `GRANT SELECT … TO anon`. **No write, no PII, no CRM tables.** |
| **`authenticated`** (staff CRM) | Supabase Auth JWT (1–2 staff log in) | CRUD on CRM tables: `customers`, `agencies`, `fees`, `partners`, `tasks`, `transactions`, `recs`, `wiki_*`, `activity_log`, `app_settings` | `to authenticated using (true)` per table |
| **`service_role`** (pipeline & server-side workers) | service key (never in a browser) | bypasses RLS: `cat.*` source writes, `REFRESH MATERIALIZED VIEW`, `data_change_log` | N/A (bypasses) |

**The `using(true)` for anon on every table is a data leak and must be removed** — it exposes
171 customers, transactions, activity log, and app settings to anyone with the anon key
(which is in every shipped `config.js`). The corrective is the table-by-table revocation in §2.3.

### 2.2 Catalog boundary (public reads, private source)

```sql
-- PostgREST exposes only the `public` schema. `cat` is invisible to it.
-- anon gets SELECT on the read models only:
grant usage  on schema public to anon;
grant select on public.v_school, public.v_major, public.v_college_tuition,
               public.v_scholarship_tier, public.v_deadline, public.v_provenance,
               public.mv_school_card
  to anon;
-- (compat views `universities` / `university_guides` granted during migration, §4)

-- source tables: no anon grant, RLS enabled, no anon policy → anon cannot read them directly.
alter table cat.school           enable row level security;
alter table cat.program          enable row level security;
alter table cat.college          enable row level security;
alter table cat.department       enable row level security;
alter table cat.scholarship      enable row level security;
alter table cat.scholarship_tier enable row level security;
alter table cat.period           enable row level security;
alter table cat.guide_source     enable row level security;
alter table cat.etl_run          enable row level security;
alter table cat.change_log       enable row level security;
-- no `for anon` policies are created on cat.* — that is the entire boundary.
```

The read models are `security definer` views (owner = schema owner, which can read `cat.*`).
PostgREST resolves them as the owner, so anon sees exactly the view's rows and nothing else.

> ⚠️ `security definer` views bypass RLS on the underlying tables. That is **intended**
> here, but it means the view's `WHERE`/`JOIN` is the only gate: keep them read-only,
> never parameterised by client input at definition time, and never grant anon `INSERT`/
> `UPDATE`/`DELETE` on them.

### 2.3 CRM private data — revoke anon, move to `authenticated`

```sql
-- 1) Drop the blanket anon CRUD (the existing using(true) mistake):
drop policy if exists agencies_anon_all      on agencies;
drop policy if exists fees_anon_all          on fees;
drop policy if exists partners_anon_all      on partners;
drop policy if exists tasks_anon_all         on tasks;
drop policy if exists transactions_anon_all  on transactions;
drop policy if exists recs_anon_all          on recs;
drop policy if exists wiki_cats_anon_all     on wiki_cats;
drop policy if exists wiki_notes_anon_all    on wiki_notes;
drop policy if exists wiki_docs_anon_all     on wiki_docs;
drop policy if exists activity_log_anon_all  on activity_log;
drop policy if exists app_settings_anon_all  on app_settings;
-- (universities / university_guides anon policies are replaced by view grants in §4)

-- 2) Staff-only access. Two tables stay partially public on purpose (below).
create policy staff_all on customers   for all to authenticated using (true) with check (true);
create policy staff_all on tasks       for all to authenticated using (true) with check (true);
create policy staff_all on transactions for all to authenticated using (true) with check (true);
create policy staff_all on recs        for all to authenticated using (true) with check (true);
create policy staff_all on activity_log for all to authenticated using (true) with check (true);
create policy staff_all on app_settings for all to authenticated using (true) with check (true);
create policy staff_all on wiki_cats   for all to authenticated using (true) with check (true);
create policy staff_all on wiki_notes  for all to authenticated using (true) with check (true);
create policy staff_all on wiki_docs   for all to authenticated using (true) with check (true);
create policy staff_all on partners    for all to authenticated using (true) with check (true);
```

**Two deliberate exceptions — read-only anon where the public web actually needs it:**

```sql
-- agencies: the public apply form's dropdown needs agency names only. Expose 2 columns via a view,
-- not the table, so commission/policy/note stay private.
create or replace view public.v_agencies as select name from agencies;
grant select on public.v_agencies to anon;

-- fees: the public "our fees" page needs name+amount only.
create or replace view public.v_fees as select name, amount, sort from fees;
grant select on public.v_fees to anon;
```

(`customers`, `transactions`, `activity_log`, `app_settings`, `wiki_notes` **never** get anon
access — they carry student PII and business internals.)

### 2.4 Server-side writes (the register-amc pattern, kept)

`camnemi-register-amc` already does the right thing: the browser/Worker holds the **anon** key
but all sensitive writes go through **`security definer` RPC functions** that enforce
server-side validation (duplicate detection, ID generation, bucket path). Keep this and extend
it: the AMC submit RPC is the *only* write path anon can reach, and it is not table-granted.

```sql
-- illustrative: the one public write path, validated server-side, not a table grant.
create or replace function public.amc_register(p jsonb)
returns jsonb language plpgsql security definer as $$
declare new_id text;
begin
  -- validate, dedupe, generate AMC-YYYY-NNNN, insert into customers, return id
  ...
end $$;
revoke all on function public.amc_register(...) from public;
grant execute on function public.amc_register(...) to anon;
```

---

## 3. Refresh strategy — one rebuild per day, no downtime

### 3.1 The daily cycle (owned by Design B's pipeline, C defines the read-side steps)

```
08:00  ETL (Design B) lands new/updated rows into cat.*, writes cat.etl_run + cat.change_log
       (idempotent upserts on (school_id, level, guide_year); md5-based skip; no in-place edit of history)
09:00  REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_school_card;   -- non-blocking
       export data.js (artifact) from mv_school_card + v_major + v_scholarship_tier
       bump app_settings 'published_version' = run_id  (provenance + staleness marker)
       commit → GitHub Pages repo (data.js) + R2 (catalog.json) + KV (version stamp)
```

The refresh is wrapped in **one transaction** so readers see the old snapshot or the new one,
never a half-rebuilt state. `REFRESH MATERIALIZED VIEW CONCURRENTLY` requires the unique index
(`mv_school_card_pk` above) and does **not** take an `ACCESS EXCLUSIVE` lock, so live reads
never block — the "no downtime" constraint.

```sql
refresh materialized view concurrently public.mv_school_card;
```

### 3.2 Postgres direct read vs generated artifact — when each wins

| Consumer | Direct PostgREST (anon, live view) | Generated artifact (`data.js` / `catalog.json`) |
|---|---|---|
| **apply** — interactive filter/sort on the full card | ✅ primary path (already does this) | JSON on R2 as cold-start fallback |
| **CRM** — school search, scholarship browse, deadlines | ✅ primary path | `data.js` as **offline fallback** (already wired) |
| **Workers** — register-amc (write) | RPC only | n/a |
| **topik / medical / game** | not a guide consumer | own data |
| **offline / export / PDF generation** | n/a | ✅ `data.js` + `catalog.json` |

**Decision:** interactive reads go **direct to PostgREST** (the data is tiny and this keeps
one source of truth, no cache-invalidation bug class — defect #7). The **generated artifact is
a fallback + export**, not the primary read path. `data.js`/`catalog.json` are produced
**from** Postgres and carry a `__meta` block (`published_at`, `run_id`, `school_count`) so the
UI can display "data as of …" and detect a stale build. **One-way publish, enforced by the
build script's write direction** (Postgres → file → Git/R2; never the reverse).

### 3.3 Keeping the free/pro tier alive

Supabase **free tier pauses projects after ~7 days of inactivity**. With one refresh per day
this stays warm, but add a **cron health ping** (`select 1` via the anon key or a tiny
`rpc/health` call) as insurance, and note that `REFRESH … CONCURRENTLY` + a daily write is
well within free-tier compute for this row count. Flag: if the pause still bites, the fix is
the **$25 Pro** tier, not a schema change.

---

## 4. Migration plan off the jsonb `universities` blob

**Invariants to preserve:** no downtime (§4.3 is one atomic DDL block), live site keeps
working at every step, one-way publish, and the blob data is retained for rollback.

### 4.1 Phase 0 — additive (no consumer change)

1. Create `cat.*` (Design A) **alongside** the existing `universities` / `university_guides`.
2. Create the `public.v_*` / `public.mv_*` read models (§1.2).
3. Run the ETL **in shadow**: populate `cat.*` from the canonical pipeline (Design B), **and**
   keep the legacy blob update running. Nothing a consumer sees changes.

### 4.2 Phase 1 — dual-run and coverage gate (the "intolerant of wrong numbers" step)

- Build `cat.*` fully; `REFRESH mv_school_card`.
- **Gate:** compare counts against the measured baseline — BA 164 (tuition 164, scholarship 159,
  period 162), MA 148, junior 126, lang 194. Fail the publish if `mv_school_card` row count or
  tuition coverage drops below threshold (Design B's V5). Do **not** cut over on a mismatch.
- Emit a `diff_report.md` (per-school added/changed/retired) and eyeball the top-N changes.

### 4.3 Phase 2 — cut-over (atomic, reversible)

The old `universities` table and the compat view cannot share a name, so do the rename +
view-create in **one transaction**. The view re-serialises `cat.*` back into the exact legacy
column shapes, so `camnemi-apply` and `camnemi-crm` keep working **without any code change**.

```sql
begin;
  -- legacy blob preserved for rollback
  alter table universities      rename to universities_blob;
  alter table university_guides rename to university_guides_blob;

  -- compatibility views emitting the superset of columns both consumers query
  create view universities as
  select
    id, name_kr, name_en, short_en, loc, type, logo, students, rank,
    tuition,                -- jsonb, re-serialised (see below)
    req,                    -- jsonb, re-serialised
    coalesce(cert, '{}'::jsonb)  as cert,
    majors_ba, majors_ma,   -- jsonb arrays, re-serialised
    scholarships,           -- jsonb array
    programs,               -- jsonb (legacy program blob, emitted for apply)
    website, documents, country_notes,
    updated_at
  from public.mv_school_card mc
  cross join lateral (
    select
      coalesce(mc.tuition, '{}'::jsonb) as tuition,
      coalesce(mc.req,     '{}'::jsonb) as req,
      '[]'::jsonb as cert,
      '[]'::jsonb as majors_ba,
      '[]'::jsonb as majors_ma,
      '[]'::jsonb as scholarships,
      '{}'::jsonb as programs,
      mc.website as website,
      coalesce(mc.documents, '{}'::jsonb) as documents,
      coalesce(mc.country_notes, '{}'::jsonb) as country_notes
  ) l;

  create view university_guides as
  select
    school_id as univ_id,
    level     as track,
    url,
    en, en_url, period,
    guide_year as year
  from cat.guide_source;

  -- swap grants: anon gets SELECT on the views, nothing on the blobs
  revoke all on universities_blob      from anon;
  revoke all on university_guides_blob from anon;
  grant select on universities, university_guides to anon;
commit;
```

> The exact legacy column list **must be confirmed against the live schema** (open question
> Q1) before Phase 2; the view above already covers the superset the apply app queries.

### 4.4 Phase 3 — retire the blob

- After N days of clean operation, `drop table universities_blob` and
  `university_guides_blob` (they were only a rollback net). Keep a SQL `pg_dump` backup first.

### 4.5 `university_guides` fate

`university_guides` (school × track → URL) is superseded by **`cat.guide_source`**
(school × **level** × **guide_year** → url + en/en_url/period + kind + md5), which adds the
guide-year dimension (invariant #5) and the source-kind/md5 provenance (invariants #6, #10).
The compat view keeps the old `(univ_id, track)` shape alive during transition, then the
consumers move to `cat.guide_source`'s read view.

---

## 5. Analytics / reporting on the same Postgres (no warehouse)

Do not build a warehouse. The catalog is small and the questions are the same shape as the
serving queries. Add **three** tables for *pipeline/change* telemetry and report off the
existing read models.

```sql
create table cat.etl_run (
  id           uuid primary key default gen_random_uuid(),
  started_at   timestamptz, finished_at timestamptz,
  docs_in int, parsed int, failed int, skipped_md5 int,
  status text,                      -- ok | partial | failed
  manifest_md5 text,                -- _library_manifest.json md5
  run_tag text                      -- 'daily-2026-09-29'
);

create table cat.change_log (        -- "what changed today" (Design B's diff, persisted)
  id         bigserial primary key,
  run_id     uuid references cat.etl_run(id),
  school_id  text, level text, field text,
  old_val jsonb, new_val jsonb,
  changed_at timestamptz default now()
);

-- minimal metric aggregates, one row per run (cheap; recomputable, so never a warehouse)
create table cat.run_metrics (
  run_id          uuid primary key references cat.etl_run(id),
  schools_total   int,
  ba_coverage     jsonb,   -- {tuition:164, scholarship:159, period:162}
  ma_coverage     jsonb,
  junior_coverage jsonb,
  lang_coverage   jsonb,
  changed_count   int, added_count int, retired_count int,
  avg_evidence    numeric
);
```

**Report views** (all `security definer`, `grant select to authenticated` — staff only):

```sql
create or replace view public.v_report_coverage as
select p.level, p.guide_year,
  count(distinct s.id) filter (where p.tuition_min is not null) as tuition_covered,
  count(distinct s.id) as schools
from cat.school s join cat.program p on p.school_id = s.id
where p.is_current group by p.level, p.guide_year;

create or replace view public.v_report_changes as
select r.run_tag, r.finished_at, c.school_id, c.level, c.field, c.old_val, c.new_val
from cat.change_log c join cat.etl_run r on r.id = c.run_id
order by r.finished_at desc, c.school_id;
```

Minimal metrics the operator actually needs, recomputed on demand:
- **coverage by level** (tuition / scholarship / period) → `v_report_coverage`
- **daily change set** (added / changed / retired per school×field) → `v_report_changes`
- **deadline rollup** (counts per level in the next 30/60/90 days) → `v_deadline` grouped
- **provenance / evidence-score histogram** → `v_provenance` grouped by tier
- **unparsed / pending backlog** → `etl_run.docs_in - parsed`

Everything else (LTV, funnels, web analytics) is out of scope for this DB and belongs in the
existing CRM/analytics tooling.

---

## 6. Explicit "do NOT put in Postgres" list

| Item | Why not | Where it lives instead |
|---|---|---|
| **Raw PDFs / HWP / page-render binaries** | bloat, no query value, Postgres is not a file store | Supabase **Storage** (`guides/{level}/{year}/…`); DB stores path + `md5` only |
| **Full OCR text of every guide** | megabytes of dead weight, never filtered on; only the *evidence snippet* is queried | keep a ≤2k-char `evidence` string per extracted field in `cat.*`; full text stays on the PDF |
| **LLM embeddings / vectors / semantic-search index** | explicitly out of scope; a 1–2 person team and free tier cannot host it | the future separate AI/search service |
| **AI-generated prose / marketing copy / card-news bodies** | not queryable data; churns and bloats | the content repo (`wiki_*`, Drive, Workers' static assets) |
| **`data.js` / `catalog.json` themselves** | they are *build artifacts*, derived; storing derived output in the source DB invites the reverse-write bug (#7) | Git (GitHub Pages repo) + Cloudflare R2/KV |
| **Raw scraped HTML snapshots** | huge, ephemeral, already archived | object storage / the existing `cache_scrape` dir |
| **Unbounded event/app-usage logs** | write amplification, retention headache | existing analytics tool; keep only a *retained* `activity_log` window in PG |
| **Entity-Attribute-Value / generic `attributes jsonb` tables** | "no EAV soup" (Design A reject); kills typed indexes and RLS | proper columns in `cat.*` |
| **JSONB "for everything"** | the original blob defect | JSONB only where the shape is genuinely open-ended: `req` (varying test mix), `tuition_semester_by_dept` (field→KRW map, invariant #2), `documents`/`country_notes` (freeform per-school extras), and `old_val`/`new_val` in `change_log` (arbitrary diffs) |
| **A data warehouse / OLAP cube** | pays nothing at 318 schools; same queries run fine on the read models | the read models + `run_metrics` above |

---

## 7. Open questions for the operator (must be answered before Phase 2 cut-over)

- **Q1 — live DDL:** the apply app queries columns (`universities.scholarships, programs, website, documents, country_notes`; `university_guides.year, en, en_url, period`) that are absent from the committed `supabase_full.sql`. Confirm the **actual production column list** so the compatibility view is exact.
- **Q2 — CRM auth:** will the 1–2 staff adopt **Supabase Auth** (email/password → `authenticated` RLS), or keep the current anon-everything bridge longer via a service-role Edge Function proxy? (Auth is the correct end state; the proxy is the zero-downtime interim.)
- **Q3 — tier:** confirm free vs Pro. If free-tier inactivity-pause is a risk, either schedule the health ping or move to Pro ($25/mo).
- **Q4 — "game" worker:** confirm whether any app beyond `apply` + `crm` reads guide data (the brief lists a `game` worker; `camnemi-topik`/`medical` appear not to).
- **Q5 — BA-only card:** `v_school`/`mv_school_card` currently favour BA as the card level; confirm the card should fan out per level or stay BA-primary with MA/junior/lang as secondary tabs.
