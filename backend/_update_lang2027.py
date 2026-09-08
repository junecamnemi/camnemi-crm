#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update lang_programs with CONFIRMED 2027 language guides only.
CONFIRMED (verified 2026-09-08 from downloaded PDFs):
  - 가톨릭대: real 2027 모집요강 PDF (2027 봄/여름 일정)
  - 이화여대: full 2027 학사일정 PDF (봄~겨울 2027 + 접수기간)
NOT confirmed (do NOT mark 2027):
  - 서강대: PDF mentions 2027 but live page only shows 2026겨울 -> leave as-is (2026)
  - 연세대: no 2027 schedule captured
"""
import json, os
KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
D2027 = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강"

kb = json.load(open(KB, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]

# tuition verified from 가톨릭 PDF (1,500,000/학기 was in older data too) and 이화 schedule
updates = {
  "가톨릭대": {
    "guide_2027": True,
    "guide_pdf_2027": os.path.join(D2027, "가톨릭대_한국어교육원_2027.pdf"),
    "year2027": {
      "spring_class": "2027.03.08~2027.05.14",
      "summer_class": "2027.06.07~2027.08.13",
      "note": "2027 모집요강 PDF 기준 (2026 겨울 접수 후 2027 봄/여름)",
    },
    "tuition_range": {"min": 1500000, "max": 1500000},
    "tuition_note": "수강료 1,500,000원/학기 (전형료 80,000원) — 2027 모집요강",
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "is_200h_10wk": True,
    "d4_eligible": True,
    "dorm": True,
    "period_2027": "2027 봄: 접수 2026.12 / 2027 여름: 접수 2027.3~4",
  },
  "이화여자대학교": {
    "guide_2027": True,
    "guide_pdf_2027": os.path.join(D2027, "이화여자대학교_한국어교육원_2027.pdf"),
    "year2027": {
      "spring": {"class": "2027.03.05~05.18", "apply": "2026.12.07~2027.01.26"},
      "summer": {"class": "2027.06.03~08.12", "apply": "2027.03.08~04.27"},
      "fall": {"class": "2027.09.02~11.17", "apply": "2027.06.07~07.27"},
      "winter": {"class": "2027.12.02~2028.02.15", "apply": "2027.09.06~10.26"},
    },
    "tuition_range": {"min": 1800000, "max": 1850000},
    "tuition_note": "수강료 학기당 약 180~185만원 — 2027 학사일정",
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "is_200h_10wk": True,
    "d4_eligible": True,
    "dorm": True,
    "period_2027": "봄 접수 12.7~1.26 / 여름 3.8~4.27 / 가을 6.7~7.27 / 겨울 9.6~10.26",
  },
}

changed = []
for key, upd in updates.items():
    for k in lp:
        if key in k:
            for fk, fv in upd.items():
                lp[k][fk] = fv
            changed.append(k)
            break

kb["lang_programs"]["updated"] = "2026-09-08 (가톨릭대·이화여대 2027 어학연수 요강 확정 반영; 서강대·연세대는 2027 미확정 유지)"
json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("2027 확정 반영 학교:", changed)
print("저장 완료:", KB)
