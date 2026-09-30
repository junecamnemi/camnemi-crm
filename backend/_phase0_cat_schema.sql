create extension if not exists pgcrypto;
create schema if not exists cat;

-- ---------- enums ----------
create type cat.doc_tier          as enum ('A','B','C','D','E');           -- E = non-document
create type cat.doc_status        as enum ('detected','fetched','identified','tiered','parsed',
                                           'verified','merged','published','review',
                                           'rejected_duplicate','retired_stale','unreadable',
                                           'rejected_nondoc');
create type cat.guide_source_kind as enum ('pdf','page-render','hwp-converted','screenshot');
create type cat.run_status        as enum ('running','ok','failed','aborted');
create type cat.parse_verdict     as enum ('accept','escalate','review','reject');
create type cat.program_status    as enum ('draft','active','stale','withdrawn');
create type cat.level_t           as enum ('ba','ma','junior','lang');

-- ---------- curated schools (not versioned) ----------
create table cat.school (
  id text primary key,                                   -- slug = canonical Korean name
  name_kr text not null unique,
  name_en text, short_en text,
  region text, loc text,
  category text not null default 'university'
    check (category in ('university','junior_college','graduate','language')),
  type text,                                             -- 국립 | 사립 | …
  logo text, photo text,
  students int, foreign_students int, rank int,
  ieqas_certified boolean, ieqas_level text, ieqas_year smallint,
  academyinfo_id text,
  excluded boolean not null default false, exclude_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table cat.school_alias (
  school_id text not null references cat.school(id) on delete cascade,
  alias text not null,
  kind text not null default 'short' check (kind in ('short','english','hanja','misspell')),
  primary key (school_id, alias)
);
create index school_alias_lookup_idx on cat.school_alias (alias);

-- ---------- the physical source document (G: library / collected page) ----------
create table cat.guide_document (
  id uuid primary key default gen_random_uuid(),
  md5 char(32) not null unique,                          -- content hash: the dedupe key
  path text not null unique,
  file_name text,
  level cat.level_t not null,
  label_year smallint,                                   -- from filename/path (UNTRUSTED)
  effective_year smallint,                               -- verified 학년도
  school_id text references cat.school(id) on delete set null,
  kind cat.guide_source_kind not null default 'pdf',
  url text,
  bytes bigint,
  text_chars int,                                        -- extracted text length (tier driver)
  tier cat.doc_tier not null default 'E',
  status cat.doc_status not null default 'detected',
  reject_reason text,
  page_count int,
  collected_at timestamptz, file_mtime bigint,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint src_year_sane check (
    effective_year is null or label_year is null
    or effective_year between label_year - 1 and label_year + 2)
);
create index guide_doc_school_level_idx on cat.guide_document (school_id, level, status);
create index guide_doc_level_year_idx  on cat.guide_document (level, effective_year);

-- ---------- runs & attempts ----------
create table cat.parse_run (
  id uuid primary key default gen_random_uuid(),
  run_kind text not null default 'daily' check (run_kind in ('daily','manual','backfill','reparse')),
  trigger_type text, target_year text,
  started_at timestamptz not null default now(), finished_at timestamptz,
  status cat.run_status not null default 'running',
  input_count int, parsed_count int,
  accept_count int, escalate_count int, review_count int, reject_count int,
  tier_counts jsonb not null default '{}'::jsonb,
  merged_doc_count int, merged_field_count int,
  published boolean not null default false,
  publish_gate jsonb not null default '{}'::jsonb,
  coverage_delta jsonb not null default '{}'::jsonb,
  rollback_to uuid references cat.parse_run(id),
  error text, killed_by text
);

create table cat.parse_attempt (
  id bigint generated always as identity primary key,
  run_id uuid not null references cat.parse_run(id) on delete cascade,
  document_id uuid not null references cat.guide_document(id) on delete cascade,
  attempt_no int not null default 1,
  tier cat.doc_tier, model text, prompt_ver text,
  status text not null,        -- ok|bad_json|empty_response|http_401|http_error|evidence_fail|error
  verdict cat.parse_verdict, score numeric(5,3),
  evidence jsonb,              -- {field: {hit, snippet}}
  raw_response text,           -- truncated model output (audit)
  usage jsonb not null default '{}'::jsonb,
  started_at timestamptz not null default now(), finished_at timestamptz, error text
);
create index pa_run_idx on cat.parse_attempt (run_id);
create index pa_doc_idx on cat.parse_attempt (document_id, attempt_no desc);

-- ---------- program = school × level × guide_year (VERSION UNIT) ----------
create table cat.program (
  id uuid primary key default gen_random_uuid(),
  school_id text not null references cat.school(id) on delete cascade,
  level cat.level_t not null,
  guide_year smallint not null,
  effective_year smallint,                              -- verified 학년도 of the driving document
  effective_from date, effective_to date,               -- window when this guide was "current"
  period_text text,
  topik_req int, ielts_req numeric(4,1), toefl_req int,
  lang_req_text text,
  track_policy text not null default 'per_department'
    check (track_policy in ('per_department','unified','none')),
  tuition_min numeric(12,0), tuition_max numeric(12,0), tuition_note text,
  apply_system text, apply_system_all text,
  app_fee_krw numeric(10,0), admission_fee_krw numeric(10,0),
  lang_per_term text, lang_total_hours text, lang_dorm boolean, lang_d4_eligible boolean,
  ieqas_certified boolean, ieqas_level text, ieqas_course text, ieqas_year smallint,
  student_count int, foreign_students int, note text,
  status cat.program_status not null default 'draft',
  is_current boolean not null default false,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id),
  asserted_by text, evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (school_id, level, guide_year),
  -- D9: a Korean-language course has NO language requirement
  constraint program_lang_no_req check (
    level <> 'lang' or (topik_req is null and ielts_req is null and toefl_req is null
                        and lang_req_text is null))
);
create index program_level_year_idx on cat.program (level, guide_year);
create index program_school_cur_idx on cat.program (school_id, is_current, level);

