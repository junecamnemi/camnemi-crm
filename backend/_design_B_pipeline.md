# Camnemi Guide DB — Daily Ingestion + Provenance/Audit Contract (Design B)

Scope: from "a new/changed 모집요강 PDF/page appears" to "the published read models reflect it".
Companion to the schema design (Design A: tables/DDL for the guide domain). This document
owns the **state machine, keys/idempotency, supersede/versioning, rollback/publish gates,
audit trail, and observability**. Read models (`consulting_db.json`, `data.js`, Supabase) are
treated here as publish *targets*; their schema is a projection of `program_current`.

Guiding principles (drawn from the production invariants):

1. **Correctness and auditability beat elegance.** Every number must trace to (PDF, page/section,
   parse run, model, tier, evidence score).
2. **Fill-only + year-gated writes.** A 2026 value must never overwrite a 2027 value; a newer
   guide may overwrite. Older years fill gaps only.
3. **Content-hash gating everywhere.** Nothing is re-parsed or re-merged unless its bytes changed.
4. **Soft-delete, never hard-delete.** Superseded programs and dropped majors are *retired*, not
   removed, so "which guide was current on date X" stays answerable.
5. **Derived stores are one-way projections.** Postgres is the system of record; file stores are
   rebuilt atomically and fill-only, never the reverse.

---

## 1. State machine per document

One `guide_document` row = one physical source (PDF or rendered page/HWP) in the library.
Its `status` drives the whole pipeline. Statuses are a Postgres enum.

### 1.1 States

Progressive (in order):

| # | status       | meaning                                                                 |
|---|--------------|-------------------------------------------------------------------------|
| 0 | `detected`   | Detector saw current-year recruiting content, or a library scan saw a new file. |
| 1 | `fetched`    | Bytes collected into the library; `content_hash` (md5) computed.         |
| 2 | `identified` | `school_id` (canonical key), `level`, and **resolved** `guide_year` set. |
| 3 | `tiered`     | `doc_tier.classify` assigned A/B/C/D/E + `text_len` + `ocr_used`.        |
| 4 | `parsed`     | LLM extraction returned strict JSON; evidence check ran.                 |
| 5 | `verified`   | `kb_verify.score` produced accept / escalate / review.                   |
| 6 | `review`     | Parked for a human (score < 0.50, or tier D). Not auto-merged.           |
| 7 | `merged`     | Values written into `program` + children (fill-only, year-gated).        |
| 8 | `published`  | Read models rebuilt from `program_current`; publish gate passed.         |

Terminal:

| status                | meaning                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| `rejected_duplicate`  | `content_hash` already present for this (school, level). No-op.          |
| `retired_stale`       | Superseded by a newer guide_year (or same-year newer md5). Kept for audit. |
| `unreadable`          | 0 pages / corrupt / blank body (`guide_library --validate` or pymupdf open fail). |
| `rejected_nondoc`     | Tier E (web capture) after re-collect retries exhausted.                 |

### 1.2 Transitions

```
                    ┌──────────────────────────────────────────────┐
                    │                (library scan / detector)       │
                    ▼                                                │
   (re-collect)  detected ──fetch──▶ fetched ──identify──▶ identified
        ▲             │                 │                     │
        │   (md5 dup) │    (0-page/     │    (can't open)      │
        │             ▼    corrupt)     ▼                     ▼
        │      rejected_duplicate  unreadable              tiered
        │                                                      │
        └──(E tier, retries < N)─── tier E ──(retries exhausted)──▶ rejected_nondoc
                                       │  (A/B/C/D)
                                       ▼
                                    parsed ──(bad/empty JSON, retry)──▶ (re-parse, same state)
                                       │
                                       ▼
                                   verified ──score──▶ accept ──▶ merged ──gate──▶ published
                                       │ │                    ▲
                                       │ └── escalate ────────┘ (re-parse w/ pro, new attempt)
                                       └── review ──▶ (human accepts) ──▶ merged
                                              └── (human rejects) ──▶ review (stays; no merge)

   published ──(newer guide_year OR newer md5 same year)──▶ retired_stale (old doc)
```

Rules:

- **`fetched → identified`** needs `school_keys.resolve()` to succeed *and* `guide_year`
  resolved. `folder_year` is **untrusted** (17+ schools labelled 2027 were really 2026학년도);
  `guide_year` comes from document text/meta, cross-checked against folder.
