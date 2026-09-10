#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update verified_kb.json lang_programs.schools with this session's CONFIRMED D-4 data.
Source of truth is verified_kb; consulting_db is regenerated afterward by _build_consulting_db.py.
Backup first."""
import json, os, shutil, datetime

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
bak = KB.replace(".json", f"_lang_bak_{datetime.date.today().isoformat()}.json")
shutil.copy(KB, bak)
print("백업:", bak)

kb = json.load(open(KB, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]

D26 = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
D27 = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강"

# Updates keyed by the verified_kb lang_programs key name
updates = {
  # 가톨릭대(부천): 2027 봄/여름 + 2026겨울 확정 (공식 kli.catholic.ac.kr)
  "가톨릭대": {"period": "2026 겨울: 12.07~2027.02.18(접수 8.1~9.23). 2027 봄: 3.08~5.14(접수 11.1~12.24). 2027 여름: 6.07~8.13(접수 2.1~3.26)",
    "guide_pdf": os.path.join(D27, "가톨릭대_한국어교육원_2027.pdf")},
  # 이화여자대: 2027 4학기 확정
  "이화여자대학교": {"period": "2027 봄 3.05~5.18(접수 12.7~1.26)/여름 6.03~8.12(3.8~4.27)/가을 9.02~11.17(6.7~7.27)/겨울 12.02~2028.2.15(9.6~10.26)",
    "guide_pdf": os.path.join(D27, "이화여자대학교_한국어교육원_2027.pdf")},
  # 서울여자대: 겨울 12.7~2.18 확정
  "서울여자대": {"period": "2026 겨울: 12.07~2027.02.18(접수마감 9.30). 2027 봄 3.8~5.18(마감 12.31)",
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~13:00)"}},
  # 덕성여자대: 150만/학기, 겨울 11.30~2.5 확정
  "덕성여자대": {"tuition_range": {"min": 1500000, "max": 1500000},
    "tuition_note": "수강료 300만/2학기(=150만/학기, 문화수업비포함), 전형료 10만 — 덕성여대 글로벌교육원",
    "period": "2026 겨울: 11.30~2027.02.05(마감 10.16). 2027 봄 3.8~5.18(마감 12.31)",
    "is_200h_10wk": True},
  # 동의대: d4=True 수정, 120만/학기, 겨울 11.16~1.22
  "동의대": {"d4_eligible": True,
    "tuition_range": {"min": 1200000, "max": 1200000},
    "tuition_note": "수강료 240만/2학기(=120만/학기, 문화비포함), 전형료 5만. 서류+면접, 우편·방문만",
    "period": "2026 겨울: 11.16~2027.01.22. 2027봄 2차 접수 12.22~1.9 예정",
    "is_200h_10wk": True},
  # 부천대: 130만/학기, 겨울 12.7~2.12
  "부천대학교": {"tuition_range": {"min": 1300000, "max": 1300000},
    "tuition_note": "수강료 130만/학기, 전형료 5만, 보험 10만(D-4) — 부천대 국제교류원",
    "period": "2026 겨울: 12.07~2027.02.12(접수 9.7~11.13)",
    "is_200h_10wk": True},
  # 인천대: 겨울 12.7~2.17, dorm True
  "인천대학교": {"period": "2026 겨울: 12.07~2027.02.17(접수 8.31~10.2). 1년 4학기 10주",
    "dorm": True,
    "is_200h_10wk": True},
  # 인하대: 140만/학기, 겨울 12월~2월
  "인하대": {"tuition_range": {"min": 1400000, "max": 1400000},
    "tuition_note": "수강료 140만/학기(2024.9 인상), 원서비 10만 — 인하대 어학당",
    "period": "겨울학기 12월~2월. 해외지원 접수 ~9~11월",
    "is_200h_10wk": True},
  # 경인여대: 신규 (인천 계양구) — D-4 한국어과정
  "경인여자대학교": {"region": "인천광역시",
    "tuition_range": {"min": 1100000, "max": 1100000},
    "tuition_note": "학비 110만/학기(1년 4학기 선납 440만), 전형료 5만, 보험 7만 — 경인여대 국제교류원",
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h(09:00~12:50)"},
    "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
    "period": "2026 겨울(4학기): 12.07~2027.02.24. ⚠️여대, 어학당 남녀수용 확인 필요",
    "guide_pdf": "https://www.kiwu.ac.kr (국제교류원 032-540-0402~4)"},
  # 재능대(송도): 신규 (인천 연수구)
  "재능대학교": {"region": "인천광역시",
    "tuition_range": None,
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
    "is_200h_10wk": True, "d4_eligible": True, "dorm": False,
    "period": "D-4 한국어연수 운영(송도글로벌캠퍼스). 2026 겨울 일정 미게시 - 국제교류협력센터 032-890-7751",
    "guide_pdf": "https://apply.jeiu.ac.kr (032-890-7751)"},
  # 경복대: 신규 — 캄보디아 D-4 미수용 기록 (남양주/서울 130만, 포천 110만 per 공식)
  "경복대": {"region": "경기도",
    "tuition_range": {"min": 1100000, "max": 1300000},
    "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
    "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
    "period": "연 8학기(남양주/서울/포천). ⚠️캄보디아 D-4 어학연수 미수용",
    "lang_note": "캄보디아 미수용(경복대 D-4). 남양주/서울캠 130만/학기, 포천 110만. 국제어학원 031-570-9882",
    "guide_pdf": "https://eng.kbu.ac.kr (국제어학원)"},
}

changed=[]
for key, upd in updates.items():
    if key not in lp:
        # new key
        lp[key] = {"region": "?", "tuition_range": None, "tuition_note": "",
                   "structure": {"per_term": "10주","total_hours":"200h","per_day":None},
                   "is_200h_10wk": True, "d4_eligible": True, "dorm": False,
                   "period": None, "guide_pdf": ""}
        lp[key].update(upd)
        changed.append(f"+{key}(신규)")
    else:
        for fk,fv in upd.items():
            lp[key][fk]=fv
        changed.append(f"~{key}(갱신)")

kb["lang_programs"]["updated"] = "2026-09-08 (D-4 어학연수: 가톨릭/이화 2027 + 인천·부천·서울여대·덕성·동의·인하·경인여대·재능·경복)"
json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("변경:", changed)
print("lang_programs.schools 수:", len(lp))
print("저장:", KB)
