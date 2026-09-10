# -*- coding: utf-8 -*-
"""FIX: remove 한양대 winter-data wrongly injected into 한양여자대학교; add 한양대학교."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]

# 1) Remove ONLY the 4 wrongly-injected fields from 한양여자대학교
hyu_women = lp.get("한양여자대학교", {})
for f in ["tuition_range","period","period_note","verified_winter_2026"]:
    hyu_women.pop(f, None)
print("한양여자대 cleaned. remaining keys:", list(hyu_women.keys()))

# 2) Add 한양대학교 (if not already a proper entry)
if "한양대학교" not in lp or not lp["한양대학교"].get("verified_winter_2026"):
    lp["한양대학교"] = {
        "region": "서울특별시",
        "tuition_range": {"min": 1850000, "max": 1850000},
        "period": "2026 겨울 12.2~2027.2.12, 접수 9.9~10.8, 접수비 15만, 레벨테스트 11.24",
        "period_note": "2026 겨울학기(12월) D-4, 검증 2026-09-10",
        "d4_eligible": True,
        "verified_winter_2026": True,
        "structure": {"per_term": "10주", "total_hours": "200h(10주)"},
        "dorm": True,
    }
print("한양대학교:", lp["한양대학교"]["tuition_range"], "| verified:", lp["한양대학교"]["verified_winter_2026"])

json.dump(kb, open(KB_PATH,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("DONE")
