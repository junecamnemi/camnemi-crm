#!/usr/bin/env python3
"""publish_all.py — 정본 → 산출물 게시 (검증 통과 시에만).
① Supabase universities.programs
② 워크북 재빌드(선택, --xlsx)
사용: python publish_all.py [--force]
"""
import json, os, re, sys, math
import psycopg2

BE = r'C:\Users\wisew\camnemi-crm\backend'
CANON = os.path.join(BE, 'canonical', 'schools.jsonl')
REPORT = os.path.join(BE, 'validation_report.md')


def norm(s):
    return re.sub(r'[^\uac00-\ud7a3A-Za-z0-9]', '', str(s or '')).lower()


def load_canon():
    return [json.loads(l) for l in open(CANON, encoding='utf-8') if l.strip()]


def gate_ok():
    if not os.path.exists(REPORT):
        return False
    t = open(REPORT, encoding='utf-8').read()
    return t.count('❌') == 0


def build_programs(rec):
    """canonical programs -> 사이트용 {ba:{...}, ma:{...}, lang:{...}, junior:{...}}"""
    out = {}
    for pk, d in (rec.get('programs') or {}).items():
        cols = d.get('colleges') or []
        depts = []
        for c in cols:
            t = c.get('tuition_krw')
            for dep in (c.get('departments') or []):
                depts.append({
                    'college': c.get('college'), 'major': dep.get('major'),
                    'kor': bool(dep.get('korean_track')), 'eng': bool(dep.get('english_track')),
                    'topik': dep.get('topik'), 'ielts': dep.get('ielts'),
                    'tuition_krw': t, 'tuition_usd': (int(math.ceil(t/1350.0/100.0)*100) if t else None),
                })
        out[pk] = {
            'period': d.get('period'),
            'topik': (d.get('req') or {}).get('topik') if isinstance(d.get('req'), dict) else None,
            'ielts': (d.get('req') or {}).get('ielts') if isinstance(d.get('req'), dict) else None,
            'track_note': d.get('track_note'),
            'departments': depts,
            'scholarships': d.get('scholarships') or [],
        }
    return out


def main():
    force = '--force' in sys.argv
    if not force and not gate_ok():
        print("GATE FAIL — 게시 차단 (validation_report.md 확인). --force 로 우회 가능.")
        return 2
    recs = load_canon()
    pw = re.search(r'SUPABASE_DB_PASSWORD\s*=\s*(\S+)',
                   open(r'C:\Users\wisew\camnemi-crm\.env', encoding='utf-8').read()).group(1)
    conn = psycopg2.connect(host='aws-0-ap-northeast-2.pooler.supabase.com', port=5432,
                            user='postgres.zjdvzpylxazfbazioxto', password=pw, dbname='postgres')
    cur = conn.cursor()
    upd = 0
    for r in recs:
        progs = build_programs(r)
        if not progs:
            continue
        # match by name_kr (exact or normalized)
        cur.execute("select name_kr from universities")
        names = [x[0] for x in cur.fetchall()]
        m = None
        for n in names:
            if norm(n) == norm(r['school']) or (len(norm(r['school'])) > 3 and
                                                (norm(r['school']) in norm(n) or norm(n) in norm(r['school']))):
                m = n
                break
        if not m:
            continue
        cur.execute("update universities set programs=%s::jsonb where name_kr=%s",
                    (json.dumps(progs, ensure_ascii=False), m))
        upd += 1
    conn.commit()
    print(f"published programs -> Supabase: {upd} schools")
    return 0


if __name__ == '__main__':
    sys.exit(main())
