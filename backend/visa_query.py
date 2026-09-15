#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visa_query.py — Korea visa lookup for the bot/consulting (사증발급 + 체류변경 연결).

Usage:
  python visa_query.py --from D-4                 # what D-4 can change to (국내)
  python visa_query.py --from E-7 --to D-2        # is a specific change allowed?
  python visa_query.py --family D-2               # family invitation (F-3)
  python visa_query.py --income                   # income requirements table
  python visa_query.py --sajeung D-4              # 사증발급 서류 (해외 비자 신청)
  python visa_query.py --flow                     # 사증→입국→체류변경 연결 흐름
  python visa_query.py --status "D-2 유학"         # 전체 (사증+체류)
  python visa_query.py --photo                    # 외국인등록 사진 규격(OCR)
"""
import json, os, sys, argparse

B = r"C:\Users\USER\camnemi-crm\backend"
KB = json.load(open(os.path.join(B, "visa_kb_kr.json"), encoding="utf-8"))

def show_change(frm):
    cm = KB.get("change_matrix", {})
    hit = None
    for k in cm:
        if k.upper() == frm.upper() or k.startswith(frm.upper()):
            hit = k; break
    if not hit:
        print(f"[{frm}] 변경 규정: KB에 없음 (출입국 1345 확인)"); return
    v = cm[hit]
    print(f"■ {hit} → 변경 가능한 체류자격")
    if isinstance(v, dict):
        for kk in ("can_change_to", "allowed", "to"):
            if kk in v:
                for x in (v[kk] if isinstance(v[kk], list) else [v[kk]]):
                    if isinstance(x, dict):
                        print(f"  · {x.get('to','')}: {x.get('condition','')}  💰{x.get('income','')}")
                    else:
                        print(f"  · {x}")
        for kk in ("cannot_change_to", "restricted", "forbidden"):
            if kk in v:
                print(f"  ✗ 제한: {v[kk]}")
    else:
        print(" ", v)

def show_transition(frm, to):
    cm = KB.get("change_matrix", {}).get(frm.upper()) or {}
    vals = cm.get("can_change_to") if isinstance(cm, dict) else None
    if vals:
        for x in vals:
            nm = x.get("to","") if isinstance(x, dict) else str(x)
            if to.upper() in nm.upper():
                print(f"✅ {frm} → {to}: 가능")
                if isinstance(x, dict):
                    print(f"   조건: {x.get('condition','')}  💰소득: {x.get('income','')}")
                return
        print(f"❌ {frm} → {to}: 직접 변경 불가(KB 기준). 기타 경로/1345 확인.")
    else:
        print(f"[{frm}] 정보 없음")

def show_family(v):
    f = KB.get("family_invitation", {})
    hit = next((k for k in f if k.upper()==v.upper() or k.startswith(v.upper())), None)
    if not hit:
        print(f"[{v}] 가족초청: KB에 없음"); return
    print(f"■ {hit} 가족 초청: {f[hit]}")

def show_income():
    inc = KB.get("income_requirements", {})
    print("■ 2026 비자별 소득(임금) 요건")
    for k, val in inc.items():
        if k == "note": print(f"  ({val})"); continue
        amt = val.get("연봉") or val.get("기준") if isinstance(val, dict) else val
        print(f"  · {k}: {amt}")

def show_sajeung(v):
    bs = KB.get("by_status", {})
    hit = next((k for k in bs if v.upper() in k.upper()), None)
    if not hit:
        print(f"[{v}] 사증발급: KB에 없음"); return
    si = bs[hit].get("sajeung_issuance", {})
    print(f"■ {hit} — 사증발급(해외) 대상")
    print(f"  대상: {si.get('target','')}")
    print("  필수서류:")
    for d in (si.get("required_docs") or []): print(f"    · {d}")
    for c in (si.get("by_case") or []): print(f"    + (조건) {c}")
    print(f"  연결: {bs[hit].get('connection','')}")

def show_status(v):
    show_sajeung(v); print()
    bs = KB.get("by_status", {})
    hit = next((k for k in bs if v.upper() in k.upper()), None)
    if hit:
        dc = bs[hit].get("domestic_change", {})
        print(f"■ {hit} — 국내 체류자격 변경")
        print(f"  허용: {dc.get('allowed_from','')}")
        print(f"  제한: {dc.get('restricted_from','')}")
        print(f"  서류: {dc.get('required_docs','')}")
        print(f"  활동: {dc.get('activities','')}")

def show_flow():
    f = KB.get("flow", {})
    print("■ 사증발급 → 입국 → 체류변경 연결 흐름")
    for k, v in f.items(): print(f"  · {k}: {v}")
    print(f"  ★ 핵심: {f.get('key_path','')}")

ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
ap.add_argument("--family"); ap.add_argument("--income", action="store_true")
ap.add_argument("--sajeung"); ap.add_argument("--status"); ap.add_argument("--flow", action="store_true")
ap.add_argument("--photo", action="store_true")
a = ap.parse_args()
if a.flow: show_flow()
elif a.photo: print("■ 외국인등록용 사진 규격\n"+KB.get("photo_spec",""))
elif a.income: show_income()
elif a.family: show_family(a.family)
elif a.sajeung: show_sajeung(a.sajeung)
elif a.status: show_status(a.status)
elif a.frm and a.to: show_transition(a.frm, a.to)
elif a.frm: show_change(a.frm)
else: ap.print_help()
