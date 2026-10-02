#!/usr/bin/env python3
"""build_canonical.py — 파편화된 소스 → 단일 정본(canonical/schools.jsonl).
소스: 파싱캐시(_schools_parsed.jsonl) + KB(verified_kb) + 대학알리미(_tuition_acad.jsonl)
"""
import json, os, re, glob, math

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as _pp

# Resolve the corpus root through the ONE path layer. It used to hardcode the retired
# `내 드라이브` mirror, so this stage died with FileNotFoundError and the publish tail kept
# serving a week-old canonical/schools.jsonl while the job still looked green.
UP = str(_pp.drive_root())
CACHE_CANDIDATES = [os.path.join(UP, '_schools_parsed.jsonl'),
                    r'C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\_schools_parsed.jsonl']
CACHE = next((p for p in CACHE_CANDIDATES if os.path.exists(p)), CACHE_CANDIDATES[0])
ACAD_CANDIDATES = [os.path.join(UP, '_tuition_acad.jsonl'), r'C:\Users\wisew\_tuition_acad.jsonl']
ACAD = next((p for p in ACAD_CANDIDATES if os.path.exists(p)), ACAD_CANDIDATES[0])
KB = r'C:\Users\wisew\camnemi-crm\backend\verified_kb.json'
CDB = r'C:\Users\wisew\camnemi-crm\backend\consulting_db.json'
OUTDIR = r'C:\Users\wisew\camnemi-crm\backend\canonical'
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


def load_prev():
    """The canonical currently on disk, keyed by normalized school name."""
    m = {}
    if not os.path.exists(OUT):
        return m
    try:
        for l in open(OUT, encoding='utf-8'):
            l = l.strip()
            if not l:
                continue
            r = json.loads(l)
            m[norm(r.get('school'))] = r
    except Exception:
        pass
    return m


def backup_prev(keep=5):
    """Never let a rebuild silently destroy the last good canonical (it did on 2026-10-02)."""
    if not os.path.exists(OUT):
        return None
    import shutil, datetime
    dst = OUT + '.prev_' + datetime.datetime.now().strftime('%Y%m%d_%H%M')
    shutil.copy(OUT, dst)
    for p in sorted(glob.glob(OUT + '.prev_*'))[:-keep]:
        try:
            os.remove(p)
        except OSError:
            pass
    return dst


def carry_forward(school, prev):
    """Fill-only: keep enriched values this rebuild cannot reproduce.

    `build()` re-derives `programs` from the parse cache, which carries no
    colleges[].tuition_krw; `enrich_canonical` can only re-add them from academyinfo
    (_tuition_acad.jsonl — absent on this host) or the KB. Without this carry-forward a
    rebuild dropped tuition coverage 89% -> 49%, the publish gate went FAIL, and Supabase
    silently stopped updating.
    """
    n = 0
    pprogs = prev.get('programs') or {}
    for pk, d in (school.get('programs') or {}).items():
        if not isinstance(d, dict):
            continue
        pd = pprogs.get(pk)
        if not isinstance(pd, dict):
            continue
        prev_t = {c.get('college'): c.get('tuition_krw')
                  for c in (pd.get('colleges') or [])
                  if isinstance(c, dict) and c.get('tuition_krw')}
        cols = d.get('colleges') or []
        if not cols and (pd.get('colleges') or []):
            d['colleges'] = pd['colleges']
            n += len(pd['colleges'])
            continue
        for c in cols:
            if isinstance(c, dict) and not c.get('tuition_krw') and prev_t.get(c.get('college')):
                c['tuition_krw'] = prev_t[c.get('college')]
                n += 1
        for key in ('req', 'period', 'scholarships', 'tuition_krw', 'tuition_max'):
            if not d.get(key) and pd.get(key):
                d[key] = pd[key]
                n += 1
    return n


def build():
    merged = load_all()
    acad = load_acad()
    kb = load_json(KB, {}).get('schools', {})
    cdb = load_json(CDB, {}).get('schools', {})
    prev = load_prev()
    carried = 0
    out = []
    for k, e in merged.items():
        # canonical name: prefer a '학교'-suffixed clean name
        names = [n for n in e['names'] if n]
        canon = max(names, key=lambda n: (n.endswith('학교'), len(n))) if names else k
        school = {'school': canon, 'aliases': sorted(set(names))[:6],
                  'programs': e['progs'], 'sources': {}, 'validation': {}}
        # Fill-only carry-forward from the previous canonical (tuition/req/period/scholarships):
        # a rebuild must never lose enriched values it cannot reproduce from its own sources.
        pv = prev.get(norm(canon))
        if pv:
            carried += carry_forward(school, pv)
            for mk, mv in (pv.get('meta') or {}).items():
                school.setdefault('meta', {}).setdefault(mk, mv)
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
    backup = backup_prev()
    with open(OUT, 'w', encoding='utf-8') as f:
        for s in out:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    print(f"canonical: {len(out)} schools -> {OUT}")
    print(f"carried forward: {carried} enriched field(s) from the previous canonical"
          + (f" | backup: {os.path.basename(backup)}" if backup else " | no previous canonical"))
    print("with kb:", sum(1 for s in out if s['sources']['kb']),
          "| with academyinfo:", sum(1 for s in out if s['sources']['academyinfo']),
          "| with consulting_db:", sum(1 for s in out if s['sources']['consulting_db']))
    return out


if __name__ == '__main__':
    build()
