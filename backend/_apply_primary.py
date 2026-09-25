#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive the PRIMARY application system per school from the PDF scan (priority rules)."""
import json, collections

d = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\_apply_systems_pdf.json", encoding="utf-8"))
# priority: 플랫폼(유웨이/진학) > 홈페이지(온라인) > 이메일 > 우편 > 방문
PRIORITY = ["유웨이어플라이", "진학어플라이", "홈페이지", "이메일", "우편", "방문"]

def primary(systems):
    for p in PRIORITY:
        if p in systems:
            return p
    return systems[0] if systems else "?"

for lvl in ["학부", "전문대", "대학원", "어학연수"]:
    dd = d.get(lvl, {})
    c = collections.Counter()
    for s, v in dd.items():
        c[primary(v["systems"])] += 1
    print(f"=== {lvl} ({len(dd)}개) 주 방식 ===")
    for k, n in c.most_common():
        print(f"   {k}: {n}")
    print("   예시(5):", ", ".join(f"{s}({primary(v['systems'])})" for s, v in list(dd.items())[:5]))
    print()

# save a per-school primary table
out = {}
for lvl in ["학부", "전문대", "대학원", "어학연수"]:
    out[lvl] = {s: {"primary": primary(v["systems"]), "all": v["systems"], "file": v["file"]}
                for s, v in d.get(lvl, {}).items()}
json.dump(out, open(r"C:\Users\wisew\camnemi-crm\backend\_apply_primary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: _apply_primary.json")
