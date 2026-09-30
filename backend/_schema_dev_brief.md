# DEV brief — Camnemi university-guide database redesign

## Who we are
Camnemi = study-in-Korea agency (Cambodian/international students). We maintain a database of
Korean universities' **admission guides (모집요강)** for the **foreigner track only**
(재외국민 특별전형 excluded). Deliverables that consume this DB: student advising/consulting
reports, an agency CRM (171 students), several Cloudflare Workers web apps
(registeramc / apply / game / medical / topik), printed PDFs, and card-news content.

## The requirement (verbatim from the operator)
- The school DB is used for **analysis and web services**, refreshed **once per day**.
- The **school list is already curated** (no discovery problem — ~318 schools + 126 junior colleges).
- Design how a school guide (모집요강) that gets updated should be modelled in the DB.
- **AI/semantic search is OUT OF SCOPE** — that gets built separately. Do not design for it.
- Daily update = new guide PDF arrives for a school × level → parses → DB reflects it.

## What exists today (real, measured — not aspirational)

### 1. Guide PDF library (source of truth for documents)
`G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides\{ba|ma|junior|lang}\{2026|2027}\`
1,308 PDFs; current cycle = ba/2027 161, ma/2027 12, junior/2027 52, lang/2027 72, lang/2026 32.
Manifest with md5 per file: `guides/_library_manifest.json`.

### 2. verified_kb.json — curated KB (the current "golden" store)
Sections: `schools` (164 BA), `master.schools` (148), `junior.schools` (126),
`lang_programs.schools` (194), plus `visa_restricted_2026`, `medical_reqs`, `ai_departments`,
`free_major_programs`, `guide` (school → reference link + status).
Per-school fields (BA example): name, region, rank, type, topik_req, ielts_req, lang_req, period,
tuition_min/max/tuition_semester, `tuition_semester_by_dept` (field→KRW map),
`colleges[].departments[]{major, korean_track, english_track, topik, ielts}`,
`majors_full`, `scholarships_categorized[]{name, condition|criteria, benefit, type(enroll|existing),
category(academic|language|both|general)}`, `scholarship_curated`, `scholarships{enroll[],existing[]}`,
`fee_structure{app_fee, admission_fee}`, `apply_system`, `ieqas_certified/level/course/year`,
`student_count`, `guide_year`, `guide_effective_year`, `_llm_parsed{field: provenance}`.

### 3. canonical/schools.jsonl — 318 records, "single source of truth" attempt
```json
{"school":"전북대학교","aliases":["전북대","JBNU"],
 "meta":{"students":23561,"type":"국립","loc":"전북 전주","logo":"logos/x.png"},
 "programs":{"ba":{"period":"...","req":{"topik":2,"ielts":5.5,"toefl":71},
   "track_policy":"per_department",
   "colleges":[{"college":"공과대학","tuition_krw":2704000,
     "departments":[{"major":"기계공학과","korean_track":true,"english_track":false,"topik":2,"ielts":null}]}],
   "scholarships":[{"name":"성적우수","criteria":"...","award":"..."}],
   "tuition_note":"...","track_note":"...","lang":{"per_term":"","total_hours":"","dorm":false,"d4_eligible":true}}},
 "sources":{"guide_pdf":["..."],"academyinfo":{"schlId":"0000025"},"kb":"verified_kb:전북대학교"},
 "validation":{"schema_ok":true,"coverage":{},"conflicts":[],"checked_at":"..."}}
```
Measured program-level field presence: ba 179 programs (req on 162), ma 141 (132), junior 127,
lang 158 (129 have a `req` — **wrong**, see invariant below).

### 4. consulting_db.json — derived, bot-facing (394 schools, levels BA/MA/전문학사/어학연수)
### 5. data.js — derived, GitHub-Pages site (BA 190 / junior 126 / MA tuition 126)
### 6. Supabase (Postgres) — today's schema is a blob, known to be wrong
```sql
create table universities (id text primary key, name_kr text, name_en text, short_en text,
  loc text, type text default 'univ', logo text, students int, rank int,
  tuition jsonb default '{}', req jsonb default '{}', cert jsonb default '{}',
  majors_ba jsonb default '[]', majors_ma jsonb default '[]', extra jsonb default '{}',
  updated_at timestamptz default now());
create table university_guides (univ_id text references universities(id), track text, url text,
  primary key (univ_id, track));
