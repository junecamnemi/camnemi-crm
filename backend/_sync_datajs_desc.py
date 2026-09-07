# -*- coding: utf-8 -*-
"""Append descriptive (non-tier) scholarships for 전남대/포항공대 which are
'full/partial waiver' style (no numeric % ladder), from curation data."""
import json, re

DATA = r"C:\Users\USER\camnemi-crm\data.js"
BASE = r"C:\Users\USER\camnemi-crm\backend"

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
dn = {u.get("n"): u for u in data}

# load the two schools from curation
DESC = {}
for cf in ["_curation_out_batch0.json", "_curation_out_batch3.json"]:
    fp = BASE + "/" + cf
    for e in json.load(open(fp, encoding="utf-8")):
        n = e.get("school", "").replace("0002748_", "").strip()
        if n in ("전남대학교", "포항공과대학교"):
            desc = []
            if e.get("scholarship_enroll"):
                desc.append("입학: " + (e["scholarship_enroll"] if isinstance(e["scholarship_enroll"], str) else "; ".join(e["scholarship_enroll"])))
            if e.get("scholarship_existing"):
                desc.append("재학: " + (e["scholarship_existing"] if isinstance(e["scholarship_existing"], str) else "; ".join(e["scholarship_existing"])))
            DESC[n] = " / ".join(desc)

for name, txt in DESC.items():
    u = dn.get(name)
    if not u:
        print(f"SKIP {name}")
        continue
    sch = u.get("scholarships") or []
    # drop any auto-generated empty placeholders from prior syncs for this school
    sch = [s for s in sch if not s.get("name", "").startswith(("입학장학금(TOPIK", "재학 성적"))]
    sch.append({
        "name": "외국인 장학금(원본 요강)",
        "level": "undergrad",
        "type": "enroll",
        "tiers": [],
        "desc": txt,
    })
    u["scholarships"] = sch
    print(f"✓ {name}")

content_out = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end + 1:]
open(DATA, "w", encoding="utf-8").write(content_out)
print("done")
