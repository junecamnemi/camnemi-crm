#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect the application/submission system for every university, by level.

Scans verified_kb for mentions of:
  - 유웨이 / uwayapply        -> 유웨이어플라이
  - 진학어플라이 / 진학사      -> 진학어플라이
  - 이메일 / 메일 / @...       -> 이메일 제출
  - 홈페이지 / 온라인 / 인터넷  -> 학교 홈페이지(온라인)
  - 우편                      -> 우편
  - 방문                      -> 방문
Separates by level: ba(schools) / junior / ma(master) / lang.
"""
import json, re, collections

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB, encoding="utf-8"))

SECTIONS = [("학부", kb["schools"]),
            ("전문대", kb["junior"]["schools"]),
            ("대학원", kb["master"]["schools"]),
            ("어학연수", kb["lang_programs"]["schools"])]

PATS = [
    ("유웨이어플라이", re.compile(r"유웨이|uway|uwayapply", re.I)),
    ("진학어플라이", re.compile(r"진학어플라이|진학사|jinhak", re.I)),
    ("이메일", re.compile(r"이메일|메일\s*제출|e-?mail|@[a-zA-Z0-9.\-]+\.(ac\.kr|com|kr|org)")),
    ("홈페이지", re.compile(r"홈페이지|온라인\s*접수|인터넷\s*접수|ipsi|입학사이트|웹\s*접수")),
    ("우편", re.compile(r"우편")),
    ("방문", re.compile(r"방문\s*접수|내방")),
]

def classify(v):
    blob = json.dumps(v, ensure_ascii=False)
    hits = [name for name, p in PATS if p.search(blob)]
    return hits

report = {}
for label, d in SECTIONS:
    counts = collections.Counter()
    detail = collections.defaultdict(list)
    unknown = []
    for school, v in d.items():
        hits = classify(v)
        if not hits:
            unknown.append(school); counts["미기재"] += 1; continue
        # priority: 플랫폼 > 이메일 > 홈페이지 > 우편/방문
        for h in hits:
            counts[h] += 1
            detail[h].append(school)
        primary = next((h for h in ["유웨이어플라이", "진학어플라이", "이메일", "홈페이지", "우편", "방문"] if h in hits), hits[0])
        counts[f"__primary:{primary}"] += 1
    report[label] = {"n": len(d), "counts": dict(counts), "detail": {k: v for k, v in detail.items()}, "unknown": unknown}

for label, r in report.items():
    print(f"\n===== {label} ({r['n']}개) =====")
    for k, v in sorted(r["counts"].items(), key=lambda x: -x[1]):
        if not k.startswith("__"):
            print(f"  {k}: {v}")
    print("  -- 주(主) 방식 --")
    for k, v in sorted(r["counts"].items(), key=lambda x: -x[1]):
        if k.startswith("__primary:"):
            print(f"    {k.split(':',1)[1]}: {v}")

json.dump(report, open(r"C:\Users\USER\camnemi-crm\backend\_apply_systems.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장: _apply_systems.json")
