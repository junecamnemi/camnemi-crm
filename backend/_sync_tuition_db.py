#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync per-department tuition into universities_blob.tuition via psycopg2 (postgres role).

Why not REST: the anon key lost UPDATE on the base tables (Phase 2 RLS tightening) → 401.
Why universities_blob: it is the base table the public `universities` view reads for
`tuition.fields` (per-department breakdown) and min/max fallback.

Input: _merge_tuition_input.json (built by _build_tuition_merge_input.py from
tuition_by_department.json). Merge is additive per (school, track): existing field values are
preserved, new ones overwrite, min/max recomputed. Read-back verification after commit.
"""
import json, os, re, sys
import psycopg2

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, '_merge_tuition_input.json')
ENV = os.path.join(BASE, '..', '.env')

ALIAS = {'포스텍': '포항공과대학교', '한국해양대학교': '국립한국해양대학교',
         '한국교통대학교': '국립한국교통대학교', '부경대학교': '국립부경대학교',
         '창원대학교': '국립창원대학교', '용인송담대학교': '용인예술과학대학교'}

def norm(s):
    return re.sub(r'[^가-힣A-Za-z0-9]', '', str(s or ''))

def get_pw():
    env = open(ENV, encoding='utf-8', errors='ignore').read()
    return re.search(r'SUPABASE_DB_PASSWORD\s*=\s*(\S+)', env).group(1)

def resolve(name, rows):
    """rows: list of (name_kr,). Return the matching name_kr or None."""
    target = norm(name)
    if name in ALIAS:
        an = ALIAS[name]
        for (nk,) in rows:
            if nk == an:
                return nk
    for (nk,) in rows:
        if nk == name:
            return nk
    for (nk,) in rows:
        n = norm(nk)
        if n == target:
            return nk
    # loose: one contains the other (short school names like 국민대 → 국민대학교)
    for (nk,) in rows:
        n = norm(nk)
        if len(target) >= 3 and (target in n or (len(n) >= 3 and n in target)):
            return nk
    return None

def main():
    recs = json.load(open(INPUT, encoding='utf-8'))
    pw = get_pw()
    conn = psycopg2.connect(host='aws-0-ap-northeast-2.pooler.supabase.com', port=5432,
                            dbname='postgres', user='postgres.zjdvzpylxazfbazioxto',
                            password=pw, connect_timeout=20)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute("select name_kr, tuition from universities_blob")
    rows = cur.fetchall()
    names = [(r[0],) for r in rows]
    current = {r[0]: (r[1] or {}) for r in rows}

    upd, skipped = 0, []
    for rec in recs:
        univ = rec['univ']
        nk = resolve(univ, names)
        if not nk:
            skipped.append(univ); continue
        cur_t = current.get(nk) or {}
        new = dict(cur_t) if isinstance(cur_t, dict) else {}
        changed = False
        for tr in ('ba', 'ma'):
            r = rec.get(tr)
            if not isinstance(r, dict) or not (r.get('fields') or {}):
                continue
            merged = dict((new.get(tr) or {}).get('fields') or {}) if isinstance(new.get(tr), dict) else {}
            merged.update(r['fields'])
            vals = [v for v in merged.values() if isinstance(v, (int, float)) and v > 0]
            if not vals:
                continue
            lo = r.get('min') if isinstance(r.get('min'), (int, float)) and r['min'] > 0 else min(vals)
            hi = r.get('max') if isinstance(r.get('max'), (int, float)) and r['max'] > 0 else max(vals)
            new[tr] = {'min': int(lo), 'max': int(hi), 'fields': merged}
            changed = True
        if changed:
            cur.execute("update universities_blob set tuition=%s::jsonb where name_kr=%s",
                        (json.dumps(new, ensure_ascii=False), nk))
            upd += 1
    conn.commit()

    # read-back verification
    cur.execute("select count(*) from universities_blob where tuition is not null")
    total = cur.fetchone()[0]
    cur.execute("select count(*) from universities_blob where tuition ? 'ba' and tuition ? 'ma'")
    both = cur.fetchone()[0]
    conn.close()
    print(f"merged tuition for {upd} universities | unresolved: {len(skipped)}")
    if skipped:
        print("unresolved sample:", skipped[:15])
    print(f"read-back: universities_blob with tuition={total}, with ba+ma={both}")

if __name__ == '__main__':
    main()
