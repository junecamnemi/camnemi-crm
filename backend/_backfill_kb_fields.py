# -*- coding: utf-8 -*-
"""Backfill region/loc/topik_req/ielts_req/rank into KB schools from data.js,
so advisor_query filters (region/ielts/topik) work for curated schools."""
import json, re

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
DATA = r"C:\Users\USER\camnemi-crm\data.js"

kb = json.load(open(KB, encoding="utf-8"))
content = open(DATA, encoding="utf-8").read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[": depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            end = i
            break
data = json.loads(content[start:end + 1])

dn = {u.get("n"): u for u in data if u.get("type") == "univ"}
ba = kb["schools"]

n_fixed = 0
for name, s in ba.items():
    u = dn.get(name)
    if not u:
        continue
    changed = False
    if not s.get("region") and u.get("loc"):
        s["region"] = u["loc"]
        changed = True
    if not s.get("loc") and u.get("loc"):
        s["loc"] = u["loc"]
        changed = True
    req = u.get("req") or {}
    if not s.get("topik_req") and req.get("topik"):
        s["topik_req"] = req["topik"]
        changed = True
    if not s.get("ielts_req") and req.get("ielts"):
        s["ielts_req"] = req["ielts"]
        changed = True
    if not s.get("rank") and u.get("rk"):
        s["rank"] = u["rk"]
        changed = True
    if changed:
        n_fixed += 1

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"보강 {n_fixed}개 학교")
