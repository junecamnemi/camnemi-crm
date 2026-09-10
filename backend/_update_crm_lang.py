#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update consulting_db.json with this session's verified D-4 어학연수 data.
Backs up first. Adds/updates programs.어학연수 for each confirmed school."""
import json, os, shutil, datetime

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"

# backup
bak = DB.replace(".json", f"_bak_{datetime.date.today().isoformat()}.json")
shutil.copy(DB, bak)
print("백업:", bak)

cdb = json.load(open(DB, encoding="utf-8"))
sch = cdb["schools"]

# Session-verified D-4 Korean language program data
updates = {
  "인천대학교": {"tuition": {"min": None, "max": None},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~12:50)"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울: 2026.12.07~2027.02.17 (접수 8.31~10.2)",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\인천대학교_한국어교육원.pdf"},
  "부천대학교": {"tuition": {"min": 1300000, "max": 1300000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울: 2026.12.07~2027.02.12 (접수 9.7~11.13). 학비 130만/학기",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\부천대학교_한국어교육원.pdf"},
  "경인여자대학교": {"tuition": {"min": 1100000, "max": 1100000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울(4학기): 2026.12.07~2027.02.24. 학비 110만/학기(1년 4학기 선납 440만), 전형료 5만",
    "guide_pdf": "https://www.kiwu.ac.kr (국제교류원 032-540-0402)"},
  "가톨릭대학교": {"tuition": {"min": 1500000, "max": 1500000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울: 12.07~2027.02.18(접수 8.1~9.23). 2027 봄: 3.08~5.14(접수 11.1~12.24). 2027 여름: 6.07~8.13(접수 2.1~3.26). 학비 150만/학기",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2027_어학연수_모집요강\\가톨릭대_한국어교육원_2027.pdf"},
  "이화여자대학교": {"tuition": {"min": 1800000, "max": 1850000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:10~13:00)"},
    "d4_eligible": True, "dorm": True,
    "period": "2027 봄 3.05~5.18(접수 12.7~1.26)/여름 6.03~8.12(3.8~4.27)/가을 9.02~11.17(6.7~7.27)/겨울 12.02~2028.2.15(9.6~10.26)",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2027_어학연수_모집요강\\이화여자대학교_한국어교육원_2027.pdf"},
  "동의대학교": {"tuition": {"min": 1200000, "max": 1200000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~12:40)"},
    "d4_eligible": True, "dorm": False,
    "period": "2026 겨울: 11.16~2027.01.22. 봄 접수(12~1월). 학비 240만/2학기(1학기 120만)",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\동의대_한국어교육원.pdf"},
  "인하대학교": {"tuition": {"min": 1400000, "max": 1400000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "d4_eligible": True, "dorm": False,
    "period": "겨울학기 12월~2월. 학비 140만/학기(2024.9 인상), 원서비 10만. 해외 지원 접수 ~9~11월",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\인하대_한국어교육원.pdf"},
  "서강대학교": {"tuition": {"min": 1860000, "max": 1860000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~13:00)"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울(KGP200): 12.03~2027.02.22(접수 9.10~10.22). 학비 186만/학기(입학금 10만)",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2027_어학연수_모집요강\\서강대_한국어교육원_참고캡처_2026겨울포함.pdf"},
}

changed_new = []
changed_update = []
for school, langdata in updates.items():
    if school not in sch:
        print(f"  ⚠ {school}: CRM DB에 없음 - skip")
        continue
    progs = sch[school].setdefault("programs", {})
    existed = "어학연수" in progs
    progs["어학연수"] = langdata
    if existed:
        changed_update.append(school)
    else:
        changed_new.append(school)

cdb["meta"]["updated"] = "2026-09-08 (D-4 어학연수 8개교 갱신/추가)"
json.dump(cdb, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n신규 추가 어학연수: {len(changed_new)}개")
for s in changed_new: print("  +", s)
print(f"\n기존 어학연수 갱신: {len(changed_update)}개")
for s in changed_update: print("  ~", s)
print("\n저장 완료:", DB)
