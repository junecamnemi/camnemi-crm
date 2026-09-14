#!/usr/bin/env python3
"""build_canonical.py — 파편화된 소스 → 단일 정본(canonical/schools.jsonl).
소스: 파싱캐시(_schools_parsed.jsonl) + KB(verified_kb) + 대학알리미(_tuition_acad.jsonl)
"""
import json, os, re, glob, math

UP = r'C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project'
CACHE = os.path.join(UP, '_schools_parsed.jsonl')
ACAD = r'C:\Users\USER\_tuition_acad.jsonl'
KB = r'C:\Users\USER\camnemi-crm\backend\verified_kb.json'
CDB = r'C:\Users\USER\camnemi-crm\backend\consulting_db.json'
OUTDIR = r'C:\Users\USER\camnemi-crm\backend\canonical'
OUT = os.path.join(OUTDIR, 'schools.jsonl')
os.makedirs(OUTDIR, exist_ok=True)


def norm(s):
    return re.sub(r'[^\uac00-\ud7a3A-Za-z0-9]', '', str(s or '')).lower()


def key_of(nm):
    k = re.sub(r'\.pdf$', '', str(nm), flags=re.I)
    k = re.sub(r'_(전문학사|모집요강|입학안내|한국어교육원|대학원|외국인|재외국민|영어트랙).*$', '', k)
    k = re.sub(r'[\[\]\(\)].*$', '', k).strip()
    k = re.sub(r'(학교|대학교|대학|대)$', '', k)
    return re.sub(r'[^\uac00-\ud7a3A-Za-z0-9]', '', k)


def clean_name(nm):
    c = re.sub(r'\.pdf$', '', str(nm), flags=re.I)
    c = re.sub(r'_(전문학사|모집요강|입학안내|한국어교육원|대학원|외국인|재외국민|영어트랙|BA|MA).*$', '', c)
    c = re.sub(r'[\[\]\(\)].*$', '', c).strip()
    return c or str(nm)


def load_all():
    rows = [json.loads(l) for l in open(CACHE, encoding='utf-8') if l.strip()]
    # merge by normalized key
    merged = {}
    for d in rows:
        raw = d.get('_school') or ''
        k = key_of(raw)
        if len(k) < 2:
            continue
        e = merged.setdefault(k, {'names': [], 'progs': {}})
        e['names'].append(clean_name(raw))
        e['progs'][d.get('_program')] = d
    return merged


def load_acad():
    m = {}
    if os.path.exists(ACAD):
        for l in open(ACAD, encoding='utf-8'):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get('n'):
                m[norm(r['univ'])] = r
    return m


def load_json(p, default):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return default


def usd(krw):
    return int(math.ceil((krw or 0) / 1350.0 / 100.0) * 100)


def build():
    merged = load_all()
    acad = load_acad()
    kb = load_json(KB, {}).get('schools', {})
    cdb = load_json(CDB, {}).get('schools', {})
    out = []
    for k, e in merged.items():
        # canonical name: prefer a '학교'-suffixed clean name
        names = [n for n in e['names'] if n]
        canon = max(names, key=lambda n: (n.endswith('학교'), len(n))) if names else k
        school = {'school': canon, 'aliases': sorted(set(names))[:6],
                  'programs': e['progs'], 'sources': {}, 'validation': {}}
        # sources / cross-refs
        kb_rec = next((v for kk, v in kb.items() if norm(kk) == norm(canon) or
                       norm(kk) in norm(canon) or norm(canon) in norm(kk)), None)
        cdb_rec = next((v for kk, v in cdb.items() if norm(kk) == norm(canon)), None)
        ac = acad.get(norm(canon))
        school['sources'] = {
            'parse_cache': True,
            'kb': bool(kb_rec),
            'consulting_db': bool(cdb_rec),
            'academyinfo': (ac or {}).get('schlId'),
            'n_pdfs': len(e['progs']),
        }
        if ac and ac.get('rows'):
            school['meta'] = {'academyinfo_tuition_sample': ac['rows'][:3]}
            school['meta']['academyinfo_n_major'] = ac.get('n')
        if kb_rec:
            if kb_rec.get('student_count'):
                school.setdefault('meta', {})['students'] = kb_rec['student_count']
            if kb_rec.get('track'):
                school.setdefault('meta', {})['track_kb'] = kb_rec['track']
        out.append(school)
    out.sort(key=lambda x: x['school'])
    with open(OUT, 'w', encoding='utf-8') as f:
        for s in out:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    print(f"canonical: {len(out)} schools -> {OUT}")
    print("with kb:", sum(1 for s in out if s['sources']['kb']),
          "| with academyinfo:", sum(1 for s in out if s['sources']['academyinfo']),
          "| with consulting_db:", sum(1 for s in out if s['sources']['consulting_db']))
    return out


if __name__ == '__main__':
    build()
