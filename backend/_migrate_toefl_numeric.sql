begin;
drop view if exists public.universities;
drop view if exists public.v_deadline;
drop view if exists public.v_major;
drop view if exists public.v_program_current;
drop view if exists public.v_provenance;
drop view if exists public.v_scholarship_tier;
alter table cat.program alter column toefl_req type numeric(4,1) using toefl_req::numeric(4,1);
create view public.v_program_current as SELECT id, school_id, level, guide_year, effective_year, effective_from, effective_to, period_text,
    topik_req, ielts_req, toefl_req, lang_req_text, track_policy, tuition_min, tuition_max, tuition_note,
    apply_system, apply_system_all, app_fee_krw, admission_fee_krw, lang_per_term, lang_total_hours, lang_dorm,
    lang_d4_eligible, ieqas_certified, ieqas_level, ieqas_course, ieqas_year, student_count, foreign_students,
    note, status, is_current, source_doc_id, parse_run_id, asserted_by, evidence, created_at, updated_at,
    toefl_scale, scholarship_note
   FROM cat.program WHERE status = 'active'::cat.program_status AND is_current;
comment on view public.v_program_current is 'Current active program per school+level. toefl_scale must be read together with toefl_req: ibt = 0-120, new_2026 = the 2026 1-6 scale.';
create view public.v_deadline as SELECT s.id AS school_id, s.name_kr, s.name_en, s.loc, p.level, p.guide_year, r.round_label, r.kind,
    r.starts_on, r.ends_on, r.ends_on - CURRENT_DATE AS days_left, r.period_text, p.source_doc_id
   FROM cat.school s
     JOIN cat.program p ON p.school_id = s.id AND p.is_current
     JOIN cat.application_round r ON r.program_id = p.id
  WHERE r.ends_on IS NOT NULL;
create view public.v_major as SELECT s.id AS school_id, s.name_kr, s.name_en, s.loc, s.region, s.type, s.rank, p.level, p.guide_year,
    p.is_current, c.name AS college, d.id AS department_id, d.name AS major, d.name_en AS major_en,
    d.korean_track, d.english_track, d.korean_topik, d.korean_ielts, d.english_topik, d.english_ielts,
    COALESCE(tu.amount_krw, p.tuition_min) AS tuition_krw, p.source_doc_id, p.evidence
   FROM cat.school s
     JOIN cat.program p ON p.school_id = s.id AND p.is_current
     LEFT JOIN cat.college c ON c.program_id = p.id
     JOIN cat.department d ON d.program_id = p.id AND (c.id IS NULL OR d.college_id = c.id)
     LEFT JOIN cat.tuition tu ON tu.department_id = d.id AND tu.scope = 'department'
  WHERE d.status = 'active';
create view public.v_provenance as SELECT s.id AS school_id, s.name_kr, p.level, p.guide_year, p.effective_year, gd.path AS source_pdf,
    gd.kind AS source_kind, gd.md5, gd.tier, pr.id AS parse_run_id, pr.finished_at AS parsed_at,
    fp.field, fp.value, fp.evidence_score, fp.page_ref, fp.asserted_by
   FROM cat.school s
     JOIN cat.program p ON p.school_id = s.id
     JOIN cat.guide_document gd ON gd.id = p.source_doc_id
     LEFT JOIN cat.parse_run pr ON pr.id = p.parse_run_id
     LEFT JOIN cat.field_provenance fp ON fp.program_id = p.id AND fp.superseded_at IS NULL
  WHERE p.is_current;
create view public.v_scholarship_tier as SELECT s.id AS school_id, s.name_kr, p.level, p.guide_year, sch.id AS scholarship_id,
    sch.name AS scholarship_name, sch.type, sch.category, t.condition_type, t.condition_min, t.condition_text,
    t.benefit_type, t.benefit_value, t.benefit_text, t.sort_order
   FROM cat.school s
     JOIN cat.program p ON p.school_id = s.id AND p.is_current
     JOIN cat.scholarship sch ON sch.program_id = p.id
     JOIN cat.scholarship_tier t ON t.scholarship_id = sch.id;