- **`tiered` = E** does **not** fail the run; it enqueues re-collection (fetch the real PDF /
  re-render the page). `reattempts` increments; after `max_recollect_attempts` → `rejected_nondoc`.
- **`verified` = escalate** re-parses with the pro model as a *new* `parse_attempt`, staying in
  `verified` until a definitive verdict.
- **`verified` = review** moves to `review`; merge never touches it. A human promotes to
  `merged` (with a `run_kind='manual'` run) or leaves it parked.
- **Terminal states are stable** — a row in a terminal state is only revisited if its
  `content_hash` changes (the file was replaced on disk), which resets it to `fetched`.

### 1.3 Status columns

```sql
create type guide_level as enum ('ba','ma','junior','lang');
create type guide_source_kind as enum ('pdf','page_render','hwp_converted');
create type doc_tier as enum ('A','B','C','D','E');
create type doc_status as enum (
  'detected','fetched','identified','tiered','parsed','verified','review','merged','published',
  'rejected_duplicate','retired_stale','unreadable','rejected_nondoc'
);
create type parse_verdict as enum ('accept','escalate','review','reject');
create type run_status as enum ('running','succeeded','failed','aborted','killed');
create type program_status as enum ('active','stale','withdrawn');
create type scholarship_type as enum ('enroll','existing');
create type scholarship_category as enum ('academic','language','both','general');
create type benefit_kind as enum ('percent','amount','fee_waiver','dorm_fee','other');

create table guide_document (
  id bigint generated always as identity primary key,
  content_hash text not null,                 -- md5 of raw bytes (mirrors _library_manifest.json)
  library_path text,                          -- canonical path on G: drive
  file_name text not null,
  level guide_level not null,
  folder_year text,                           -- UNTRUSTED: year from folder path
  guide_year text,                            -- RESOLVED 모집 year ('2026'|'2027'|null)
  school_id text references school(id),       -- null until identified
  source_kind guide_source_kind not null default 'pdf',
  source_url text,                            -- for page_render / hwp_converted
  bytes bigint,
  tier doc_tier,
  text_len int,
  ocr_used boolean not null default false,
  page_count int,
  status doc_status not null default 'detected',
  reject_reason text,
  reattempts int not null default 0,
  first_seen_at timestamptz not null default now(),
  last_status_at timestamptz not null default now()
);

create index gd_content_hash_idx  on guide_document (content_hash);
create index gd_school_level_idx  on guide_document (school_id, level, status);

-- Byte-identical dedupe key: same bytes serving different school/level must BOTH survive
-- (숭실대 ba vs ma). Unique only within (content_hash, level, school).
create unique index gd_dedupe_key
  on guide_document (content_hash, level, coalesce(school_id, ''));
```

---

## 2. Core value model (referenced by provenance)

Typed columns on `program` for the hot query path; child tables for the genuinely relational
shapes. JSONB is reserved for open-ended prose (notes, verbatim strings).