-- ---------- colleges / departments ----------
create table cat.college (
  id uuid primary key default gen_random_uuid(),
  program_id uuid not null references cat.program(id) on delete cascade,
  name text not null, tuition_note text, sort_order int not null default 0,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (program_id, name)
);
create index college_program_idx on cat.college (program_id);
create index college_name_idx on cat.college (name);

create table cat.department (
  id uuid primary key default gen_random_uuid(),
  program_id uuid not null references cat.program(id) on delete cascade,
  college_id uuid references cat.college(id) on delete set null,
  name text not null, name_en text,
  korean_track boolean not null default false,
  english_track boolean not null default false,
  korean_topik int, korean_ielts numeric(4,1), korean_toefl int,
  english_topik int, english_ielts numeric(4,1), english_toefl int,
  track_req_text text,
  is_free_major boolean not null default false, is_ai boolean not null default false,
  status text not null default 'active' check (status in ('active','withdrawn')),
  sort_order int not null default 0,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (program_id, college_id, name)
);
create index department_program_idx on cat.department (program_id);
create index department_college_idx on cat.department (college_id) where college_id is not null;
create index dept_english_ielts_idx on cat.department (english_ielts) where english_track;   -- advising query
create index dept_korean_topik_idx  on cat.department (korean_topik)  where korean_track;
create index department_free_idx    on cat.department (program_id) where is_free_major;

