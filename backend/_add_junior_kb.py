#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add 2-year junior colleges (전문대학) to the verified KB, from data.js.
These are cheap, short (2-3yr) programs with low language requirements."""
import json, re, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

with open(DATA_FILE, encoding="utf-8") as f:
    content = f.read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            data = json.loads(content[start : i + 1])
            break

def majors_of(u):
    ba = u.get("majors_ba") or []
    if isinstance(ba, list):
        out = []
        for m in ba:
            if isinstance(m, str):
                out.append(m)
            elif isinstance(m, dict):
                out.append(m.get("kr", ""))
        if out:
            return out
    flat = u.get("majors") or []
    return [m for m in flat if isinstance(m, str)] if isinstance(flat, list) else []

def tuition_ba(u):
    tu = (u.get("tuition") or {}).get("ba") or {}
    return tu.get("min"), tu.get("max")

# build junior section
junior = {}
for u in data:
    if u.get("type") != "junior":
        continue
    nm = u.get("n", "")
    req = u.get("req") or {}
    tmin, tmax = tuition_ba(u)
    majors = [re.sub(r"^[·ㆍ\s]+", "", m) for m in majors_of(u) if m]
    junior[nm] = {
        "name": nm,
        "region": u.get("loc", ""),
        "rank": "-",
        "type": "전문대학(2~3년제)",
        "topik_req": req.get("topik"),
        "ielts_req": req.get("ielts"),
        "selftest": req.get("selftest", False),
        "n_majors": len(majors),
        "majors_sample": majors[:10],
        "tuition_min": tmin,
        "tuition_max": tmax,
    }

kb_path = os.path.join(BASE, "verified_kb.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

kb["junior"] = {
    "meta": "2년제 전문대학 (전문학사). 4년제보다 저렴하고 언어요건 낮음. TOPIK 2급 또는 IELTS 5.5 수준. 취업 중심.",
    "schools": junior,
}

with open(kb_path, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"전문대학 {len(junior)}개 KB에 추가 완료!")
print(f"\n=== 샘플 (서울 전문대) ===")
seoul = [s for s in junior.values() if s["region"] == "서울특별시"]
for s in sorted(seoul, key=lambda x: x["name"])[:15]:
    print(f"  {s['name']}: TOPIK {s['topik_req']}, IELTS {s['ielts_req']}, 전공 {s['n_majors']}개, 등록금 {s['tuition_min']}")

print(f"\n=== 등록금 낮은 순 (전체) ===")
with_t = sorted([s for s in junior.values() if s["tuition_min"]], key=lambda x: x["tuition_min"])
for s in with_t[:10]:
    print(f"  {s['name']}: {s['tuition_min']:,}~{s['tuition_max'] or ''}")
