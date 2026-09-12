#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply school-status findings from _realguide2.json to verified_kb + consulting_db.

  광양보건대학교  -> closed (폐교 2026-08-31)            : 추천 제외
  군산간호대학교  -> no_foreigner_track (외국인 전형 없음) : 추천 제외
  송곡대학교      -> active (외국인전형 운영, 공개PDF 미확보)

Adds `status` / `status_note` and mirrors into consulting_db.
"""
import json, os, re, shutil, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json"); CDB = os.path.join(B, "consulting_db.json")

FINDINGS = {
    "광양보건대학교": {"status": "closed",
        "status_note": "폐교(2026-08-31). 법인 양남학원 파산선고 2026-06-19. 2026 외국인 모집요강 부존재 — 추천 제외.",
        "recommend_exclude": True},
    "군산간호대학교": {"status": "no_foreigner_track",
        "status_note": "외국인/재외국민 전형 미운영(2026 입학전형 시행계획 확인). 일반·지역고교·특성화고·간호조무사 등만 — 외국인 추천 대상 아님.",
        "recommend_exclude": True},
    "송곡대학교": {"status": "active",
        "status_note": "재외국민·외국인(순수외국인) 정원외 특별전형 운영(지원자격: 부모 모두 외국인 / 외국서 초·중등 전과정). 단 공개 모집요강 PDF 미확보(입학사이트 SSO 로그인 차단) — 자료 확인 필요.",
        "recommend_exclude": False},
}

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, KB.replace(".json", f"_bak_status_{datetime.date.today()}.json"))

applied = []
d = kb["junior"]["schools"]
idx = {norm(k): k for k in d}
for name, meta in FINDINGS.items():
    k = idx.get(norm(name))
    if not k:
        for k2 in idx:
            if norm(name) in k2 or k2 in norm(name):
                k = idx[k2]; break
    if not k:
        print("  ✗ KB에 없음:", name); continue
    d[k].update(meta)
    applied.append((k, meta["status"]))

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print("verified_kb 반영:", applied)

# mirror into consulting_db (school-level)
cdb = json.load(open(CDB, encoding="utf-8"))
n = 0
for name, s in cdb["schools"].items():
    for nm, meta in FINDINGS.items():
        if norm(nm) == norm(name) or norm(nm) in norm(name):
            s["status"] = meta["status"]; s["status_note"] = meta["status_note"]
            s["recommend_exclude"] = meta["recommend_exclude"]; n += 1
open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
print(f"consulting_db 반영: {n}개교")
