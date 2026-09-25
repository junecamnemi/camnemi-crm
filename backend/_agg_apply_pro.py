#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggregate the DeepSeek-Pro application-system classification by level."""
import json, re, collections, os

P = r"C:\Users\wisew\camnemi-crm\backend\_apply_pro.jsonl"
rows = [json.loads(l) for l in open(P, encoding="utf-8") if l.strip()]
print(f"총 {len(rows)}개 판별\n")

def school(fn):
    s = re.sub(r"^\d+_", "", fn)
    s = re.sub(r"_?(2026|2027|외국인|전문학사|대학원|한국어교육원|모집요강|입학안내|\(렌더\)|\[본교\]|\[제2캠퍼스\]|_original).*$", "", s)
    return s.strip("_ -") or fn

out = {}
for lvl in ["학부", "전문대", "대학원", "어학연수"]:
    rs = [r for r in rows if r.get("_level") == lvl]
    # dedupe by school (prefer non-미기재)
    by = {}
    for r in rs:
        s = school(r["_file"])
        if s not in by or (by[s]["primary"] == "미기재" and r["primary"] != "미기재"):
            by[s] = r
    c = collections.Counter(v["primary"] for v in by.values())
    out[lvl] = {"n": len(by), "dist": dict(c),
                "schools": {s: {"primary": v["primary"], "all": v.get("all"), "ev": v.get("evidence")} for s, v in sorted(by.items())}}

for lvl, v in out.items():
    print(f"===== {lvl} ({v['n']}개교) =====")
    for k, n in sorted(v["dist"].items(), key=lambda x: -x[1]):
        print(f"   {k}: {n}")
    print()

# dump school lists per primary
lines = []
for lvl, v in out.items():
    lines.append(f"\n## {lvl} ({v['n']}개교)\n")
    for prim in ["유웨이어플라이", "진학어플라이", "홈페이지", "이메일", "우편", "방문", "미기재"]:
        ss = [s for s, x in v["schools"].items() if x["primary"] == prim]
        if ss:
            lines.append(f"### {prim} ({len(ss)})\n" + ", ".join(ss) + "\n")
open(r"C:\Users\wisew\camnemi-crm\backend\지원시스템_레벨별.md", "w", encoding="utf-8").write("\n".join(lines))
json.dump(out, open(r"C:\Users\wisew\camnemi-crm\backend\_apply_pro_agg.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: 지원시스템_레벨별.md / _apply_pro_agg.json")