create view public.universities as WITH cur AS (
         SELECT p.id AS program_id, p.school_id, p.level, p.topik_req, p.ielts_req, p.toefl_req,
            p.toefl_scale, p.tuition_min, p.tuition_max, p.track_policy, p.req_verified
           FROM cat.program p WHERE p.is_current AND p.status = 'active'::cat.program_status
        ), ba AS (SELECT * FROM cur WHERE level = 'ba'::cat.level_t),
           ma AS (SELECT * FROM cur WHERE level = 'ma'::cat.level_t),
        maj AS (SELECT d.program_id, jsonb_agg(jsonb_build_object('kr', d.name, 'en', COALESCE(d.name_en, '')) ORDER BY d.sort_order, d.name) AS arr
           FROM cat.department d GROUP BY d.program_id),
        sch AS (SELECT sc.program_id, jsonb_agg(jsonb_build_object('name', sc.name, 'condition', COALESCE(sc.note, ''), 'benefit', COALESCE(sc.type, '')) ORDER BY sc.name) AS arr
           FROM cat.scholarship sc GROUP BY sc.program_id),
        tu AS (SELECT tuition.program_id, min(tuition.amount_krw) AS lo, max(tuition.amount_krw) AS hi
           FROM cat.tuition WHERE tuition.amount_krw IS NOT NULL GROUP BY tuition.program_id)
 SELECT COALESCE(b.id, s.name_kr) AS id,
    COALESCE(s.name_kr, b.name_kr) AS name_kr, COALESCE(s.name_en, b.name_en) AS name_en,
    COALESCE(s.short_en, b.short_en) AS short_en, COALESCE(s.loc, b.loc) AS loc,
    COALESCE(s.type, b.type) AS type, COALESCE(s.logo, b.logo) AS logo,
    COALESCE(s.students, b.students) AS students, COALESCE(s.rank, b.rank) AS rank,
    jsonb_build_object('ba', jsonb_build_object('min', COALESCE(ba.tuition_min, tu_ba.lo, NULLIF((b.tuition -> 'ba') ->> 'min', '')::numeric), 'max', COALESCE(ba.tuition_max, tu_ba.hi, NULLIF((b.tuition -> 'ba') ->> 'max', '')::numeric), 'fields', COALESCE((b.tuition -> 'ba') -> 'fields', '{}'::jsonb)), 'ma', jsonb_build_object('min', COALESCE(ma.tuition_min, tu_ma.lo, NULLIF((b.tuition -> 'ma') ->> 'min', '')::numeric), 'max', COALESCE(ma.tuition_max, tu_ma.hi, NULLIF((b.tuition -> 'ma') ->> 'max', '')::numeric), 'fields', COALESCE((b.tuition -> 'ma') -> 'fields', '{}'::jsonb))) AS tuition,
    jsonb_build_object('topik', COALESCE(ba.topik_req, b.t), 'ielts', COALESCE(ba.ielts_req, b.i), 'toefl', ba.toefl_req, 'toefl_scale', ba.toefl_scale, 'verified', ba.req_verified, 'kiip', b.req ->> 'kiip', 'sejong', b.req ->> 'sejong', 'selftest', COALESCE(b.req ->> 'selftest', 'false'), 'english', COALESCE(b.req ->> 'english', 'false')) AS req,
    b.cert, COALESCE(maj_ba.arr, b.majors_ba) AS majors_ba, COALESCE(maj_ma.arr, b.majors_ma) AS majors_ma, b.extra,
    GREATEST(COALESCE(s.updated_at, now()), COALESCE(b.updated_at, now())) AS updated_at,
    COALESCE(sch_ba.arr, b.scholarships) AS scholarships, b.req_note, b.website,
    COALESCE(ba.topik_req, b.t) AS t, COALESCE(ba.ielts_req, b.i)::numeric(4,1) AS i,
    COALESCE(b.eng, CASE WHEN ba.track_policy ~~* '%english%' THEN 'y' ELSE b.eng END) AS eng,
    b.documents, b.country_notes, b.programs
   FROM cat.school s
     FULL JOIN universities_blob b ON b.name_kr = s.name_kr
     LEFT JOIN ba ON ba.school_id = s.id
     LEFT JOIN ma ON ma.school_id = s.id
     LEFT JOIN tu tu_ba ON tu_ba.program_id = ba.program_id
     LEFT JOIN tu tu_ma ON tu_ma.program_id = ma.program_id
     LEFT JOIN maj maj_ba ON maj_ba.program_id = ba.program_id
     LEFT JOIN maj maj_ma ON maj_ma.program_id = ma.program_id
     LEFT JOIN sch sch_ba ON sch_ba.program_id = ba.program_id;
grant select on public.universities to anon, authenticated;
commit;