```
Also present: customers (171), agencies, fees, partners, tasks, transactions, recs,
wiki_cats/wiki_notes/wiki_docs, activity_log, app_settings. All tables have anon RLS `using(true)`.
CRM = GitHub Pages static app reading Supabase with the anon key; `data.js` is the offline fallback.

## Invariants and defects the design MUST prevent (all observed in production)
1. **어학연수(lang) has NO language requirement.** TOPIK/IELTS/TOEFL are not admission requirements
   for a Korean-language course. An LLM merge once attached requirements to 6 lang schools.
   → must be enforced structurally, not by convention.
2. **Per-department tuition exists** (e.g. 간호 3,703,750 / 인문 3,160,000 / 예술 3,824,000 KRW per
   semester) and also "first semester vs later semesters" tiers. Prose-only tuition
   (`"인문 ₩4,253,000 / 이학체육 ₩5,076,000"`) broke every numeric consumer.
3. **Two tracks per department** — `korean_track` / `english_track` booleans with per-track
   `topik`/`ielts`. Advising queries ("show me English-track majors for IELTS 5.5") must be a
   plain indexed query, not a script that scrapes JSON shapes.
4. **Scholarship is two axes**: `type` = enroll(입학, first semester) vs existing(재학, ongoing);
   `category` = academic / language / both / general. Conditions are TOPIK or IELTS or GPA tiered,
   and benefit can be a percentage, an amount, an admission-fee waiver, or a dorm fee.
5. **Guide year ≠ label.** 17+ schools labelled 2027 in their filenames were really 2026학년도.
   YoY breakage: a 2026 value must never overwrite a 2027 value; a newer guide may.
6. **Provenance is mandatory.** Every value needs to be traceable to (PDF, page/section, parse run,
   model, tier, evidence score). Users have repeatedly caught wrong tuition/scholarship numbers
   and demand verification against the actual guide.
7. **Derived stores are fill-only.** A full rebuild of a derived store wiped enrichment fields;
   ~80% of a past "missing data" incident was sync/build defects, not missing sources.
8. **Format contracts matter**: verified_kb/consulting_db = indent=1 + LF; data.js = minified.
   CRLF once inflated a diff to ~100k lines.
9. **Parsing quality depends on the source document, not the model.** Tier router:
   A ≥5,000 chars text, B 1,000–5,000, C 200–1,000 (OCR), D <200 (OCR), E non-document
   (web screenshot → reject and re-collect). Hallucinated `period` values came from 300–700 char
   PDFs. Currently: 329 current-cycle PDFs, 243 parsed, 86 pending.
10. **Non-PDF sources exist**: some guides are only web pages / HWP files → collected as rendered
    PDFs; the DB must record the source kind (pdf | page-render | hwp-converted) and the URL.

## What to design (deliverables)
A senior data/backend architect's proposal that a small team can implement:
1. **PostgreSQL DDL** for the guide/admission domain: schools, programs (school × level × guide
   year), requirements, colleges/departments, per-department tuition, tuition tiers, scholarships
   (with their two axes), fees, application periods (possibly multiple rounds per program),
   guide sources & parse provenance, and curated lists (visa-restricted, medical, free-major).
2. **Temporal / versioning strategy** for daily refreshes: how today's guide coexists with last
   year's, how to diff "what changed today", and how to answer "which guide was current on date X".
3. **Daily pipeline contract**: what the ETL writes, upsert keys, idempotency, soft-delete/retire
   of stale programs, rollback, and the audit trail. Assume ~330 current-cycle documents and 1,308
   total, one run per day.
4. **Serving layer**: how web apps (Supabase anon + RLS) and analytics/reporting read it —
   views/materialized views, indexes, denormalised read models, caching, and what should NOT live
   in Postgres.
5. **Migration plan** from the existing jsonb `universities` blob (no downtime, keep the live site
   working) and how `verified_kb.json` / `consulting_db.json` / `data.js` relate to Postgres
   going forward (publish direction must be one-way).
6. **Explicitly reject** anything that doesn't pay for itself — no entity/attribute-value soup, no
   EAV, no JSONB-for-everything. Justify JSONB only where the shape is genuinely open-ended.

Constraints: small team (1–2 devs), Postgres via Supabase (free/pro tier), Windows dev machine,
no AI/semantic-search features in this design, must survive duplicate/partial guide availability,
and the operator is intolerant of silently-wrong numbers — correctness and auditability beat
elegance.