```sql
create table school (
  id text primary key,                        -- canonical key from school_keys.json (e.g. '가천대학교')
  name_kr text not null,
  name_en text,
  region text,
  kind text not null default 'univ',          -- 'univ' | 'junior_college'
  status text not null default 'active',
  updated_at timestamptz not null default now()
);

create table program (
  id bigint generated always as identity primary key,
  school_id text not null references school(id),
  level guide_level not null,
  guide_year text not null,                   -- cycle this program admits
  status program_status not null default 'active',
  -- hot-path typed scalars (all evidence-checked before write)
  topik_req text, ielts_req text, toefl_req text,
  period_start date, period_end date, period_raw text,
  app_fee int, admission_fee int,
  tuition_semester int,                        -- school-level representative tuition
  apply_system text,
  ieqas_certified boolean, ieqas_level text,
  student_count int,
  notes jsonb not null default '{}'::jsonb,    -- open-ended prose only
  effective_from timestamptz not null default now(),
  effective_to timestamptz,                    -- null = current; set on supersede/withdraw
  published_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (school_id, level, guide_year)
);

-- INVARIANT #1: lang programs carry no language requirement (structural, not convention).
alter table program add constraint lang_no_lang_req
  check (level <> 'lang' or (topik_req is null and ielts_req is null and toefl_req is null));

create table program_round (                   -- possibly multiple application rounds
  id bigint generated always as identity primary key,
  program_id bigint not null references program(id) on delete cascade,
  round_no int not null default 1,
  label text,                                  -- '원서접수' | '추가모집' ...
  period_start date, period_end date, period_raw text,
  status program_status not null default 'active',
  unique (program_id, round_no)
);

create table department (                      -- per-department, two-track (INVARIANT #3)
  id bigint generated always as identity primary key,
  program_id bigint not null references program(id) on delete cascade,
  college text, major text not null,
  korean_track boolean not null default true,
  english_track boolean not null default false,
  korean_topik text, korean_ielts text,
  english_topik text, english_ielts text,
  status program_status not null default 'active',
  withdrawn_reason text,
  unique (program_id, college, major)
);
create index dept_english_track_idx on department (program_id) where english_track;
create index dept_ielts_idx on department (english_ielts);

create table tuition_tier (                    -- per-department + first-vs-later semester (INVARIANT #2)
  id bigint generated always as identity primary key,
  program_id bigint not null references program(id) on delete cascade,
  department_id bigint references department(id) on delete cascade,
  college text, major text,
  tier_label text,                             -- '인문' | '자연' | 'first_semester' | 'later_semester'
  semester text,                               -- 'first' | 'later' | null (every semester)
  amount_krw int not null,
  status program_status not null default 'active'
);
create index tuition_program_college_idx on tuition_tier (program_id, college);

create table scholarship (                     -- two axes: type × category (INVARIANT #4)
  id bigint generated always as identity primary key,
  program_id bigint not null references program(id) on delete cascade,
  name text not null,
  s_type scholarship_type not null,            -- enroll | existing
  category scholarship_category not null,      -- academic | language | both | general
  condition text, benefit text,
  benefit_kind benefit_kind, benefit_value numeric,
  status program_status not null default 'active'
);
create index scholarship_axes_idx on scholarship (program_id, s_type, category);
```

---

## 3. Run & audit tables (the provenance contract)

```sql
create table parse_run (
  id uuid primary key default gen_random_uuid(),
  run_kind text not null default 'daily',      -- daily | manual | backfill | reparse
  trigger_type text,                           -- cron | manual | retry
  target_year text,                            -- authoritative year for this run
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status run_status not null default 'running',
  input_count int, parsed_count int,
  accept_count int, escalate_count int, review_count int, reject_count int,
  tier_counts jsonb not null default '{}'::jsonb,
  merged_doc_count int, merged_field_count int,
  published boolean not null default false,
  publish_gate jsonb not null default '{}'::jsonb,   -- per-gate results
  coverage_delta jsonb not null default '{}'::jsonb,
  rollback_to uuid references parse_run(id),
  error text, killed_by text
);

create table parse_attempt (                   -- one LLM call (or retry) for one doc
  id bigint generated always as identity primary key,
  run_id uuid not null references parse_run(id) on delete cascade,
  document_id bigint not null references guide_document(id),
  attempt_no int not null default 1,
  tier doc_tier, model text, prompt_ver text,
  status text not null,                        -- ok | bad_json | empty_response | http_401 | http_error | evidence_fail | error
  verdict parse_verdict,
  score numeric(5,3),
  evidence jsonb,                              -- per-field: {field: {"hit":bool,"snippet":"..."}}
  raw_response text,                           -- truncated model output (audit)
  usage jsonb not null default '{}'::jsonb,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  error text
);
create index pa_run_idx on parse_attempt (run_id);
create index pa_doc_idx on parse_attempt (document_id, attempt_no desc);

-- Append-only per-field provenance. The CURRENT value of a field has superseded_at = null;
-- superseded rows are the history. One table serves both "current provenance" and "audit log".
create table field_provenance (
  id bigint generated always as identity primary key,
  program_id bigint not null references program(id) on delete cascade,
  entity_kind text not null,                   -- program | round | department | tuition | scholarship
  entity_id bigint,                            -- child row id when entity_kind <> 'program'
  field text not null,
  value jsonb not null,                        -- snapshot of the value as written
  guide_year text not null,                    -- year of the doc that produced it
  document_id bigint references guide_document(id),
  attempt_id bigint references parse_attempt(id),
  run_id uuid references parse_run(id),
  model text, tier doc_tier,
  evidence_score numeric(5,3),
  evidence jsonb,
  source_kind guide_source_kind, source_url text,
  page_ref text,                               -- page/section when extractable
  written_at timestamptz not null default now(),
  superseded_at timestamptz                    -- set when a newer write replaces this value
);
create index fp_current_idx on field_provenance (program_id, field, superseded_at, written_at desc);
create index fp_entity_idx  on field_provenance (entity_kind, entity_id);
create index fp_run_idx     on field_provenance (run_id);

-- "What changed today", one row per value transition (old vs new side by side).
-- Denormalized from field_provenance for cheap human diff + reporting.
create table field_change (
  id bigint generated always as identity primary key,
  run_id uuid not null references parse_run(id) on delete cascade,
  program_id bigint not null references program(id) on delete cascade,
  entity_kind text not null, entity_id bigint,
  field text not null,
  guide_year_from text, guide_year_to text,
  old_value jsonb, new_value jsonb,
  document_id bigint references guide_document(id),
  changed_at timestamptz not null default now()
);
create index fc_run_idx on field_change (run_id);
create index fc_program_idx on field_change (program_id, changed_at desc);

-- Kill-switch / thresholds (operated via `app_settings`-style keys; survives redeploys).
create table pipeline_setting (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);
-- keys: current_guide_year, kill_switch(bool), coverage_tol, max_recollect_attempts,
--       model_map, alert_webhook, publish_enabled(bool)
```

