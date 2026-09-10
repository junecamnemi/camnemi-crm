#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add 재능대(송도) + 경인여대 lang where the standalone lang key is absent.
재능대학교 has 전문학사 only; its D-4 lang should live under abbrev '재능대' lang key
(consistent with the 85 lang-only abbrev key design)."""
import json, os

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
d = json.load(open(DB, encoding="utf-8"))
sch = d["schools"]

# 재능대(송도) lang — under abbrev key 재능대 (standalone lang, like other lang-only keys)
jei_lang = {
    "region": "인천광역시",
    "tuition": None,
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
    "d4_eligible": True, "dorm": False,
    "period": "D-4 한국어연수 운영(송도글로벌캠퍼스). 2026 겨울 일정 미게시 - 국제교류협력센터 032-890-7751",
    "guide_pdf": "https://apply.jeiu.ac.kr (032-890-7751)",
}
if "재능대" not in sch:
    sch["재능대"] = {"name": "재능대학교", "region": "인천광역시", "rank": None,
                     "programs": {"어학연수": jei_lang}}
    print("재능대 lang 키 생성")
else:
    sch["재능대"].setdefault("programs", {})["어학연수"] = jei_lang
    print("재능대 lang 갱신")

json.dump(d, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# verify
d2=json.load(open(DB,encoding='utf-8'))
print("재능대어학:", list(d2['schools'].get('재능대',{}).get('programs',{}).keys()))
pm=sum(1 for s in d2['schools'].values() for p in s.get('programs',{}).values() if p.get('popular_majors'))
print(f"popular_majors 보유: {pm} | 총 학교: {len(d2['schools'])}")
