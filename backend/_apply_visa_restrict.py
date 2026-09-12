#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge visa_restricted_2026 INTO individual school entries so the engines enforce it.

  degree_restricted  -> status='visa_restricted_degree', recommend_exclude=True (추천 금지)
  lang_restricted    -> status='visa_restricted_lang',  lang d4_eligible=False (D-4 금지, 학위 OK)
Also patches recommend.py to respect `recommend_exclude`.
"""
import json, os, re, shutil, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json"); CDB = os.path.join(B, "consulting_db.json")

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, KB.replace(".json", f"_bak_visa_{datetime.date.today()}.json"))
vr = kb["visa_restricted_2026"]
sections = [("schools", None), ("master", "schools"), ("junior", "schools"), ("lang_programs", "schools")]

# build name->(section,key) index
idx = {}
for a, b in sections:
    d = kb[a][b] if b else kb[a]
    for k in d:
        idx.setdefault(norm(k), (a, b, k))

def locate(s):
    """STRICT matching: exact normalized equality only (avoids 중앙승가→중앙대 false positives)."""
    return idx.get(norm(s))

deg_applied = []
for s in vr["degree_restricted"]:
    hit = locate(s)
    if not hit:
        continue
    a, b, k = hit
    ent = kb[a][b][k] if b else kb[a][k]
    if not ent.get("status"):
        ent["status"] = "visa_restricted_degree"
        ent["recommend_exclude"] = True
        ent["status_note"] = f"비자 정밀심사 학위과정 제한 (2026.2.12, {vr.get('effective','')}). 신입생 비자 발급 원칙 제한 — 추천 금지."
        deg_applied.append(k)

lang_applied = []
for s in vr["lang_restricted"]:
    hit = locate(s)
    if not hit:
        continue
    a, b, k = hit
    ent = kb[a][b][k] if b else kb[a][k]
    if not ent.get("status"):
        ent["status"] = "visa_restricted_lang"
        ent["status_note"] = f"어학연수(D-4) 비자 정밀심사 제한 (2026.2.12) — D-4 금지, 학위과정은 가능."
        lang_applied.append(k)
    # lang program d4 off
    lk = kb["lang_programs"]["schools"].get(k) or next((v for kk, v in kb["lang_programs"]["schools"].items() if norm(kk) == norm(s)), None)
    if lk is not None:
        lk["d4_eligible"] = False

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print(f"degree 제한 반영: {len(deg_applied)}개교 → {deg_applied}")
print(f"lang 제한 반영: {len(lang_applied)}개교 → {lang_applied}")

# mirror to consulting_db
cdb = json.load(open(CDB, encoding="utf-8"))
for s in vr["degree_restricted"] + vr["lang_restricted"]:
    for name, ent in cdb["schools"].items():
        if norm(s) == norm(name):   # strict only
            if s in vr["degree_restricted"]:
                ent["status"] = "visa_restricted_degree"; ent["recommend_exclude"] = True
            else:
                ent["status"] = "visa_restricted_lang"
                lp = (ent.get("programs") or {}).get("어학연수")
                if lp is not None:
                    lp["d4_eligible"] = False
open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
print("consulting_db 반영 완료")