`program_current` view — the single read model the derived stores project from:

```sql
create view program_current as
select * from program
where status = 'active' and effective_to is null;
-- one row per (school_id, level): the highest guide_year is kept active; older rows are stale.
```

"Which guide was current on date X":

```sql
select * from program
where school_id = :s and level = :l
  and effective_from <= :X and (effective_to is null or effective_to > :X);
```

---

## 4. Upsert keys, idempotency, re-run safety

### 4.1 Natural keys

| table            | key                                                            |
|------------------|----------------------------------------------------------------|
| `school`         | `id` (canonical key)                                           |
| `guide_document` | `(content_hash, level, coalesce(school_id,''))` unique index   |
| `program`        | `(school_id, level, guide_year)`                               |
| `program_round`  | `(program_id, round_no)`                                       |
| `department`     | `(program_id, college, major)`                                 |
| `parse_attempt`  | append-only (no natural key); `(document_id, attempt_no)` index |
| `field_provenance` | append-only; "current" = `superseded_at is null`             |

### 4.2 Idempotency rules

1. **Content-hash gating is the primary dedupe.** A document is (re)processed iff its
   `content_hash` differs from the last successful processing. Same hash ⇒ skip, regardless of
   state. The library manifest md5 is authoritative; the DB stores a copy in `content_hash`.
2. **Re-run of the same bytes is a no-op** at every stage: `guide_document` upsert finds the
   existing row (dedupe key), parse is skipped (`status >= 'parsed'` and hash unchanged), merge
   writes only fields that actually changed (`old == new` ⇒ no `field_change` row, no
   `field_provenance` append), publish is a pure projection.
3. **Fill-only merge** is idempotent by construction: a field already populated by a newer-or-equal
   year is never rewritten by an older year, and a same-year re-merge of identical values is a no-op.
4. **Year gate** (see §5) makes supersede deterministic: supersede is keyed to `guide_year`
   ordering, so re-applying a supersede is idempotent.

### 4.3 Partial-failure resume

All pipeline state lives in the DB, so a killed run resumes by *status*, not by file timestamp:

```
resume queue = select * from guide_document
               where status in ('detected','fetched','identified','tiered')
                 or (status in ('parsed','verified') and not has_successful_attempt(content_hash))
```

