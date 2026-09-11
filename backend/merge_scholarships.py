#!/usr/bin/env python3
"""merge_scholarships.py — merge DeepSeek-parsed structured scholarships into
universities.scholarships, split by 입학(enroll) / 재학(existing).

Reads scholarships_llm.jsonl (from parse_scholarships.py). For each university:
- collects scholarships from ALL its guides (ba / ma / lang / junior)
- tags each with `level` from the guide folder when the model didn't set one
- dedupes by (name, type, level), merging tiers
- preserves any existing scholarships already in the DB
"""
import os, re, json, urllib.request, urllib.parse
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
JSONL = os.path.join(BASE, "scholarships_llm.jsonl")

def _key():
    h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
    return re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h).group(1)

ALIAS = {'포스텍':'포항공과대학교','한국해양대학교':'국립한국해양대학교','한국교통대학교':'국립한국교통대학교',
         '부경대학교':'국립부경대학교','창원대학교':'국립창원대학교','용인송담대학교':'용인예술과학대학교'}
LEVEL = {'ba':'undergrad','ma':'grad','lang':'lang','junior':'junior'}

def main():
    key = _key()
    def get(p):
        r = urllib.request.Request("https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/" + p,
                                   headers={'apikey': key, 'Authorization': 'Bearer ' + key})
        return json.loads(urllib.request.urlopen(r, timeout=40).read())
    def patch(uid, body):
        r = urllib.request.Request(
            "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/universities?id=eq." + urllib.parse.quote(uid),
            data=json.dumps(body, ensure_ascii=False).encode(), method='PATCH',
            headers={'apikey': key, 'Authorization': 'Bearer ' + key,
                     'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
        urllib.request.urlopen(r, timeout=30).read()

    univs = {u['id']: u for u in get('universities?select=id,scholarships&limit=500')}

    def resolve(s):
        s = (s or '').strip()
        if s in univs: return s
        if s in ALIAS and ALIAS[s] in univs: return ALIAS[s]
        for a, uid in ALIAS.items():
            if a in s and uid in univs: return uid
        for uid in univs:
            if uid in s or s.startswith(uid): return uid
        return None

    rows = [json.loads(l) for l in open(JSONL, encoding='utf-8')] if os.path.exists(JSONL) else []
    by = defaultdict(list)
    for r in rows:
        uid = resolve(r.get('school'))
        if not uid: continue
        lvl = LEVEL.get(r.get('_prog'), 'undergrad')
        for s in (r.get('scholarships') or []):
            if not isinstance(s, dict) or not s.get('name'): continue
            s = dict(s)
            s.setdefault('level', lvl)
            if s.get('type') not in ('enroll', 'existing'): s['type'] = 'enroll'
            by[uid].append(s)

    upd = 0
    for uid, items in by.items():
        cur = univs[uid].get('scholarships') or []
        def key_of(s): return (str(s.get('name','')).strip(), s.get('type',''), s.get('level',''))
        merged = {key_of(s): s for s in cur}
        for s in items:
            k = key_of(s)
            if k in merged:
                # merge tiers
                t0 = merged[k].get('tiers') or []
                seen = {(t.get('score'), t.get('amount')) for t in t0}
                for t in (s.get('tiers') or []):
                    if (t.get('score'), t.get('amount')) not in seen:
                        t0.append(t); seen.add((t.get('score'), t.get('amount')))
                merged[k]['tiers'] = t0
            else:
                merged[k] = s
        out = list(merged.values())
        if out != cur:
            patch(uid, {'scholarships': out}); upd += 1
    print(f"merged scholarships for {upd} universities (parsed rows: {len(rows)})")
    counts = defaultdict(lambda: [0,0])
    for uid, items in by.items():
        for s in items: counts[uid][0 if s.get('type')=='enroll' else 1] += 1
    print("universities touched:", len(by))

if __name__ == '__main__':
    main()