-- ---------- tuition (typed rows; never prose) ----------
create table cat.tuition (
  id uuid primary key default gen_random_uuid(),
  program_id uuid not null references cat.program(id) on delete cascade,
  college_id uuid references cat.college(id) on delete cascade,
  department_id uuid references cat.department(id) on delete cascade,
  scope text not null default 'program' check (scope in ('program','college','department')),
  tier text not null default 'semester'
    check (tier in ('first_semester','later_semester','semester','per_credit','annual','other')),
  unit text not null default 'per_semester'
    check (unit in ('per_semester','per_credit','per_year','per_term')),
  amount_krw numeric(12,0) not null check (amount_krw >= 0 and amount_krw <= 20000000),
  note text, sort_order int not null default 0,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index tuition_program_idx on cat.tuition (program_id);
create index tuition_program_dept_idx on cat.tuition (program_id, department_id);

-- ---------- application rounds ----------
create table cat.application_round (
  id uuid primary key default gen_random_uuid(),
  program_id uuid not null references cat.program(id) on delete cascade,
  round_label text,                                     -- 1차 / 수시 / 정시 / 후기
  kind text not null default 'application'
    check (kind in ('application','announcement','registration','interview','other')),
  starts_on date, ends_on date, period_text text, sort_order int not null default 0,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index app_round_program_idx on cat.application_round (program_id);
create index app_round_ends_idx on cat.application_round (ends_on) where ends_on is not null;

-- ---------- scholarships: two axes + tiers ----------
create table cat.scholarship (
  id uuid primary key default gen_random_uuid(),
  program_id uuid not null references cat.program(id) on delete cascade,
  name text not null,
  type text not null check (type in ('enroll','existing')),          -- 입학 | 재학
  category text not null default 'general'
    check (category in ('academic','language','both','general')),
  note text,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index scholarship_program_idx on cat.scholarship (program_id);
create index scholarship_axes_idx on cat.scholarship (type, category);

create table cat.scholarship_tier (
  id uuid primary key default gen_random_uuid(),
  scholarship_id uuid not null references cat.scholarship(id) on delete cascade,
  condition_type text default 'general'
    check (condition_type in ('topik','ielts','toefl','gpa','both','general','none')),
  condition_min numeric, condition_text text,
  benefit_type text not null default 'percent'
    check (benefit_type in ('percent','amount','fee_waiver','dorm','other')),
  benefit_value numeric, benefit_text text, sort_order int not null default 0,
  source_doc_id uuid not null references cat.guide_document(id),
  parse_run_id uuid references cat.parse_run(id), asserted_by text,
  evidence numeric(3,2) not null default 0,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index scholarship_tier_sch_idx on cat.scholarship_tier (scholarship_id);
create index sch_tier_score_idx on cat.scholarship_tier (condition_type, condition_min);

-- ---------- curated lists (visa-restricted, medical, ai, free-major, …) ----------
create table cat.curated_list (
  id text primary key, name text not null,
  source_text text, effective_text text, note text,
  updated_at timestamptz not null default now()
);

create table cat.curated_list_item (
  id uuid primary key default gen_random_uuid(),
  list_id text not null references cat.curated_list(id) on delete cascade,
  school_id text references cat.school(id) on delete cascade,
  program_id uuid references cat.program(id) on delete cascade,
  department_id uuid references cat.department(id) on delete cascade,
  category text, restrict_kind text, flag boolean, note text,
  extra jsonb not null default '{}'::jsonb,             -- JSONB #1 (justified: heterogeneous per list)
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index cli_list_school_idx on cat.curated_list_item (list_id, school_id);

-- ---------- 대학알리미 cross-check snapshot (validation only, never served) ----------
create table cat.academyinfo_ref (
  school_id text not null references cat.school(id) on delete cascade,
  code text not null,                                   -- schlId
  payload jsonb not null,                               -- JSONB #2 (justified: raw upstream payload)
  fetched_at timestamptz not null default now(),
  primary key (school_id, code)
);

-- ---------- provenance: append-only, current row = superseded_at is null ----------
create table cat.field_provenance (
  id bigint generated always as identity primary key,
  program_id uuid not null references cat.program(id) on delete cascade,
  entity_kind text not null,                            -- program|round|college|department|tuition|scholarship|tier
  entity_id uuid,
  field text not null,
  value jsonb not null,
  guide_year text not null,
  document_id uuid references cat.guide_document(id),
  attempt_id bigint references cat.parse_attempt(id),
  run_id uuid references cat.parse_run(id),
  model text, tier cat.doc_tier,
  evidence_score numeric(5,3), evidence jsonb,
  asserted_by text,                                     -- model name or 'manual:<person>'
  source_kind cat.guide_source_kind, source_url text,
  page_ref text,
  written_at timestamptz not null default now(),
  superseded_at timestamptz
);
create index fp_current_idx on cat.field_provenance (program_id, field, superseded_at, written_at desc);
create index fp_entity_idx  on cat.field_provenance (entity_kind, entity_id);
create index fp_run_idx     on cat.field_provenance (run_id);

create table cat.field_change (
  id bigint generated always as identity primary key,
  run_id uuid not null references cat.parse_run(id) on delete cascade,
  program_id uuid not null references cat.program(id) on delete cascade,
  entity_kind text not null, entity_id uuid,
  field text not null, guide_year_from text, guide_year_to text,
  old_value jsonb, new_value jsonb,
  document_id uuid references cat.guide_document(id),
  changed_at timestamptz not null default now()
);
create index fc_run_idx on cat.field_change (run_id);
create index fc_program_idx on cat.field_change (program_id, changed_at desc);

-- ---------- kill-switch / thresholds ----------
create table cat.pipeline_setting (
  key text primary key, value jsonb not null,
  updated_at timestamptz not null default now()
);
-- current_guide_year, kill_switch, coverage_tol, max_recollect_attempts, model_map,
-- alert_webhook, publish_enabled

-- ---------- triggers / helpers ----------
create or replace function cat.set_updated_at() returns trigger as $$
begin new.updated_at := now(); return new; end $$ language plpgsql;

create or replace function cat.enforce_lang_no_req() returns trigger as $$
begin
  if new.level = 'lang' then
    if exists (select 1 from cat.department d where d.program_id = new.id) then
      raise exception 'lang program % cannot own departments', new.id;
    end if;
  end if;
  return new;
end $$ language plpgsql;
-- (attach after-insert/after-update; the CHECK on program covers the scalar case)

do $$ declare t text;
begin
  foreach t in array array['school','guide_document','program','college','department','tuition',
                           'application_round','scholarship','scholarship_tier']
  loop
    execute format('create trigger %I before update on cat.%I for each row execute function cat.set_updated_at()', 'trg_'||t||'_upd', t);
  end loop;
end $$;
commit;


-- current-cycle read model
create view public.v_program_current as
select * from cat.program where status = 'active' and is_current;


-- the advising query, as an index scan (D6)
create or replace view public.v_major as
select s.id as school_id, s.name_kr, s.name_en, s.loc, s.region, s.type, s.rank,
       p.level, p.guide_year, p.is_current,
       c.name as college,
       d.id as department_id, d.name as major, d.name_en as major_en,
       d.korean_track, d.english_track,
       d.korean_topik, d.korean_ielts, d.english_topik, d.english_ielts,
       coalesce(tu.amount_krw, p.tuition_min) as tuition_krw,
       p.source_doc_id, p.evidence
from cat.school s
join cat.program p      on p.school_id = s.id and p.is_current
left join cat.college c on c.program_id = p.id
join cat.department d   on d.program_id = p.id and (c.id is null or d.college_id = c.id)
left join cat.tuition tu on tu.department_id = d.id and tu.scope = 'department'
where d.status = 'active';


create or replace view public.v_deadline as
select s.id as school_id, s.name_kr, s.name_en, s.loc,
       p.level, p.guide_year,
       r.round_label, r.kind, r.starts_on, r.ends_on,
       (r.ends_on - current_date) as days_left, r.period_text,
       p.source_doc_id
from cat.school s
join cat.program p on p.school_id = s.id and p.is_current
join cat.application_round r on r.program_id = p.id
where r.ends_on is not null;

create or replace view public.v_scholarship_tier as
select s.id as school_id, s.name_kr, p.level, p.guide_year,
       sch.id as scholarship_id, sch.name as scholarship_name, sch.type, sch.category,
       t.condition_type, t.condition_min, t.condition_text,
       t.benefit_type, t.benefit_value, t.benefit_text, t.sort_order
from cat.school s
join cat.program p on p.school_id = s.id and p.is_current
join cat.scholarship sch on sch.program_id = p.id
join cat.scholarship_tier t on t.scholarship_id = sch.id;

create or replace view public.v_provenance as
select s.id as school_id, s.name_kr, p.level, p.guide_year, p.effective_year,
       gd.path as source_pdf, gd.kind as source_kind, gd.md5, gd.tier,
       pr.id as parse_run_id, pr.finished_at as parsed_at,
       fp.field, fp.value, fp.evidence_score, fp.page_ref, fp.asserted_by
from cat.school s
join cat.program p on p.school_id = s.id
join cat.guide_document gd on gd.id = p.source_doc_id
left join cat.parse_run pr on pr.id = p.parse_run_id
left join cat.field_provenance fp on fp.program_id = p.id and fp.superseded_at is null
where p.is_current;



