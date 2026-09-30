# Design A — Core Relational Schema for Camnemi Admission-Guide Database

Senior data-architecture proposal for the guide/admission domain (schools × degree levels ×
guide years), re-parsed daily from 모집요강 PDFs. Postgres 15+ via Supabase, 1–2 dev team.
Correctness + auditability over elegance; no AI/semantic search; no EAV; JSONB only where the
shape is genuinely open-ended (each use justified inline).

---

## 0. Design principles (read first)

1. **The guide year (학년도) is the version key.** A program is `(school × level × guide_year)`,
   one row per academic year. 2026 and 2027 data are *physically distinct rows*, so a 2026 value
   can never "overwrite" a 2027 value — the two school years coexist. See §2.
2. **`effective_year` ≠ `label_year`.** 17+ files named "2027" were actually 2026학년도
   (defect #5). The *verified* 학년도 is a first-class column on the source document, and every
   program row's `guide_year` is forced to equal its source document's `effective_year` by a
   trigger. The upsert key is the verified year, never the filename.
3. **Provenance is denormalised onto value rows, not a separate EAV evidence table.** Every
   value-bearing table carries `source_doc_id`, `parse_run_id`, `asserted_by`, `evidence`.
   Traceability to (PDF, parse run, model, tier, evidence score) is enforced with `NOT NULL`
   or `DEFAULT` so a value without provenance cannot be committed. Tier/model resolve through
   two joins, not per-cell storage.
4. **Language requirements are structural, not conventional.** A requirement lives only on
   degree programs (`ba`/`ma`/`junior`) and on `department` track columns; `lang` is excluded by
   `CHECK` + a trigger (invariant #1, §3.1).
5. **Track requirements are flattened, not nested JSON.** `korean_track`/`english_track` booleans
   plus per-track `topik/ielts/toefl` numeric columns live directly on `department`. "English-track
   majors for IELTS ≤ 5.5" is a plain indexed predicate (defect #3).
6. **Tuition is tier rows, not prose.** First-semester vs later-semester, per-credit vs
   per-semester are rows in `tuition` with a `tier` and `unit` enum (defect #2).
7. **Scholarships are two axes + tiered benefits** on a parent `scholarship` (type, category)
   with a `scholarship_tier` child (condition + benefit). (defect #4)
8. **Source kind is explicit** — `pdf | page-render | hwp-converted | screenshot` plus a URL
   (defect #10); parse-quality tier `A–E` live on the source document (defect #9).

---

## 1. Entity summary (table list)

| Table | Purpose | Key |
|---|---|---|
| `school` | Stable, curated school identity (not versioned) | `id` (slug) |
| `school_alias` | Alternative names for matching (전북대, JBNU) | `(school_id, alias)` |
| `program` | School × level × guide_year header (period, req, tuition range, apply system, lang structure, ieqas flags) | `(school_id, level, guide_year)` |
| `college` | Grouping college within a program | `id` |
| `department` | Major under a program/college, with both tracks + per-track topik/ielts/toefl | `id` |
| `tuition` | Tiered amount: scope(program/college/department) × tier(first/later semester, per-credit…) × unit | `id` |
| `application_round` | Application/announcement/registration periods (multiple per program) | `id` |
| `scholarship` | Two-axis scholarship (type × category) | `id` |
| `scholarship_tier` | Condition + benefit for one scholarship (tiered) | `id` |
| `source_document` | The PDF / rendered page / HWP file with md5, kind, URL, tier, label_year vs effective_year | `id` (md5 unique) |
| `parse_run` | One daily ETL invocation: model, pipeline version, timing | `id` |
| `curated_list` | A curated catalog (visa-restricted, medical, ai-departments, free-major) | `id` (slug) |
| `curated_list_item` | Membership + typed flags + open-ended `extra` | `id` |
| `academyinfo_ref` | Raw 대학알리미 tuition snapshot for cross-check (V4) | `(school_id, code)` |
| `change_log` | Append-only "what changed today" for the diff report | `id` |

Fees (app fee, admission fee) are two scalar columns on `program` — they never need their own
table (they are a fixed 2-tuple per program from the same source document).

---

## 2. Complete DDL

```sql
-- ============================================================
-- Camnemi guide-domain schema (Design A)
-- Target: Postgres 15+ / Supabase
-- ============================================================
begin;

create extension if not exists pgcrypto;   -- gen_random_uuid()

-- ---------- shared reference: curated schools (NOT versioned) ----------
create table school (
  id             text primary key,                    -- slug = canonical Korean name
  name_kr        text not null unique,
  name_en        text,
  short_en       text,
  region         text,
  loc            text,
  category       text not null default 'university'
                 check (category in ('university','junior_college','graduate','language')),
  type           text,                                -- 국립 | 사립 | ... (curated)
  logo           text,
  photo          text,
  students       int,
  foreign_students int,
  rank           int,
  academyinfo_id text,                                -- 대학알리미 schlId for cross-check
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create table school_alias (
  school_id text not null references school(id) on delete cascade,
  alias     text not null,
  kind      text not null default 'short'
            check (kind in ('short','english','hanja','misspell')),
  primary key (school_id, alias)
);
create index school_alias_lookup_idx on school_alias (alias);

-- ---------- source documents (the PDF library) ----------
create table source_document (
  id             uuid primary key default gen_random_uuid(),
  md5            char(32) not null unique,           -- content hash (library manifest)
  path           text not null unique,               -- G:\... library path
  name           text,
  level          text not null check (level in ('ba','ma','junior','lang')),
  label_year     smallint,                          -- year shown in filename/path
  effective_year smallint,                          -- VERIFIED 학년도 (≠ label possible)
  school_id      text references school(id) on delete set null,
  kind           text not null default 'pdf'
                 check (kind in ('pdf','page-render','hwp-converted','screenshot')),
  url            text,                               -- source web page/HWP (defect #10)
  bytes          bigint,
  text_chars     int,                                -- extracted text length (drives tier)
  tier           text not null default 'E'
                 check (tier in ('A','B','C','D','E')),  -- A≥5000c B≥1000 C≥200 D<200 E=non-doc
  status         text not null default 'present'
                 check (status in ('present','missing','archived','rejected')),
  collected_at   timestamptz,
  file_mtime     bigint,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  -- a filename labelled 2027 cannot really be a 2024 guide (guards mis-labelling)
  constraint src_year_sane check (
    effective_year is null or label_year is null
    or effective_year between label_year - 1 and label_year + 2)
);
create index source_document_level_year_idx on source_document (level, effective_year);
create index source_document_school_idx on source_document (school_id) where school_id is not null;

-- ---------- one daily parse/ETL invocation ----------
create table parse_run (
  id               uuid primary key default gen_random_uuid(),
  started_at       timestamptz not null default now(),
  finished_at      timestamptz,
  model            text,                              -- e.g. deepseek-v4-pro
  pipeline_version text,
  run_trigger      text not null default 'daily'
                   check (run_trigger in ('daily','manual','backfill')),
  doc_count        int not null default 0,
  changed_count    int not null default 0,
  status           text not null default 'running'
                   check (status in ('running','ok','failed')),
  note             text,
  created_at       timestamptz not null default now()
);

-- ---------- program = school x level x guide_year (VERSION UNIT) ----------
create table program (
  id               uuid primary key default gen_random_uuid(),
  school_id        text not null references school(id) on delete cascade,
  level            text not null check (level in ('ba','ma','junior','lang')),
  guide_year       smallint not null,                -- 학년도 the guide is FOR (verified)

  -- application period (prose; structured rounds in application_round)
  period_text      text,

  -- program-level language requirement (used when track_policy = 'unified' or 'none')
  topik_req        int,
  ielts_req        numeric(4,1),
  toefl_req        int,
  lang_req_text    text,                              -- free-form (junior multi-option prose)

  track_policy     text not null default 'per_department'
                   check (track_policy in ('per_department','unified','none')),

  -- tuition summary range (detail in tuition table)
  tuition_min      numeric(12,0),
  tuition_max      numeric(12,0),
  tuition_note     text,

  -- apply system / portal
  apply_system     text,
  apply_system_all text,

  -- language-course structure (meaningful only when level='lang')
  lang_per_term    text,
  lang_total_hours text,
  lang_dorm        boolean,
  lang_d4_eligible boolean,

  -- ieqas / degree certification
  ieqas_certified  boolean,
  ieqas_level      text,
  ieqas_course     text,
  ieqas_year       smallint,

  student_count    int,
  foreign_students int,
  note             text,

  status           text not null default 'draft'
                   check (status in ('draft','verified','published','retired')),
  is_current       boolean not null default false,   -- latest guide_year for (school,level)
  first_seen_at    timestamptz not null default now(),

  -- PROVENANCE (invariant #3 — mandatory)
  source_doc_id    uuid not null references source_document(id),
  parse_run_id     uuid references parse_run(id),    -- null = manual review
  asserted_by      text,                              -- model name or 'manual:<person>'
  evidence         numeric(3,2) not null default 0,  -- 0..1 confidence

  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),

  -- one program per (school, level, guide_year)
  unique (school_id, level, guide_year),

  -- invariant #1: a language course carries NO language requirement
  constraint program_lang_no_req check (
    level <> 'lang' or (
      topik_req  is null and ielts_req  is null and toefl_req  is null and lang_req_text is null
    ))
);
create index program_level_year_idx     on program (level, guide_year);
create index program_school_idx         on program (school_id);
create index program_current_idx        on program (level, guide_year) where is_current;

-- ---------- college (grouping within a program) ----------
create table college (
  id              uuid primary key default gen_random_uuid(),
  program_id      uuid not null references program(id) on delete cascade,
  name            text not null,
  tuition_note    text,
  sort_order      int not null default 0,
  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (program_id, name)
);
create index college_program_idx on college (program_id);

-- ---------- department (major) with BOTH tracks flattened ----------
create table department (
  id              uuid primary key default gen_random_uuid(),
  program_id      uuid not null references program(id) on delete cascade,
  college_id      uuid references college(id) on delete set null,
  name            text not null,                      -- major, e.g. 기계공학과

  -- track availability (defect #3 — plain indexed booleans)
  korean_track    boolean not null default false,
  english_track   boolean not null default false,

  -- per-track language requirements (flattened; NOT EAV)
  korean_topik    int,
  korean_ielts    numeric(4,1),
  korean_toefl    int,
  english_topik   int,
  english_ielts   numeric(4,1),
  english_toefl   int,
  track_req_text  text,                               -- free-form residual (junior)

  is_free_major   boolean not null default false,    -- curated flag
  is_ai           boolean not null default false,    -- curated flag
  sort_order      int not null default 0,

  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),

  unique (program_id, college_id, name)
);
create index department_program_idx      on department (program_id);
create index department_college_idx      on department (college_id) where college_id is not null;
-- the "English-track majors for IELTS ≤ 5.5" advising query:
create index department_english_ielts_idx on department (english_ielts) where english_track;
create index department_korean_topik_idx  on department (korean_topik)  where korean_track;
create index department_free_major_idx    on department (program_id)     where is_free_major;

-- ---------- tuition tiers (defect #2 — no prose) ----------
create table tuition (
  id              uuid primary key default gen_random_uuid(),
  program_id      uuid not null references program(id) on delete cascade,
  department_id   uuid references department(id) on delete cascade,  -- null = program/college scope
  college_name    text,                              -- college-level scope (when no college row)

  scope           text not null default 'program'
                  check (scope in ('program','college','department')),
  tier            text not null default 'semester'
                  check (tier in ('first_semester','later_semester','semester','per_credit','annual','other')),
  unit            text not null default 'per_semester'
                  check (unit in ('per_semester','per_credit','per_year','per_term')),
  amount_krw      numeric(12,0) not null
                  check (amount_krw >= 0 and amount_krw <= 20000000),  -- V3 outlier gate (0..20M KRW)
  note            text,
  sort_order      int not null default 0,

  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index tuition_program_idx on tuition (program_id);
create index tuition_program_dept_idx on tuition (program_id, department_id);

-- ---------- application rounds / periods ----------
create table application_round (
  id              uuid primary key default gen_random_uuid(),
  program_id      uuid not null references program(id) on delete cascade,
  round_label     text,                               -- 1차 / 2차 / 수시 / 정시 / 후기
  kind            text not null default 'application'
                  check (kind in ('application','announcement','registration','interview','other')),
  starts_on       date,
  ends_on         date,
  period_text     text,                               -- free-form residual
  sort_order      int not null default 0,

  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index app_round_program_idx on application_round (program_id);

-- ---------- scholarship (two axes) + tiered benefit ----------
create table scholarship (
  id              uuid primary key default gen_random_uuid(),
  program_id      uuid not null references program(id) on delete cascade,
  name            text not null,
  type            text not null check (type in ('enroll','existing')),   -- 입학 | 재학
  category        text not null default 'general'
                  check (category in ('academic','language','both','general')),
  note            text,

  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index scholarship_program_idx on scholarship (program_id);
create index scholarship_type_cat_idx on scholarship (type, category);

create table scholarship_tier (
  id              uuid primary key default gen_random_uuid(),
  scholarship_id  uuid not null references scholarship(id) on delete cascade,
  condition_type  text default 'general'
                  check (condition_type in ('topik','ielts','toefl','gpa','both','general','none')),
  condition_min   numeric,                            -- threshold (TOPIK level, IELTS, GPA)
  condition_text  text,                               -- free-form criteria
  benefit_type    text not null default 'percent'
                  check (benefit_type in ('percent','amount','fee_waiver','dorm','other')),
  benefit_value   numeric,                            -- percent number, or KRW amount
  benefit_text    text,                               -- free-form (수업료 100%)
  sort_order      int not null default 0,

  source_doc_id   uuid not null references source_document(id),
  parse_run_id    uuid references parse_run(id),
  asserted_by     text,
  evidence        numeric(3,2) not null default 0,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index scholarship_tier_sch_idx on scholarship_tier (scholarship_id);

-- ---------- curated lists ----------
create table curated_list (
  id              text primary key,                   -- slug: visa_restricted_2026, medical_reqs, ...
  name            text not null,
  source_text     text,                               -- citation (보도자료 등)
  effective_text  text,                               -- effective period prose
  note            text,
  updated_at      timestamptz not null default now()
);

create table curated_list_item (
  id              uuid primary key default gen_random_uuid(),
  list_id         text not null references curated_list(id) on delete cascade,
  school_id       text references school(id) on delete cascade,
  program_id      uuid references program(id) on delete cascade,
  department_id   uuid references department(id) on delete cascade,
  category        text,                               -- free-major category / medical dept group
  restrict_kind   text,                               -- visa: 'degree' | 'language'
  flag            boolean,                            -- e.g. english_track eligibility
  note            text,
  -- JSONB ONLY here: the residual per-list shape is genuinely open-ended
  -- (medical recruiting rows, ai depts map, free-major extra fields).
  extra           jsonb not null default '{}'::jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index cli_list_school_idx on curated_list_item (list_id, school_id);
create index cli_list_program_idx on curated_list_item (list_id, program_id) where program_id is not null;

-- ---------- 대학알리미 reference snapshot (cross-check only, V4) ----------
create table academyinfo_ref (
  school_id   text not null references school(id) on delete cascade,
  code        text not null,                          -- schlId
  -- JSONB ONLY here: raw external API snapshot used solely for validation
  -- (per-계열 tuition), never served; shape is upstream-defined.
  payload     jsonb not null,
  fetched_at  timestamptz not null default now(),
  primary key (school_id, code)
);

-- ---------- change log (append-only) powers "what changed today" ----------
create table change_log (
  id            bigserial primary key,
  parse_run_id  uuid references parse_run(id),
  changed_at    timestamptz not null default now(),
  entity        text not null,                        -- table name
  entity_id     uuid,
  school_id     text,
  level         text,
  guide_year    smallint,
  kind          text not null check (kind in ('insert','update','delete','retire')),
  field         text,
  old_value     text,
  new_value     text
);
create index change_log_parse_run_idx on change_log (parse_run_id);
create index change_log_school_entity_idx on change_log (school_id, entity);

-- ---------- shared updated_at trigger ----------
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at := now();
  return new;
end $$ language plpgsql;

create trigger trg_program_updated_at   before update on program            for each row execute function set_updated_at();
create trigger trg_college_updated_at   before update on college            for each row execute function set_updated_at();
create trigger trg_department_updated_at before update on department        for each row execute function set_updated_at();
create trigger trg_tuition_updated_at   before update on tuition            for each row execute function set_updated_at();
create trigger trg_appround_updated_at  before update on application_round  for each row execute function set_updated_at();
create trigger trg_scholarship_updated_at before update on scholarship      for each row execute function set_updated_at();
create trigger trg_schriptier_updated_at  before update on scholarship_tier for each row execute function set_updated_at();
create trigger trg_school_updated_at    before update on school             for each row execute function set_updated_at();

commit;
```

### DDL rationale (per decision)

- **`program` unique `(school_id, level, guide_year)`** — physically separates school years; this
  *is* the temporal skeleton. Nothing else needs a `valid_from/valid_to` range for correctness.
- **`source_doc_id NOT NULL` on every value table** — structural provenance (invariant #3). A row
  with no source PDF, no (nullable) parse run, and a `DEFAULT 0` evidence score can still be
  inserted by a human reviewer (`asserted_by='manual:name'`), which is the intended escape hatch —
  what is *prevented* is a value that slipped in without *any* trace.
- **Track req flattened on `department`** — a fixed set of ≤6 numeric columns per row is not EAV;
  it is the denormalised read shape the advising queries need. The partial indexes
  `where english_track` / `where korean_track` make the two headline queries plain index scans.
- **`scholarship` + `scholarship_tier` split** — the two axes (`type`, `category`) are
  per-scholarship-name; the condition/benefit is per-tier (TOPIK 6→100%, TOPIK 5→70%). A
  single-tier scholarship just has one tier row.
- **Tuition as rows with `tier`+`unit` enums** — kills the prose-tuition failure (#2) while
  keeping first-vs-later-semester and per-credit-vs-per-semester queryable and numeric.
- **`lang_*` columns instead of a `req` blob on lang** — lang has *no* language requirement; it
  has a *structure* (term, hours, dorm, D4 eligibility), modelled as typed columns not a
  requirement row.
- **`curated_list_item.extra` and `academyinfo_ref.payload` are the only two JSONB columns**, each
  justified: the curated lists carry heterogeneous residual fields, and the academyinfo snapshot is
  a raw upstream API payload used only for cross-validation, never served.

---

## 3. Structural enforcement of the three invariants

### 3.1 `lang` carries NO topik/ielts/toefl

Two layers, both in the schema/constraint layer (not the application):

1. `CHECK program_lang_no_req` — program-level requirement columns must all be NULL when
   `level='lang'`.
2. Trigger that blocks a `department` (the *other* place a requirement can live) from ever hanging
   under a `lang` program — closing the path the original LLM-merge bug walked:

```sql
-- Departments/tracks can only exist under degree programs, never lang.
create or replace function trg_no_department_under_lang() returns trigger as $$
declare p_level text;
begin
  select level into p_level from program where id = new.program_id;
  if p_level = 'lang' then
    raise exception 'invariant: cannot attach a department/track to a lang program (level=lang has no requirement)';
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_department_no_lang before insert or update on department
  for each row execute function trg_no_department_under_lang();
```

### 3.2 A 2026 value must never overwrite a 2027 value

Enforced by **row separation + a source-year guard trigger**:

- Programs are distinct rows per `guide_year` (`unique (school_id, level, guide_year)`); writing a
  2026 value "over" a 2027 value is structurally impossible — it would be a *different* row.
- The actual production failure was a parse of a 2026 document being upserted under
  `guide_year=2027` (label confusion). The guard trigger makes that impossible: a program row's
  `guide_year` must equal its source document's `effective_year`.

```sql
create or replace function trg_program_year_must_match_source() returns trigger as $$
declare src_eff smallint;
begin
  select effective_year into src_eff from source_document where id = new.source_doc_id;
  if src_eff is null then
    raise exception 'source document % has no verified effective_year; cannot assign a program', new.source_doc_id;
  end if;
  if new.guide_year <> src_eff then
    raise exception 'invariant: guide_year % does not match source effective_year % (label mis-match)',
      new.guide_year, src_eff;
  end if;
  return new;
end $$ language plpgsql;

create trigger trg_program_year_guard before insert or update on program
  for each row execute function trg_program_year_must_match_source();
```

The same rule applies to every child table (tuition, department, scholarship, …): their
`source_doc_id` must belong to a document whose `effective_year` equals the parent program's
`guide_year`. The ETL contract (§4) enforces this by construction (children are written inside the
parent upsert); a child-level trigger can be added if desired — one function, parametrised by the
FK column, is enough.

A **newer** guide (higher `guide_year`) *may* retire an older one: the ETL sets
`program.is_current = false` on the superseded row and `true` on the new one, and flips
`status='retired'` — the older row's values are never mutated.

### 3.3 Every value traceable to (source PDF, parse run, model, tier, evidence score)

- `source_doc_id` → the PDF/rendered file (which carries `tier` and `url`/`kind`).
- `parse_run_id` → which daily run, which `model`, which `pipeline_version`.
- `asserted_by` → the model or `manual:<person>`.
- `evidence` → 0..1 confidence score.

These four columns are present **on every value table** and `source_doc_id` is `NOT NULL`, so the
DB refuses a trace-less value. The full join to render a provenance line is:

```sql
-- "show me where this tuition number came from"
select t.amount_krw, t.evidence,
       sd.path, sd.tier, sd.kind, sd.url, sd.effective_year,
       pr.run_trigger, pr.model as run_model, pr.pipeline_version
from tuition t
join source_document sd on sd.id = t.source_doc_id
left join parse_run pr  on pr.id = t.parse_run_id
where t.id = :tuition_row_id;
```

---

## 4. Temporal / versioning strategy

### How years coexist
Each `program` row is keyed `(school, level, guide_year)`. The 2026 and 2027 guides for the same
school are two rows; nothing is overwritten. `program.is_current` marks the highest published
`guide_year` per `(school, level)` (maintained by the ETL, not by application code).

### "Which guide was current on date X"
Currency is defined by the guide's `effective_year` and its application-window coverage; we do not
need a `valid_from/valid_to` pair because application rounds carry the real dates.

```sql
-- the guide/application window current on date X for a given school+level
with latest as (
  select p.*,
         row_number() over (
           partition by school_id, level
           order by guide_year desc, first_seen_at desc) as rn
  from program p
  where p.status in ('verified','published')
    and p.guide_year <= (select max(effective_year) from source_document sd
                          where sd.collected_at <= :x)   -- only guides that existed by X
)
select * from latest where rn = 1 and school_id = :school and level = :level;
```

For the stricter "the application period *open* on date X", filter `application_round` instead:

```sql
select p.*, ar.round_label, ar.starts_on, ar.ends_on
from program p
join application_round ar on ar.program_id = p.id and ar.kind = 'application'
where p.school_id = :school and p.level = :level
  and ar.starts_on <= :x and (ar.ends_on is null or ar.ends_on >= :x);
```

### "What changed today" (daily diff)
Two independent answers, both cheap:

1. **`change_log`** — append-only rows written by the ETL for every insert/update/retire, joined to
   `parse_run`. `select * from change_log where parse_run_id = :todays_run` is today's diff,
   grouped by `(school, level, guide_year)` and `field`. This is the primary feed for the
   `diff_report.md` / Telegram notification.
2. **Two-year compare** — since years coexist as rows, `guide_year N` vs `guide_year N-1` for the
   same `(school, level)` is a row-wise join, no snapshots needed:

```sql
select c.school_id, c.level,
       c.tuition_min as this_min, p.tuition_min as prev_min,
       c.topik_req  as this_topik, p.topik_req as prev_topik
from program c
join program p on p.school_id = c.school_id and p.level = c.level and p.guide_year = c.guide_year - 1
where c.guide_year = :current_year;
```

### Daily pipeline contract (brief)
- Upsert key = `(school_id, level, effective_year)` — **never** the filename year.
- Idempotent: `insert ... on conflict (school_id, level, guide_year) do update`, children deleted
  and re-inserted by `program_id` (they are pure derivatives of one source document).
- Soft-retire: programs whose school × level no longer has a current-cycle document get
  `is_current=false` / `status='retired'`, never deleted, so historical lookups survive.
- Rollback: the whole run is one transaction per `parse_run_id`; on failure, `parse_run.status='failed'`
  and the transaction rolls back atomically (children + program together).
- Derived stores (`verified_kb.json`, `consulting_db.json`, `data.js`, the xlsx) and the
  CRM/site Supabase tables are **fill-only** reads (§5) — enrichments never flow back (defect #7).

---

## 5. Serving layer + one-way publish (summary)

- **Postgres is the source of truth.** `verified_kb.json` / `consulting_db.json` / `data.js` become
  *generated artifacts* published from Postgres (one-way). Enrichment that used to be hand-edited in
  those files now lands in Postgres first (as `asserted_by='manual'` rows or `curated_list_item`).
- **Analytics/reporting** read straight from Postgres; a materialized view
  `mv_program_current` (or just `is_current=true`) is the denormalised read model.
- **Web apps (Supabase anon + RLS)** read via a *published-only* view with `using (true)` policy
  but scoped to `status='published' and is_current`, so drafts and unverified rows are not served.
- **What does NOT live in Postgres:** the raw PDF/DOCX bytes (stay on the shared drive; Postgres
  stores `path` + `md5`), the LLM semantic-search index (explicitly out of scope), and minified
  `data.js` (a generated file, never a source). Format contracts (indent=1+LF for the JSON stores,
  minified for `data.js`) are enforced in the *publisher*, since the DB is never hand-edited (defect #8).

---

## 6. Open questions

1. **Track requirement at program vs department level.** The data uses `track_policy`
   (`unified` vs `per_department`). Should `program.topik_req`/`ielts_req` be allowed when
   `track_policy='per_department'`, or must all per-school req live on departments in that mode?
   (Current DDL permits both; the ETL decides. Recommend: two separate read paths, never both.)
2. **Currency definition.** Confirm "current" = latest `guide_year` regardless of application
   window vs "the window actually open today" — lead-time between guide publication and
   application open is real (~Feb publish → Sep intake). This affects `is_current` semantics only,
   not the schema.
3. **`parse_run` as transaction boundary.** Multi-document runs (330 docs) are unlikely to fit in
   one transaction comfortably — do we group by `parse_run_id` but commit per-document (rollback
   per source doc, not per day)? Recommend per-source-document transaction, tagged with one
   `parse_run_id`.
4. **Cell- vs row-level evidence.** Row-level provenance (one `source_doc_id` per row) is assumed;
   if a single department's `topik` and `ielts` ever come from *different* documents, we need a
   `value_evidence` table. Believed unnecessary — confirm.
5. **School `category` vs `level`.** `junior_college` schools only offer `junior`/`lang`, but the
   canonical data mixes levels under one school slug. Confirm the school→level allowed-matrix
   (or leave it unconstrained as now).
6. **`scholarship.type` boundary.** Is a scholarship that is "TOPIX 6 → first-semester 100% + later
   30%" one `enroll` scholarship with two tiers, or two scholarships sharing a name? Current data
   represents both as separate array entries; the `tier` child handles both, but confirm the
   intended normalization for the advising report.