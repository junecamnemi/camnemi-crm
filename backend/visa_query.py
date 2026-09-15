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

def show_che(code):
    cs = KB.get("che_statuses", {})
    hit = next((k for k in cs if k.upper()==code.upper()), None)
    if not hit:
        print(f"[{code}] 체류자격: KB에 없음. 사용 가능 코드: {', '.join(sorted(cs.keys()))}"); return
    v = cs[hit]
    print(f"■ {hit} {v.get('name','')}")
    print(f"  대상: {v.get('target','')}")
    print(f"  체류기간: {v.get('duration','')}")
    print("  제출서류:")
    for d in (v.get("required_docs") or []): print(f"    · {d}")
    print(f"  활동범위: {v.get('activities','')}")
    print(f"  특이사항: {v.get('notes','')}")

def show_list():
    cs = KB.get("che_statuses", {})
    print(f"■ 체류자격 {len(cs)}개: " + ", ".join(sorted(cs.keys())))

def show_illegal():
    d = KB.get("illegal_stay", {})
    print("■ 불법체류 (출입국관리법)")
    print(f"  정의: {d.get('정의','')}")
    print("  [출국조치 3단계]")
    for s in d.get("3단계_출국조치", []):
        print(f"    {s.get('단계')} ({s.get('근거')}): {s.get('내용','')[:150]}")
    fp = d.get("형사처벌", {})
    print(f"  [형사처벌] {fp.get('근거')}: {fp.get('내용')}")
    print(f"  [과태료] {d.get('과태료',{}).get('근거')}: {d.get('과태료',{}).get('내용')}")
    print(f"  [입국규제] {d.get('입국규제',{}).get('근거')}: {d.get('입국규제',{}).get('내용')}")
    print(f"  [이의신청] {d.get('이의신청',{}).get('내용')}")

def show_g1(sub=None):
    d = KB.get("humanitarian_G1", {})
    print("■ 인도적체류 (G-1) — 출입국관리법 시행령 별표1")
    print(f"  정의: {d.get('정의','')}")
    print(f"  체류기간 상한: {d.get('체류기간_상한')}")
    print("  [세부구분]")
    for s in d.get("세부구분", []):
        if sub and sub.upper() not in str(s.get("code","")).upper(): continue
        print(f"    {s.get('code')}: {s.get('대상')} (기간 {s.get('기간')})")
    cw = d.get("취업_가능", {})
    print(f"  [취업] {cw.get('가능')}")
    print(f"    범위: {cw.get('범위')}")

ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
ap.add_argument("--family"); ap.add_argument("--income", action="store_true")
ap.add_argument("--sajeung"); ap.add_argument("--status"); ap.add_argument("--flow", action="store_true")
ap.add_argument("--photo", action="store_true")
ap.add_argument("--che"); ap.add_argument("--list", action="store_true")
ap.add_argument("--illegal", action="store_true"); ap.add_argument("--g1", nargs="?", const="", default=None)
a = ap.parse_args()
if a.flow: show_flow()
elif a.list: show_list()
elif a.che: show_che(a.che)
elif a.illegal: show_illegal()
elif a.g1 is not None: show_g1(a.g1)
elif a.photo: print("■ 외국인등록용 사진 규격\n"+KB.get("photo_spec",""))
elif a.income: show_income()
elif a.family: show_family(a.family)
elif a.sajeung: show_sajeung(a.sajeung)
elif a.status: show_status(a.status)
elif a.frm and a.to: show_transition(a.frm, a.to)
elif a.frm: show_change(a.frm)
else: ap.print_help()
