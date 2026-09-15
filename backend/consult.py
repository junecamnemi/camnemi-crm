#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consult.py — consultation engine: situation -> matched guidance (from astra-built consultation KB + visa/labor KB).

Usage:
  python consult.py "임금을 못 받았어요"           # 상황 → 상담 안내
  python consult.py --topic "사업장변경"           # 주제 직접
  python consult.py --list                         # 주제 목록
"""
import json, os, re, sys, argparse

B = r"C:\Users\USER\camnemi-crm\backend"
CONSULT = json.load(open(os.path.join(B,"consultation_kr.json"), encoding="utf-8"))
VKB = json.load(open(os.path.join(B,"visa_kb_kr.json"), encoding="utf-8"))
LABOR = json.load(open(os.path.join(B,"labor_medical_rights_kr.json"), encoding="utf-8"))
try:
    OFFICIAL = json.load(open(os.path.join(B,"official_answers_kb.json"), encoding="utf-8"))
except Exception:
    OFFICIAL = {}

def search_official(s):
    """search official Q&A/interpretations by keyword."""
    hits=[]
    for x in OFFICIAL.get("hikorea_faq", []):
        if any(w in (x.get("q","")+x.get("q","")) for w in re.findall(r"[가-힣]{2,}", s)):
            hits.append(("하이코리아 FAQ", x.get("q",""), x.get("url","")))
    for x in OFFICIAL.get("labor_interpretations", []):
        kws = re.findall(r"[가-힣]{2,}", s)
        if any(k in x.get("text","") for k in kws if len(k)>1):
            hits.append((x.get("source","고용노동부 질의회시"), x.get("text","")[:220], "moel.go.kr"))
    for k,v in (OFFICIAL.get("easylaw") or {}).items():
        if any(w in v.get("text","") for w in re.findall(r"[가-힣]{3,}", s)[:5]):
            hits.append(("생활법령정보(법제처) "+k, v.get("text","")[:220], v.get("url","")))
    # dedupe
    seen=set(); out=[]
    for h in hits:
        if h[1][:40] not in seen: seen.add(h[1][:40]); out.append(h)
    return out[:6]

# keyword -> topic index (situation matching)
KW = {
 "임금체불":["임금","체불","급여","월급","시급","못 받","지급","미지급"],
 "퇴직금":["퇴직금","퇴사","출국만기","만기보험","차액"],
 "산재":["산재","산업재해","공상","다쳐","부상","재해","요양"],
 "부당해고":["해고","권고사직","그만두라","부당"],
 "사업장변경":["사업장","이직","근무처","다른 공장","옮기"],
 "건강보험·의료":["병원","의료","진료","수술","치료","건강보험","의료비","통역"],
 "체류·재입국":["체류","재입국","연장","자격변경","외국인등록","비자"],
 "불법체류·자진출국":["불법체류","미등록","자진출국","강제퇴거","오버스테이"],
 "기숙사비·근로계약":["기숙사","숙소","계약서","근로계약","공제"],
 "최저임금·수당":["최저임금","주휴","연차","수당","초과근무"],
}
def kw_topics(s):
    hit=[]
    for t,kws in KW.items():
        if any(k in s for k in kws): hit.append(t)
    return hit

def match_topic(s):
    """score consultation topics by keyword overlap + substring."""
    best, bs = None, -1
    kt = kw_topics(s)
    for c in CONSULT:
        topic = c.get("topic","")
        score = 0
        for k in kt:
            if k.split("·")[0] in topic or any(w in topic for w in k.split("·")): score += 3
        for p in (c.get("situation_patterns") or []):
            for w in re.findall(r"[가-힣]{2,}", p):
                if w in s: score += 1
        if score > bs: best, bs = c, score
    return best, bs

def show(c):
    print(f"\n■ {c.get('topic','')}")
    print(f"  (관련 사례 {c.get('_n_cases','?')}건)")
    sp = c.get("situation_patterns") or []
    if sp:
        print("  [전형적 상황]")
        for x in sp[:5]: print(f"    · {x}")
    if c.get("guidance"):
        print(f"\n  [핵심 안내]\n    {c['guidance']}")
    for key,label in [("procedure","절차"),("required_docs","필요 서류"),("legal_basis","근거 법령"),("agencies","담당기관"),("cautions","주의")]:
        v = c.get(key) or []
        if v:
            print(f"\n  [{label}]")
            for x in v[:8]: print(f"    · {x}")
    cq = c.get("common_questions") or []
    if cq:
        print("\n  [자주 묻는 질문]")
        for x in cq[:4]:
            print(f"    Q. {x.get('q','')}")
            print(f"    A. {str(x.get('a',''))[:220]}")
    oi = c.get("official_interpretations") or []
    if oi:
        print("\n  [공식 유권해석 (고용노동부 질의회시집)]")
        for x in oi[:3]:
            print(f"    · (p{x.get('page')}) {str(x.get('text',''))[:180]}")
    os_ = c.get("official_sources") or []
    if os_:
        print("\n  [공식 출처]")
        for x in os_:
            print(f"    · {x.get('소스')} — {x.get('url')}")

def extra_kb(s):
    """attach matching visa/labor KB entries."""
    out=[]
    for t,kws in KW.items():
        if any(k in s for k in kws):
            for k2 in ["불법체류","자진출국","범칙금"]:
                if k2 in t or t in k2: pass
            if t=="퇴직금" and "출국만기보험" in LABOR: out.append(("출국만기보험", LABOR["출국만기보험"]))
            if t=="산재" and "산업재해" in LABOR: out.append(("산업재해", LABOR["산업재해"]))
            if t=="임금체불" and "임금체불" in LABOR: out.append(("임금체불", LABOR["임금체불"]))
            if t=="최저임금·수당" and "근로조건" in LABOR: out.append(("근로조건", LABOR["근로조건"]))
    if "자진출국" in s or "불법체류" in s or "미등록" in s:
        if "voluntary_departure" in VKB: out.append(("자진출국", VKB["voluntary_departure"]))
        if "illegal_stay" in VKB: out.append(("불법체류", VKB["illegal_stay"]))
    return out

def show_extra(items):
    for name, d in items[:3]:
        print(f"\n  ── [KB:{name}] ──")
        print("   ", json.dumps(d, ensure_ascii=False)[:600])

ap = argparse.ArgumentParser()
ap.add_argument("situation", nargs="?", default="")
ap.add_argument("--topic"); ap.add_argument("--list", action="store_true")
ap.add_argument("--official", action="store_true")
a = ap.parse_args()
if a.list:
    print("■ 상담 주제:")
    for c in CONSULT: print(f"  · {c.get('topic','')[:70]} ({c.get('_n_cases')}건)")
elif a.official and a.situation:
    print(f"[공식 자료 검색] {a.situation}")
    hits = search_official(a.situation)
    if hits:
        for src, txt, url in hits: print(f"\n  · [{src}] {txt}\n    {url}")
    else:
        print("  매칭 공식자료 없음")
    print(f"\n  ※ 공식 문의: 법무부 1345 / 고용노동부 1350")
elif a.topic:
    for c in CONSULT:
        if a.topic in c.get("topic",""): show(c); break
elif a.situation:
    c, sc = match_topic(a.situation)
    if c and sc>0:
        print(f"[상황] {a.situation}")
        show(c)
        show_extra(extra_kb(a.situation))
        hits = search_official(a.situation)
        if hits:
            print("\n  [공식 자료 (법무부/고용노동부/법제처)]")
            for src, txt, url in hits[:4]:
                print(f"    · [{src}] {txt[:150]}")
    else:
        print(f"[상황] {a.situation}\n  매칭 주제 없음 — --list 로 주제 확인 또는 1345 상담")
else:
    ap.print_help()
