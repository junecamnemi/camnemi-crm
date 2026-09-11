# -*- coding: utf-8 -*-
"""Flag visa-restricted (비자정밀심사) schools in KB per official 2026.2.12 press release.
Restriction = 2026 2학기부터 1년간 신입생 비자 발급 원칙 제한."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
db_path = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"

# (school, scope) — scope: 'degree' = 학위과정, 'lang' = 어학연수과정
restricted = {
    "금강대학교": "degree",
    "수원가톨릭대학교": "degree",
    "중앙승가대학교": "degree",
    "협성대학교": "degree",
    "부산경상대학교": "degree",
    "부산예술대학교": "degree",
    "한영대학교": "degree",
    "대구한의대학교": "lang",   # 어학연수과정만 제한
    "상지대학교": "lang",
    "호원대학교": "lang",
    "목포과학대학교": "lang",
}
SOURCE = "교육부·법무부·한국연구재단 공동보도 2026.2.12 (2026 2학기~1년)"

kb = json.load(open(KB_PATH, encoding="utf-8"))
flagged = 0
for sec, schools in [("BA", kb["schools"]), ("MA", kb["master"]["schools"]),
                     ("junior", kb["junior"]["schools"]), ("lang", kb["lang_programs"]["schools"])]:
    for n, v in schools.items():
        if n in restricted:
            scope = restricted[n]
            # only flag if the scope matches this section
            if scope == "lang" and sec != "lang":
                continue
            v["visa_restricted_2026"] = True
            v["visa_restricted_scope"] = scope
            v["visa_restricted_note"] = f"비자 정밀심사 대학({scope}과정) — 2026-2학기부터 1년간 신입생 비자 발급 원칙 제한. {SOURCE}"
            flagged += 1

json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"KB 비자제한 플래그: {flagged}개 항목")

# also mirror into consulting_db
db = json.load(open(db_path, encoding="utf-8"))
cf = 0
for n, s in db["schools"].items():
    if n in restricted:
        scope = restricted[n]
        if scope == "degree":
            s["visa_restricted_2026"] = True
            cf += 1
        else:
            if "어학연수" in s.get("programs", {}):
                s["visa_restricted_2026_lang"] = True
                cf += 1
json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"consulting DB 플래그: {cf}개")
