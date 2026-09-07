#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add to verified_kb.json:
1. fee_structure per school: app_fee(지원비/전형료) + admission_fee(입학금) + semester(학기 등록금)
2. scholarship categorization: enroll/existing × academic/language
   (merging _scholarship_categorized.json into each school's scholarships)
"""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")
SCH_CAT = os.path.join(BASE, "_scholarship_categorized.json")
FEES = os.path.join(BASE, "_fees_extracted.json")

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)
with open(SCH_CAT, encoding="utf-8") as f:
    sch_cat = json.load(f)
with open(FEES, encoding="utf-8") as f:
    fees = json.load(f)

# 1. fee structure
fee_notes = {}
for name, info in fees.items():
    ap = info.get("app_fee") or []
    ad = info.get("admission_fee") or []
    app_amt = ap[0][0] if ap else None
    adm_amt = ad[0][0] if ad else None
    adm_note = ""
    if ap and len(ap) > 0 and len(ap[0]) > 1:
        adm_note = ap[0][1]
    fee_notes[name] = {
        "app_fee": app_amt,  # 지원비/전형료 (KRW)
        "admission_fee": adm_amt,  # 입학금 (KRW); '0' = 면제, None = 미확인
        "note": (ad[0][1] if ad and len(ad[0]) > 1 else "") or "",
    }

# 2. merge into KB schools (match by name)
def apply_fee(school_name, entry):
    if school_name in kb["schools"]:
        s = kb["schools"][school_name]
    elif school_name in kb.get("master", {}).get("schools", {}):
        s = kb["master"]["schools"][school_name]
    elif school_name in kb.get("junior", {}).get("schools", {}):
        s = kb["junior"]["schools"][school_name]
    else:
        return False
    s["fee_structure"] = entry
    return True

# add fee structure
n_fee = 0
for name, entry in fee_notes.items():
    if apply_fee(name, entry):
        n_fee += 1

# 3. add categorized scholarships to KB schools
n_sch = 0
for school_name, schs in sch_cat.items():
    # find the school in KB (ba or master)
    target = None
    if school_name in kb["schools"]:
        target = kb["schools"][school_name]
    elif school_name in kb.get("master", {}).get("schools", {}):
        target = kb["master"]["schools"][school_name]
    if target is None:
        continue
    # store categorized scholarships
    target["scholarships_categorized"] = schs
    n_sch += 1

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"등록금 구조(지원비/입학금) 반영: {n_fee}개 학교")
print(f"장학금 분류 반영: {n_sch}개 학교")

# show sample
print("\n=== 샘플: 인하대 ===\n")
s = kb["schools"].get("인하대학교", {})
print("fee_structure:", json.dumps(s.get("fee_structure", {}), ensure_ascii=False))
sc = s.get("scholarships_categorized", [])
print(f"장학금 {len(sc)}개:")
for x in sc[:4]:
    print(f"  [{x.get('type')}/{x.get('category')}] {x.get('name','')[:40]}")
