#!/usr/bin/env python3
"""merge_tuition.py — merge structured tuition JSON into Supabase universities.tuition.

WHY THIS EXISTS (2026-09 lesson):
  The DeepSeek/guide parser reads 모집요강 (admission GUIDELINES). Those documents
  contain eligibility / schedule / documents — NOT tuition tables. Tuition lives in a
  SEPARATE '등록금 명세표' document, so a guide parse cannot populate tuition.
  Worse, the first LLM merge only wrote majors + period and silently DROPPED the
  tuition text, so 96 universities had missing/1-field tuition (연세대 showed only
  the humanities minimum, 한양대/고려대 were empty).

USAGE:
  python merge_tuition.py <input.json>
  input.json: [{"univ":"연세대학교","ba":{"min":..,"max":..,"fields":{"인문사회":..}},
                "ma":{"fields":{..}},"lang":{"fields":{..}}}, ...]
  Merges by univ id (with alias resolution). Existing fields are preserved; new
  field values overwrite. min/max recomputed from the merged field map when absent.

ALWAYS run this after collecting tuition, and add it to the daily pipeline so a
collect step can never again be disconnected from the DB.
"""
import json, os, re, sys, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
ALIAS = {'포스텍': '포항공과대학교', '한국해양대학교': '국립한국해양대학교',
         '한국교통대학교': '국립한국교통대학교', '부경대학교': '국립부경대학교',
         '창원대학교': '국립창원대학교', '용인송담대학교': '용인예술과학대학교'}

def _key():
    h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
    return re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h).group(1)

def _get(key, path):
    r = urllib.request.Request("https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/" + path,
                               headers={'apikey': key, 'Authorization': 'Bearer ' + key})
    return json.loads(urllib.request.urlopen(r, timeout=40).read())

def _patch(key, uid, body):
    r = urllib.request.Request(
        "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/universities?id=eq." + urllib.parse.quote(uid),
        data=json.dumps(body, ensure_ascii=False).encode(), method='PATCH',
        headers={'apikey': key, 'Authorization': 'Bearer ' + key,
                 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    urllib.request.urlopen(r, timeout=30).read()

def merge(records):
    key = _key()
    univs = {u['id']: u for u in _get(key, 'universities?select=id,tuition&limit=500')}

    def resolve(s):
        s = (s or '').strip()
        if s in univs: return s
        if s in ALIAS and ALIAS[s] in univs: return ALIAS[s]
        for a, uid in ALIAS.items():
            if a in s and uid in univs: return uid
        for uid in univs:
            if uid in s or s.startswith(uid): return uid
        return None

    upd, skipped = 0, []
    for rec in records:
        uid = resolve(rec.get('univ'))
        if not uid:
            skipped.append(rec.get('univ')); continue
        cur = univs[uid].get('tuition') or {}
        new, changed = dict(cur), False
        for tr in ('ba', 'ma', 'lang'):
            r = rec.get(tr)
            if not isinstance(r, dict) or not (r.get('fields') or {}): continue
            merged = dict((cur.get(tr) or {}).get('fields') or {})
            merged.update(r['fields'])
            vals = [v for v in merged.values() if isinstance(v, (int, float)) and v > 0]
            if not vals: continue
            lo = r.get('min') if isinstance(r.get('min'), (int, float)) and r['min'] > 0 else min(vals)
            hi = r.get('max') if isinstance(r.get('max'), (int, float)) and r['max'] > 0 else max(vals)
            new[tr] = {'min': int(lo), 'max': int(hi), 'fields': merged}
            changed = True
        if changed:
            _patch(key, uid, {'tuition': new}); upd += 1
    return upd, skipped

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    recs = list(data.values()) if isinstance(data, dict) else data
    upd, skipped = merge(recs)
    print(f"merged tuition for {upd} universities | unresolved: {skipped[:10]}")
