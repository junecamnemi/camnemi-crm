#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add D-4 어학연수 for additional session-researched schools (SEOUL W, DUKSUNG, JAENEUNG, etc.)
Only data verified from official pages/PDFs this session."""
import json, os, shutil, datetime

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
bak = DB.replace(".json", f"_bak2_{datetime.date.today().isoformat()}.json")
shutil.copy(DB, bak)
print("백업:", bak)

cdb = json.load(open(DB, encoding="utf-8"))
sch = cdb["schools"]

updates = {
  # 서울여자대: 정규과정 150만/학기, 2026겨울 12.7~2.18, 캄보디아 수용 (공식 klc.swu.ac.kr)
  "서울여자대학교": {"tuition": {"min": 1500000, "max": 1500000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~13:00)"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울: 12.07~2027.02.18(마감 9.30). 학비 150만/학기, 원서비 8.5만. 캄보디아 수용(21개 지정국 아님)",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\서울여자대_한국어교육원.pdf",
    "lang_note": "캄보디아 BacII 졸업증·성적증 아포스티유 인정, 신원보증서 불필요"},
  # 덕성여자대: 2학기 300만(1학기150만), 겨울 11.30~2.5, 캄보디아 수용 (공식 dilc.ds.ac.kr)
  "덕성여자대학교": {"tuition": {"min": 1500000, "max": 1500000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "d4_eligible": True, "dorm": True,
    "period": "2026 겨울: 11.30~2027.02.05(마감 10.16). 학비 300만/2학기(전형료 10만). 캄보디아 수용. 은행잔고 $10,000+ 6개월 경과",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\덕성여자대_한국어교육원.pdf",
    "lang_note": "여대지만 어학연수는 남녀 모두 수용(남성 기숙사 있음). 캄보디아 21개 지정국 아님"},
  # 재능대(송도, 인천): D-4 한국어연수 운영 확인 (032-890-7751). 일정 미게시
  "재능대학교": {"tuition": {"min": None, "max": None},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
    "d4_eligible": True, "dorm": False,
    "period": "D-4 한국어연수 운영 확인(송도글로벌캠퍼스). 2026 겨울 일정 미게시 - 국제교류협력센터 032-890-7751 문의",
    "guide_pdf": "https://apply.jeiu.ac.kr (국제교류협력센터 032-890-7751)"},
  # 삼육대(서울 노원): 학비 78만~137만 (남양주 인접)
  "삼육대학교": {"tuition": {"min": 782000, "max": 1378000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
    "d4_eligible": True, "dorm": True,
    "period": "남양주 인접(서울 노원). 학비 78만~137만/학기. 캄보디아 수용 확인 필요",
    "guide_pdf": "C:\\Users\\USER\\내 드라이브\\02_Crawling_Sheet\\University_Project\\adiga_2026_어학연수_모집요강\\삼육대_한국어교육원.pdf"},
}

changed_new, changed_update = [], []
for school, langdata in updates.items():
    if school not in sch:
        print(f"  ⚠ {school}: CRM에 없음"); continue
    progs = sch[school].setdefault("programs", {})
    existed = "어학연수" in progs
    progs["어학연수"] = langdata
    (changed_update if existed else changed_new).append(school)

cdb["meta"]["updated"] = "2026-09-08 (D-4 어학연수 추가: 서울여대·덕성여대·재능대·삼육대)"
json.dump(cdb, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("신규 추가:", changed_new)
print("기존 갱신:", changed_update if changed_update else "(없음)")
print("저장 완료")
