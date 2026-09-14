# -*- coding: utf-8 -*-
"""Sync KB lang_bypass → data.js (both univ & junior). Exact-normalized matching only."""
import json, re

DATA = r"C:\Users\USER\camnemi-crm\data.js"
KB   = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"

content = open(DATA, encoding="utf-8").read()
s = content.find("["); d=0
for i in range(s, len(content)):
    if content[i]=="[": d+=1
    elif content[i]=="]":
        d-=1
        if d==0: end=i; break
data = json.loads(content[s:end+1])
kb = json.load(open(KB, encoding="utf-8"))

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x = x[:-len(suf)]; break
    if x.endswith("대") and len(x)>1: x = x[:-1]
    return x.replace(" ", "")

# build KB index: norm -> (level, school, lang_bypass)
kb_idx = {}
for sec,key,lvl in [("schools","schools","BA"),("master","master","MA"),("junior","junior","junior")]:
    node = kb[key]
    schools = node.get("schools", node)
    for name, v in schools.items():
        if v.get("lang_bypass"):
            kb_idx.setdefault(norm(name), {})[lvl] = v["lang_bypass"]

# match data.js entries by (type, name) — exact norm first, then unique-prefix
def find(entry):
    n = norm(entry.get("n",""))
    if n in kb_idx: return kb_idx[n]
    # prefix fallback but require uniqueness
    cands = [k for k in kb_idx if len(n)>=3 and (k==n or k.startswith(n) or n.startswith(k))]
    if len(cands)==1: return kb_idx[cands[0]]
    return None

upd_univ=upd_jr=0
for u in data:
    hit = find(u)
    if not hit: continue
    lvl = "BA" if u.get("type")=="univ" else "junior"
    lb = hit.get(lvl) or hit.get("BA") or hit.get("MA") or hit.get("junior")
    if not lb: continue
    if u.get("lang_bypass") == lb: continue
    u["lang_bypass"] = lb
    if u.get("type")=="univ": upd_univ+=1
    else: upd_jr+=1

new = content[:s] + json.dumps(data, ensure_ascii=False, indent=1) + content[end+1:]
open(DATA,"w",encoding="utf-8").write(new)
print(f"data.js lang_bypass 동기화: univ {upd_univ} | junior {upd_jr}")
print(f"총 엔트리: {len(data)}")
cov = sum(1 for u in data if u.get("lang_bypass"))
print(f"lang_bypass 보유: {cov}/{len(data)}")
