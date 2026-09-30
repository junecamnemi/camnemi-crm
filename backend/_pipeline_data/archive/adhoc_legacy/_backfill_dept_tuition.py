# -*- coding: utf-8 -*-
"""Backfill per-major (fields) tuition from data.js → verified_kb + consulting_db.
data.js has 133 schools with tuition.ba.fields; KB/consulting only 1/0. Sync them."""
import json, re

DATA = r"C:\Users\wisew\camnemi-crm\data.js"
KB   = r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json"
DB   = r"C:\Users\wisew\camnemi-crm\backend\consulting_db.json"

content = open(DATA, encoding="utf-8").read()
s = content.find("["); d=0
for i in range(s, len(content)):
    if content[i]=="[": d+=1
    elif content[i]=="]":
        d-=1
        if d==0: end=i; break
data = json.loads(content[s:end+1])

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)","",str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x=x[:-len(suf)]; break
    if x.endswith("대") and len(x)>1: x=x[:-1]
    return x.replace(" ","")

# collect fields from data.js univ
fields_map = {}
for u in data:
    t = u.get("tuition")
    if isinstance(t, dict) and isinstance(t.get("ba"), dict):
        ba = t["ba"]
        f = ba.get("fields")
        if f:
            fields_map[norm(u.get("n",""))] = {"fields": f, "min": ba.get("min"), "max": ba.get("max")}
print(f"data.js 학과별 등록금: {len(fields_map)}개")

# 1) verified_kb
kb = json.load(open(KB, encoding="utf-8"))
kb_upd = 0
for name, v in kb["schools"].items():
    n = norm(name)
    if n in fields_map:
        fm = fields_map[n]
        # store as by_dept + also as fields inside tuition_semester if dict
        v["tuition_semester_by_dept"] = {
            "note": "계열별(학과별) 등록금 — data.js에서 역방향 동기화",
            "fields": fm["fields"],
            "min": fm["min"], "max": fm["max"],
        }
        kb_upd += 1
json.dump(kb, open(KB,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"verified_kb 반영: {kb_upd}")

# 2) consulting_db (also handle fuzzy for univ present there)
db = json.load(open(DB, encoding="utf-8"))
db_upd = 0
for name, school in db["schools"].items():
    n = norm(name)
    tgt = fields_map.get(n)
    if tgt is None:
        for k, v in fields_map.items():
            if len(k)>=3 and (k in n or n in k): tgt=v; break
    if not tgt: continue
    prog = school["programs"].get("BA")
    if prog is None: continue
    if isinstance(prog.get("tuition"), dict):
        prog["tuition"]["fields"] = tgt["fields"]
    else:
        prog["tuition"] = {"min": tgt["min"], "max": tgt["max"], "fields": tgt["fields"]}
    db_upd += 1
json.dump(db, open(DB,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting_db 반영: {db_upd}")
