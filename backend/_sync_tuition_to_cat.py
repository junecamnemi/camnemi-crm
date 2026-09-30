#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync tuition_by_department.json → cat.tuition (typed SOT), all levels.

Convention (matches the existing Phase-1 loader sync_kb_to_postgres.py):
  scope='college', tier='semester', unit='per_semester', college name in `note`,
  source_doc_id = the current program's source guide document.

Level mapping: BA→ba, MA→ma, 전문학사→junior. Idempotent: for each (school, level)
program we clear its cat.tuition children and re-insert from the source rows, so a
re-run never duplicates. Rows with krw<=0 or the '(미분류)' sentinel are dropped.

Uses psycopg2 (postgres role) — the anon REST key has no UPDATE on base tables.
"""
import json, os, re, sys
import psycopg2

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'tuition_by_department.json')
ENV = os.path.join(BASE, '..', '.env')

LEVEL_MAP = {'BA': 'ba', 'MA': 'ma', '전문학사': 'junior'}
ALIAS = {'포스텍': '포항공과대학교', '한국해양대학교': '국립한국해양대학교',
         '한국교통대학교': '국립한국교통대학교', '부경대학교': '국립부경대학교',
         '창원대학교': '국립창원대학교', '용인송담대학교': '용인예술과학대학교'}

def norm(s):
    return re.sub(r'[^가-힣A-Za-z0-9]', '', str(s or ''))

def get_pw():
    return re.search(r'SUPABASE_DB_PASSWORD\s*=\s*(\S+)',
                     open(ENV, encoding='utf-8', errors='ignore').read()).group(1)

def build_name_index(school_rows):
    """-> {normalized_name: (id, name_kr)} plus short-name folding."""
    idx = {}
    for sid, nk in school_rows:
        idx[norm(nk)] = (sid, nk)
        # full name also keyed by itself
        idx[nk] = (sid, nk)
    # short→full folding: 국민대 → 국민대학교
    for sid, nk in school_rows:
        if nk.endswith('학교') and nk[:-2] not in idx:
            idx[nk[:-2]] = (sid, nk)
    return idx

def resolve(name, idx, aliases):
    if name in aliases:
        name = aliases[name]
    t = norm(name)
    if t in idx:
        return idx[t]
    if name in idx:
        return idx[name]
    # prefix fallback for short names
    if len(t) >= 3:
        for key, (sid, nk) in idx.items():
            if key and (t in key or key in t):
                return (sid, nk)
    return None

def main():
    data = json.load(open(SRC, encoding='utf-8'))
    schools = data['schools']
    pw = get_pw()
    conn = psycopg2.connect(host='aws-0-ap-northeast-2.pooler.supabase.com', port=5432,
                            dbname='postgres', user='postgres.zjdvzpylxazfbazioxto',
                            password=pw, connect_timeout=20)
    cur = conn.cursor()
    cur.execute("select id, name_kr from cat.school")
    school_rows = cur.fetchall()
    name_idx = build_name_index(school_rows)
    cur.execute("select id, school_id, level, source_doc_id from cat.program where is_current")
    progs = cur.fetchall()
    # (school_id, level) -> (program_id, source_doc_id)
    prog_map = {(sid, lv): (pid, doc) for pid, sid, lv, doc in progs}

    inserts = []   # (program_id, amount_krw, note)
    skipped_school = []
    skipped_prog = []
    n_rows = 0
    for name, lv in schools.items():
        if not isinstance(lv, dict):
            continue
        for key, cat_lv in LEVEL_MAP.items():
            blk = lv.get(key)
            if not isinstance(blk, dict):
                continue
            rows = blk.get('rows') or []
            sid = resolve(name, name_idx, ALIAS)
            if not sid:
                skipped_school.append(name); continue
            pid = prog_map.get((sid[0], cat_lv))
            if not pid:
                skipped_prog.append(f"{name}:{cat_lv}"); continue
            program_id, doc_id = pid
            for r in rows:
                if not isinstance(r, dict):
                    continue
                c = (r.get('college') or '').strip()
                krw = r.get('krw')
                if not c or c == '(미분류)' or not isinstance(krw, (int, float)) or krw <= 0:
                    continue
                inserts.append((program_id, int(krw), c[:300], doc_id))
                n_rows += 1

    # idempotent write: clear then insert per affected program
    prog_ids = sorted({i[0] for i in inserts})
    cur.execute("delete from cat.tuition where program_id::text = any(%s)", (prog_ids,))
    cleared = cur.rowcount
    for program_id, amt, note, doc_id in inserts:
        cur.execute(
            "insert into cat.tuition (program_id,scope,tier,unit,amount_krw,note,source_doc_id) "
            "values (%s,'college','semester','per_semester',%s,%s,%s)",
            (program_id, amt, note, doc_id))
    conn.commit()

    # read-back verification
    cur.execute("select count(*) from cat.tuition")
    total = cur.fetchone()[0]
    cur.execute("select p.level, count(*) from cat.tuition t join cat.program p on p.id=t.program_id "
                "where p.is_current group by p.level order by p.level")
    by_level = cur.fetchall()
    conn.close()

    print(f"tuition rows written={n_rows} (programs touched={len(prog_ids)}, cleared={cleared})")
    print(f"skipped school (no cat.school match): {len(skipped_school)} {skipped_school[:10]}")
    print(f"skipped program (no current program): {len(skipped_prog)} {skipped_prog[:10]}")
    print(f"read-back cat.tuition total={total}")
    for lv, n in by_level:
        print(f"  current {lv}: {n} rows")

if __name__ == '__main__':
    main()
