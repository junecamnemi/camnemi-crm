#!/usr/bin/env python3
"""merge_documents.py — merge parsed 제출서류 into universities.documents (by track).

documents shape in DB: {"ba":[{name,en,required,note,country_specific}], "ma":[...],
"lang":[...], "junior":[...]}, plus universities.country_notes (text).
"""
import os, re, json, urllib.request, urllib.parse
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
JSONL = os.path.join(BASE, "documents_llm.jsonl")
ALIAS = {'포스텍':'포항공과대학교','한국해양대학교':'국립한국해양대학교','한국교통대학교':'국립한국교통대학교',
         '부경대학교':'국립부경대학교','창원대학교':'국립창원대학교','용인송담대학교':'용인예술과학대학교'}

def main():
    h = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
    K = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", h).group(1)
    base = "https://zjdvzpylzazfbazioxto.supabase.co/rest/v1/" if False else "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/"
    def get(p):
        r = urllib.request.Request(base + p, headers={'apikey': K, 'Authorization': 'Bearer ' + K})
        return json.loads(urllib.request.urlopen(r, timeout=40).read())
    def patch(uid, body):
        r = urllib.request.Request(base + "universities?id=eq." + urllib.parse.quote(uid),
            data=json.dumps(body, ensure_ascii=False).encode(), method='PATCH',
            headers={'apikey': K, 'Authorization': 'Bearer ' + K,
                     'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
        urllib.request.urlopen(r, timeout=30).read()

    univs = {u['id']: u for u in get('universities?select=id,documents,country_notes&limit=500')}
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
    docs = defaultdict(lambda: defaultdict(list))
    notes = {}
    for r in rows:
        uid = resolve(r.get('school'))
        if not uid: continue
        tr = r.get('_prog') or 'ba'
        for d in (r.get('documents') or []):
            if isinstance(d, dict) and d.get('name'): docs[uid][tr].append(d)
        if r.get('country_notes') and len(r['country_notes']) > len(notes.get(uid, '')):
            notes[uid] = r['country_notes']

    upd = 0
    for uid in set(list(docs) + list(notes)):
        cur = univs[uid].get('documents') or {}
        new = dict(cur)
        for tr, items in docs.get(uid, {}).items():
            merged = {d.get('name'): d for d in (new.get(tr) or [])}
            for d in items: merged[d.get('name')] = d
            new[tr] = list(merged.values())
        body = {'documents': new}
        if notes.get(uid): body['country_notes'] = notes[uid]
        if new != cur or notes.get(uid):
            patch(uid, body); upd += 1
    print(f"merged documents for {upd} universities (parsed rows {len(rows)})")
    tot = sum(len(v) for u in docs.values() for v in u.values())
    print(f"total document entries: {tot}")

if __name__ == '__main__':
    main()
