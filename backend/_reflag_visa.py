# -*- coding: utf-8 -*-
"""Revert bad greedy flags, then re-flag using EXACT normalized equality only."""
import json, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
DB_PATH = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
SOURCE = "교육부·법무부·한국연구재단 공동보도 2026.2.12 (2026 2학기~1년)"

degree_restricted = ["금강대학교","수원가톨릭대학교","중앙승가대학교","협성대학교","부산경상대학교","부산예술대학교","한영대학교","구세군사관대학원대학교","국제법률경영대학원대학교","능인대학원대학교","성서침례대학원대학교","순복음대학원대학교","에스라성경대학원대학교","치유상담대학원대학교","한국상담대학원대학교","합동신학대학원대학교"]
# NOTE: 한영대학교 = 한영대학교(junior). 서울한영대학교 is a DIFFERENT school → exclude.
lang_restricted = ["대구한의대학교","상지대학교","호원대학교","목포과학대학교"]

def norm(s):
    s = re.sub(r"\[.*?\]","",s)
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if s.endswith(suf):
            s = s[:-len(suf)]; break
    if s.endswith("대") and len(s)>1: s = s[:-1]
    return s.replace(" ","")

# exact set of normalized names to flag (degree / lang)
d_set = {norm(x) for x in degree_restricted}
l_set = {norm(x) for x in lang_restricted}

# 서울한영대학교 must NOT match 한영대학교; both normalize to '한영'?? check
print("norm 한영대학교:", norm("한영대학교"), "| norm 서울한영대학교:", norm("서울한영대학교"))

kb = json.load(open(KB_PATH, encoding="utf-8"))

# STEP 1: clear ALL prior visa flags
cleared=0
for sec, schools in [("BA", kb["schools"]), ("MA", kb["master"]["schools"]),
                     ("junior", kb["junior"]["schools"]), ("lang", kb["lang_programs"]["schools"])]:
    for n, v in schools.items():
        for f in ["visa_restricted_2026","visa_restricted_scope","visa_restricted_note"]:
            if f in v: v.pop(f); cleared+=1
print("cleared flags:", cleared)

# STEP 2: apply EXACT matches
flagged=[]
for sec, schools in [("BA", kb["schools"]), ("MA", kb["master"]["schools"]),
                     ("junior", kb["junior"]["schools"]), ("lang", kb["lang_programs"]["schools"])]:
    for n, v in schools.items():
        nn = norm(n)
        target = l_set if sec=="lang" else d_set
        if nn in target:
            scope = "lang" if sec=="lang" else "degree"
            v["visa_restricted_2026"]=True
            v["visa_restricted_scope"]=scope
            v["visa_restricted_note"]=f"비자 정밀심사({scope}과정) — 2026-2학기부터 1년간 신입생 비자 발급 원칙 제한. {SOURCE}"
            flagged.append(f"[{sec}] {n}")
print("flagged:", len(flagged))
for f in flagged: print("  ", f)

json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# consulting DB
db = json.load(open(DB_PATH, encoding="utf-8"))
for n,s in db["schools"].items():
    for f in ["visa_restricted_2026","visa_restricted_2026_lang"]:
        s.pop(f, None)
cf=0
for n,s in db["schools"].items():
    nn=norm(n)
    if nn in d_set: s["visa_restricted_2026"]=True; cf+=1
    elif nn in l_set and "어학연수" in s.get("programs",{}): s["visa_restricted_2026_lang"]=True; cf+=1
json.dump(db, open(DB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("consulting DB flagged:", cf)
