# -*- coding: utf-8 -*-
"""Sync latest KB enrichment (MA, majors, pharmacy) into data.js.
Reads consulting_db (fresh) + verified_kb, updates data.js school entries."""
import json, re

DATA = r"C:\Users\USER\camnemi-crm\data.js"
KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"

content = open(DATA, encoding="utf-8").read()
s = content.find("["); d = 0
for i in range(s, len(content)):
    if content[i]=="[": d+=1
    elif content[i]=="]":
        d-=1
        if d==0: end=i; break
data = json.loads(content[s:end+1])

kb = json.load(open(KB, encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))

def norm(s):
    s = re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학원","").replace("대학","").replace(" ","")
    while s.endswith(("대학","대")) and len(s)>1:
        s = s[:-1] if s.endswith("대") else s[:-2]
    return s.replace(" ","")

# index consulting_db by norm
db_norm = {}
for n, v in db["schools"].items():
    db_norm[norm(n)] = v

updated = 0
for u in data:
    if u.get("type") != "univ": continue
    un = norm(str(u.get("n","")))
    if not un: continue
    dbe = db_norm.get(un)
    if not dbe:
        # fuzzy
        for k, v in db_norm.items():
            if len(k)>=2 and (k in un or un in k): dbe=v; break
    if not dbe: continue
    changed=False
    # sync majors_ba from consulting BA majors
    prog = dbe.get("programs",{}).get("BA",{})
    majors = prog.get("majors")
    if majors and not u.get("majors_ba"):
        if isinstance(majors, list):
            u["majors_ba"] = majors
        elif isinstance(majors, str):
            u["majors_ba"] = [m.strip() for m in majors.split("/") if m.strip()]
        changed=True
    # sync tuition if data.js missing
    t = prog.get("tuition")
    if t and not u.get("tuition"):
        u["tuition"] = t; changed=True
    if changed: updated += 1

# re-serialize
new = content[:s] + json.dumps(data, ensure_ascii=False, indent=1) + content[end+1:]
open(DATA, "w", encoding="utf-8").write(new)
print(f"data.js sync: {updated} entries updated")
print(f"total schools: {len(data)}")