- A 401/timeout mid-call leaves the doc in `tiered` with only failed `parse_attempt` rows ⇒ picked
  up next run (or the same run's retry).
- **401 token expiry**: re-read the Nous token on every call (it lives ~1h) and, on `http_401`
  specifically, refresh + retry with backoff (bounded). After N attempts → `parse_attempt.status =
  'http_401'`, doc stays `tiered`, alert fires. Never lose the doc.
- **Reasoning-model empty response**: `content` empty but `reasoning_content` present ⇒ strip and
  re-JSON-parse; both empty ⇒ `empty_response` attempt, retry once with a simpler prompt, then
  escalate to pro; still empty ⇒ `review`.

Pseudocode for the safe re-run gate:

```python
def needs_parse(doc, last_attempt):
    if doc.status in ('merged','published','rejected_duplicate','retired_stale'):
        return False
    if last_attempt and last_attempt.content_hash == doc.content_hash \
       and last_attempt.status == 'ok' and last_attempt.verdict == 'accept':
        return False          # already parsed this exact content
    return True
```

---

## 5. Supersede, versioning, "current", stale/withdrawn

### 5.1 What is versioned

- **`program` is the version unit**: one row per (school, level, guide_year). A new cycle does not
  mutate the old row — it creates a new one and retires the old.
- **Children (`round`, `department`, `tuition_tier`, `scholarship`) are versioned via their
  `program_id` FK** — they belong to a specific cycle and are retired along with it.
- **`field_provenance` is append-only**; every write snapshots `value`, `guide_year`, doc, run,
  model, tier, evidence. Nothing is updated in place except `superseded_at`.

### 5.2 How a changed guide supersedes an old one

```
on new doc (content_hash H', same school+level, resolved guide_year Y'):
  1. Y' > current program's guide_year  -> create program(Y'), retire program(Y_old):
        program(Y_old).status='stale'; effective_to = now()
        its guide_document.status = 'retired_stale'
  2. Y' == current guide_year (same-year revision, new md5)  -> update program(Y'):
        for each changed field: write value + field_provenance (supersede prior row)
                                + field_change row
  3. Y' <  current guide_year -> fill gaps only (see 5.4); never overwrite
```

### 5.3 How "current" is resolved

- Exactly one `program` per (school, level) has `status='active' AND effective_to IS NULL`.
- `program_current` is that projection; the derived stores read only it.
- Gap-filling means the current-year program row may carry a value whose `field_provenance.
  guide_year` is an older year — provenance records the truth, not the row's own `guide_year`.

### 5.4 Year gate (fills vs overwrite) — the exact rule

Let `C = current_guide_year` from `pipeline_setting` (e.g. '2027'), `Y = doc.guide_year`:

```
write(field, val):
    prev_year = field_provenance.latest(program, field).guide_year   # null if empty
    if Y == C:                       overwrite (supersede), record change if old != val
    elif prev_year is None:          fill gap (any older year may seed an empty field)
    else:                            skip — older year must never overwrite
    # Y > C: config error -> abort run (a future cycle appearing before the flag flipped)
```

This is exactly `_merge_llm_into_kb.py`'s `upgrade_years` semantics, promoted to a transactional,
per-field rule with provenance.

### 5.5 Stale / withdrawn handling

- **Deadline passed** → `program_round.status` flips to `stale` by a cheap daily sweep
  (`where status='active' and period_end < current_date`). Computed, soft, reversible; "open
  applications" reads filter `status='active'`.
- **Major dropped from a new guide** → the department is absent from the new cycle's text. Only
  withdraw when (a) the new doc is tier A/B (high text confidence) **and** (b) the major is
  *confirmed absent* (evidence: name not in new text). Otherwise flag `review` — a parse gap must
  not masquerade as a program cancellation. Withdrawn department → `status='withdrawn'` +
  `withdrawn_reason='absent_from_guide_2027'`; row is kept, excluded from current reads.
- **A school disappears entirely** from its current-year folder → the program stays `active` on
  last-known values and the school goes to `guide_watchlist` `watch`/`needs_url`; the detector
  keeps looking. No auto-withdraw of a whole program without a positive signal.

---

## 6. Rollback & blast-radius control

### 6.1 Per-run transaction

The merge is a single transaction; publish is gated and happens only after commit of the merge.

```
with txn():
    merge_into_program(doc) for each accepted doc      # writes program/children/provenance/change
    result = run_publish_gates(run)                    # see 6.3
    if result.failed:
        raise Abort(result.failures)                   # -> rollback whole merge
    commit()                                            # merge is durable only if gates pass
publish(run)                                            # read models built from committed state
```

Blast radius = one run's writes. A failed run rolls back `program`/`provenance`/`change` to the
pre-run snapshot (`parse_run.rollback_to` points at the last good run id). Parse results themselves
(`guide_document`, `parse_attempt`) are *kept* — they are non-destructive observations, so the next
run doesn't re-spend LLM tokens.

### 6.2 Publish gate ordering

Derived stores are written atomically (`tmp` + `os.replace`), never in place, and only after all
gates pass. `consulting_db` merge stays **fill-only** so enrichment survives; `data.js` is a
minified projection; Supabase is upserted last (anon-readable, RLS read-only for the pipeline's
service role).

### 6.3 Gates that must ABORT the publish

| # | gate                                            | abort condition                                                        |
|---|-------------------------------------------------|------------------------------------------------------------------------|
| 1 | Coverage regression (`coverage_guard`)           | any level×field in a derived store drops > `coverage_tol` (10%) below source |
| 2 | Lang invariant (`lang_no_lang_req`)              | any lang program with topik/ielts/toefl set                            |
| 3 | Tier safety                                      | any `merged` write originating from tier D or E (D/E never auto-merge) |
| 4 | Year-gate violation                              | any write where incoming year < existing year for that field           |
| 5 | Numeric sanity                                   | negative/non-numeric tuition/fee/score (hallucination canary)          |
| 6 | Unreadable current guide                         | > N schools whose *only* current guide is `unreadable` would silently lose coverage |
| 7 | Duplicate/partial availability                   | a (school, level) ended the run with zero active programs and no terminal reason |

Any gate failure ⇒ `parse_run.status='aborted'`, `publish_gate` records which gate and why, merge
rolled back, **nothing published**, alert fires.

### 6.4 Rollback command

```
rollback_run(run_id):
    txn: delete field_change/provenance/child-rows/program rows written_by run_id
         restore program.status/effective_to per field_change (undo supersede)
         parse_run.status='aborted', rollback_to = last good run
    # derived files untouched: they were never rewritten because publish never ran
```

---

## 7. Audit trail

### 7.1 Parse runs

`parse_run` + `parse_attempt` give the full lineage of every extraction:
run → document → attempt → (model, prompt_ver, tier, score, evidence, usage, raw_response).
Every `field_provenance.attempt_id` and `.document_id` closes the loop.

### 7.2 Per-field provenance

`field_provenance` is the contract: for **every** value in the read models there is a row stating
`(program, field, value, guide_year, document, attempt, run, model, tier, evidence_score, evidence,
source_kind, source_url, page_ref)`. The `verified_kb` `_llm_parsed` field becomes a *query*, not a
stored blob.

### 7.3 "What changed today" for humans

Generated from `field_change` filtered by today's run, rendered as markdown:

```markdown
# Guide changes 2026-09-29 (run 3f2a…)
## 가천대학교 — BA 2027  (source: 가천대_외국인_모집요강_2027.pdf)
- period: "2026.09.01~09.30" → "2026.09.01~10.02"   [tier A, ev=1.00]
- tuition_semester: 3,160,000 → 3,200,000            [tier A, ev=1.00]
## 숭실대학교 — BA (withdrawn)
- department "기계공학과" → withdrawn (absent_from_guide_2027)
```

Every change line carries its provenance pointer so a human can jump to the source in one click.

### 7.4 Trace a wrong number back to its source page

```
value -> field_provenance (current row)
      -> document_id -> guide_document.library_path + source_url + page_ref
      -> attempt_id   -> parse_attempt.{model,tier,score,evidence,raw_response}
      -> run_id       -> parse_run.started_at
```

`page_ref` is captured when the extractor can attribute a value to a page/section (pymupdf page
index during extraction). Even without it, the evidence snippet in `field_provenance.evidence` is
the substring of the source text that was matched — the operator can re-open the PDF and find it.

---

## 8. Observability / SLA (once-a-day job)

### 8.1 Run contract

- One `parse_run` per day, `run_kind='daily'`, `trigger_type='cron'` (04:00 KST after the detector).
- **Success** = `status='succeeded'` **and** `published=true` (a run that parses but fails a gate is
  `aborted`, not silent-success).
- Non-zero exit on `failed`/`aborted`; cron surface (email/Telegram) receives the change report or
  the abort reason.

### 8.2 Alert conditions

| condition                                    | severity |
|----------------------------------------------|----------|
| run failed / aborted / killed                | critical |
| any publish gate failed                      | critical |
| coverage regression > tol                    | critical |
| `review` backlog > threshold (e.g. 20 docs)  | warning  |
| tier-E spike (collector producing web captures) | warning |
| > N consecutive `http_401` attempts in a run | warning  |
| unreadable current-year guide for a school that was previously covered | warning |
| merge wrote 0 fields but had accepted docs (pipeline drift) | warning |

### 8.3 Kill-switch

`pipeline_setting('kill_switch') = true` (or `publish_enabled=false`) halts the run at step 0:
`parse_run.status='killed', killed_by='kill_switch'`, no merge, no publish. Set manually on
regression, or auto-set by the coverage guard on a hard failure. Re-enabling re-runs the same
status queue (idempotent).

### 8.4 Format-contract hygiene

Publish writes JSON with `newline='\n'` (LF) + `indent=1` for `consulting_db`/`verified_kb`, and
minified for `data.js` — then normalizes line endings before diffing, so CRLF can never inflate a
diff again (defect #8).

---

## 9. Daily pipeline pseudocode (driver)

```python
def daily_pipeline():
    cfg = load_settings()                    # current_guide_year='2027', model_map, gates, tol
    if cfg.kill_switch or not cfg.publish_enabled:
        run = new_run('daily', status='killed', killed_by='kill_switch'); alert(run); return

    run = new_run('daily', target_year=cfg.current_guide_year)

    # 0. cheap library refresh + validate (no full rehash)
    guide_library('--refresh'); guide_library('--validate')

    # 1. ingest: detect new/changed -> guide_document rows (dedupe on content_hash)
    ingest_documents(run)                    # detected->fetched->identified->tiered (doc_tier.classify)

    # 2. parse (resumable; 401-aware)
    for doc in queue(status='tiered'):
        if not needs_parse(doc, last_attempt(doc)): continue
        parse_document(doc, run)             # -> parsed (strict JSON + evidence) -> verified (score)

    # 3. merge in one transaction, gated
    try:
        with txn():
            for doc in accepted_docs(run):
                merge_into_program(doc, run)     # §5.4 year gate; writes provenance + change
            gate_result = run_publish_gates(run) # §6.3
            if not gate_result.ok: raise Abort(gate_result)
    except Abort:
        run.status='aborted'; run.publish_gate=gate_result; alert(run); return

    # 4. publish read models (atomic; fill-only for consulting_db; Supabase upsert last)
    publish(run)                             # program_current -> consulting_db -> data.js -> Supabase
    coverage_guard()                         # post-publish regression re-check

    # 5. report + notify
    run.status='succeeded'; run.published=True
    emit_change_report(run)                  # §7.3 markdown
    notify(run)
```

`merge_into_program` (the year-gated write):

```python
def merge_into_program(doc, run):
    prog = upsert program(school_id, level, guide_year=doc.guide_year)   # version unit
    C = settings.current_guide_year
    for field, val in doc.extracted_fields.items():
        if val is None: continue
        if field in ('topik_req','ielts_req','toefl_req') and doc.level=='lang':
            continue                                   # invariant, structural
        prev = field_provenance.latest(prog, field)
        if doc.guide_year > C:
            abort("future cycle before flag flip")      # config error
        if doc.guide_year == C or prev is None:         # overwrite or fill-gap
            if prev is not None and prev.value == val:
                continue                                 # no-op (idempotent)
            write_value(prog, field, val, doc, run)      # + field_provenance(supersede) + field_change
```

---

## 10. Open questions

1. **Page/section attribution** — today's extractor returns flat fields. Capturing `page_ref`
   requires page-aware prompting (pymupdf per-page text). Worth it for the "trace to source page"
   requirement, or is document-level + evidence snippet enough for the operator?
2. **`rejected_nondoc` re-collection** — is re-collection automated (re-run the renderer /
   re-fetch the page) or a human queue? The loop is drawn as automated; confirm ownership.
3. **Same-year revision frequency** — if a school re-publishes its 2027 PDF mid-cycle several times,
   should each md5 be a new `field_change` event (current design) or only when a *value* changes?
   (Design: only value changes produce `field_change`; md5 alone updates `content_hash`.)
4. **Threshold constants** — `coverage_tol` (currently 0.10), `max_recollect_attempts`,
   review-backlog alert threshold. Proposed defaults vs operator preference?
5. **Supabase vs files as system-of-record** — this design makes Postgres authoritative and the
   JSON stores derived. Confirm the file stores (verified_kb.json etc.) are allowed to become
   one-way projections, or must they remain the golden source for external consumers?
6. **Retention** — how long to keep `parse_attempt.raw_response` and superseded `field_provenance`
   rows (audit value vs storage on the free/pro Supabase tier)?
7. **Escalate ceiling** — pro-model re-parse for escalate/review is capped at N attempts; what is N
   before a doc is permanently parked in `review`?
