-- generated 2026-10-06T15:33:56 by _migrate_loc_detail.py
create or replace view public.universities as
 WITH cur AS (
         SELECT p.id AS program_id,
            p.school_id,
            p.level,
            p.topik_req,
            p.ielts_req,
            p.toefl_req,
            p.toefl_scale,
            p.tuition_min,
            p.tuition_max,
            p.track_policy,
            p.req_verified
           FROM cat.program p
          WHERE (p.is_current AND (p.status = 'active'::cat.program_status))
        ), ba AS (
         SELECT cur.program_id,
            cur.school_id,
            cur.level,
            cur.topik_req,
            cur.ielts_req,
            cur.toefl_req,
            cur.toefl_scale,
            cur.tuition_min,
            cur.tuition_max,
            cur.track_policy,
            cur.req_verified
           FROM cur
          WHERE (cur.level = 'ba'::cat.level_t)
        ), ma AS (
         SELECT cur.program_id,
            cur.school_id,
            cur.level,
            cur.topik_req,
            cur.ielts_req,
            cur.toefl_req,
            cur.toefl_scale,
            cur.tuition_min,
            cur.tuition_max,
            cur.track_policy,
            cur.req_verified
           FROM cur
          WHERE (cur.level = 'ma'::cat.level_t)
        ), maj AS (
         SELECT d.program_id,
            jsonb_agg(jsonb_build_object('kr', d.name, 'en', COALESCE(d.name_en, ''::text)) ORDER BY d.sort_order, d.name) AS arr
           FROM cat.department d
          GROUP BY d.program_id
        ), sch AS (
         SELECT sc.program_id,
            jsonb_agg(jsonb_build_object('name', sc.name, 'condition', COALESCE(sc.note, ''::text), 'benefit', COALESCE(sc.type, ''::text)) ORDER BY sc.name) AS arr
           FROM cat.scholarship sc
          GROUP BY sc.program_id
        ), tu AS (
         SELECT tuition.program_id,
            min(tuition.amount_krw) AS lo,
            max(tuition.amount_krw) AS hi
           FROM cat.tuition
          WHERE (tuition.amount_krw IS NOT NULL)
          GROUP BY tuition.program_id
        )
 SELECT COALESCE(b.id, s.name_kr) AS id,
    COALESCE(s.name_kr, b.name_kr) AS name_kr,
    COALESCE(s.name_en, b.name_en) AS name_en,
    COALESCE(s.short_en, b.short_en) AS short_en,
    COALESCE(s.loc, b.loc) AS loc,
    COALESCE(s.type, b.type) AS type,
    COALESCE(s.logo, b.logo) AS logo,
    COALESCE(s.students, b.students) AS students,
    COALESCE(s.rank, b.rank) AS rank,
    jsonb_build_object('ba', jsonb_build_object('min', COALESCE(ba.tuition_min, tu_ba.lo, (NULLIF(((b.tuition -> 'ba'::text) ->> 'min'::text), ''::text))::numeric), 'max', COALESCE(ba.tuition_max, tu_ba.hi, (NULLIF(((b.tuition -> 'ba'::text) ->> 'max'::text), ''::text))::numeric), 'fields', COALESCE(((b.tuition -> 'ba'::text) -> 'fields'::text), '{}'::jsonb)), 'ma', jsonb_build_object('min', COALESCE(ma.tuition_min, tu_ma.lo, (NULLIF(((b.tuition -> 'ma'::text) ->> 'min'::text), ''::text))::numeric), 'max', COALESCE(ma.tuition_max, tu_ma.hi, (NULLIF(((b.tuition -> 'ma'::text) ->> 'max'::text), ''::text))::numeric), 'fields', COALESCE(((b.tuition -> 'ma'::text) -> 'fields'::text), '{}'::jsonb))) AS tuition,
    jsonb_build_object('topik', COALESCE(ba.topik_req, b.t), 'ielts', COALESCE(ba.ielts_req, b.i), 'toefl', ba.toefl_req, 'toefl_scale', ba.toefl_scale, 'verified', ba.req_verified, 'kiip', (b.req ->> 'kiip'::text), 'sejong', (b.req ->> 'sejong'::text), 'selftest', COALESCE((b.req ->> 'selftest'::text), 'false'::text), 'english', COALESCE((b.req ->> 'english'::text), 'false'::text)) AS req,
    b.cert,
    COALESCE(maj_ba.arr, b.majors_ba) AS majors_ba,
    COALESCE(maj_ma.arr, b.majors_ma) AS majors_ma,
    b.extra,
    GREATEST(COALESCE(s.updated_at, now()), COALESCE(b.updated_at, now())) AS updated_at,
    COALESCE(sch_ba.arr, b.scholarships) AS scholarships,
    b.req_note,
    b.website,
    COALESCE(ba.topik_req, b.t) AS t,
    (COALESCE(ba.ielts_req, b.i))::numeric(4,1) AS i,
    COALESCE(b.eng,
        CASE
            WHEN (ba.track_policy ~~* '%english%'::text) THEN 'y'::text
            ELSE b.eng
        END) AS eng,
    b.documents,
    b.country_notes,
    b.programs,
    COALESCE(s.loc_detail, b.loc_detail) AS loc_detail
   FROM ((((((((cat.school s
     FULL JOIN universities_blob b ON ((b.name_kr = s.name_kr)))
     LEFT JOIN ba ON ((ba.school_id = s.id)))
     LEFT JOIN ma ON ((ma.school_id = s.id)))
     LEFT JOIN tu tu_ba ON ((tu_ba.program_id = ba.program_id)))
     LEFT JOIN tu tu_ma ON ((tu_ma.program_id = ma.program_id)))
     LEFT JOIN maj maj_ba ON ((maj_ba.program_id = ba.program_id)))
     LEFT JOIN maj maj_ma ON ((maj_ma.program_id = ma.program_id)))
     LEFT JOIN sch sch_ba ON ((sch_ba.program_id = ba.program_id)));
