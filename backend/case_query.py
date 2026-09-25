#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case_query.py — 상담 케이스 프로필 조회/검증.

  python case_query.py --list                 케이스 목록
  python case_query.py CASE-2026-001          케이스 상세
  python case_query.py --match "E-9 출산"      상황으로 케이스 검색
"""
import json, os, re, argparse
B = r"C:\Users\wisew\camnemi-crm\backend"
CASES = json.load(open(os.path.join(B,"cases_kr.json"), encoding="utf-8"))["cases"]
try:
    QA = json.load(open(os.path.join(B,"qa_profiles_kr.json"), encoding="utf-8"))
    CASES = CASES + QA
except Exception:
    pass

def show(c):
    print(f"\n{'='*70}\n■ [{c['id']}] {c['title']}\n{'='*70}")
    p = c.get("profile",{})
    print(f"  체류자격: {p.get('체류자격','')} | 국적: {p.get('국적','')}")
    print(f"  상황: {p.get('상황','')}")
    print(f"  질문: {', '.join(p.get('질문',[]))}")
    for a in c.get("answers",[]):
        print(f"\n  ── Q. {a['q']}")
        print(f"     A. {a['a']}")
        for x in (a.get("절차") or []): print(f"        · {x}")
        if a.get("예외경로"): print(f"     ※ {a['예외경로']}")
        print(f"     [근거] {a.get('근거','')}")
        if a.get("공식출처"): print(f"     [공식] {', '.join(a['공식출처'])}")
    for x in (c.get("주의") or []): print(f"  ⚠ {x}")
    if c.get("다음단계"): print(f"  ▶ 다음단계: {', '.join(c['다음단계'])}")

def match(q):
    kws = [w for w in re.findall(r"[가-힣A-Za-z0-9\-]{2,}", q)]
    best, bs = None, 0
    for c in CASES:
        txt = json.dumps(c, ensure_ascii=False)
        sc = sum(1 for k in kws if k in txt)
        if sc>bs: best,bs=c,sc
    return best, bs

ap=argparse.ArgumentParser()
ap.add_argument("case", nargs="?", default=""); ap.add_argument("--list",action="store_true"); ap.add_argument("--match")
a=ap.parse_args()
if a.list:
    print("■ 케이스:")
    for c in CASES: print(f"  · [{c['id']}] {c['title']}")
elif a.match:
    c,sc=match(a.match)
    if c and sc>=2: show(c)
    else: print(f"매칭 케이스 없음 (score {sc})")
elif a.case:
    for c in CASES:
        if c["id"]==a.case or a.case in c["title"]: show(c); break
    else: print("케이스 없음")
else: ap.print_help()
