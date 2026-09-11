#!/usr/bin/env python3
"""Merge the DeepSeek-parsed guide results into Supabase."""
import json, os, re, urllib.request, urllib.parse
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(BASE, 'guides_llm_parsed.jsonl'), encoding='utf-8')]
H = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
K = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", H).group(1)
URL = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/"

def api(method, path, body=None, prefer=None):
    hdr = {"apikey": K, "Authorization": "Bearer " + K, "Content-Type": "application/json"}
    if prefer: hdr["Prefer"] = prefer
    r = urllib.request.Request(URL + path, data=(json.dumps(body).encode() if body else None), method=method, headers=hdr)
    with urllib.request.urlopen(r, timeout=40) as resp:
        t = resp.read().decode()
        return json.loads(t) if t.strip() else None

univs = {u['id']: u for u in api('GET', 'universities?select=id,majors_ba,majors_ma&limit=500')}
print("universities:", len(univs))

# group parsed majors by (school, is_ma)
by_school = defaultdict(lambda: {'ba': set(), 'ma': set()})
matched = 0; unmatched = set()
for r in rows:
    s = (r.get('school') or '').strip()
    if not s: continue
    # normalize: strip campus parentheticals, match longest univ id contained
    cand = None
    if s in univs: cand = s
    else:
        for uid in univs:
            if uid in s or s.startswith(uid):
                if cand is None or len(uid) > len(cand): cand = uid
    if not cand:
        unmatched.add(s); continue
    matched += 1
    key = 'ma' if r.get('program') == 'ma' else 'ba'
    for m in (r.get('majors') or []):
        m = str(m).strip()
        if m: by_school[cand][key].add(m)

print(f"matched rows: {matched} | unmatched schools: {len(unmatched)}")
for u in list(unmatched)[:10]: print("   ?", u)

upd = ok = fail = 0
for uid, d in by_school.items():
    u = univs[uid]
    patch = {}
    # merge with existing majors (keep existing + new)
    def merge(field, newset):
        cur = u.get(field) or []
        names = {(m.get('kr') if isinstance(m, dict) else m) for m in cur}
        out = list(cur)
        for m in sorted(newset):
            if m not in names: out.append({'kr': m}); names.add(m)
        return out
    if d['ba']:
        patch['majors_ba'] = merge('majors_ba', d['ba'])
    if d['ma']:
        patch['majors_ma'] = merge('majors_ma', d['ma'])
    if not patch: continue
    try:
        api('PATCH', f"universities?id=eq.{urllib.parse.quote(uid)}", patch, prefer='return=minimal'); upd += 1
    except Exception as e:
        fail += 1
print(f"\nupdated universities: {upd} | failed: {fail}")
