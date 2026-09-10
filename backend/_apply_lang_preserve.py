#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply session D-4 lang updates onto ORIGINAL consulting_db.json targeting the
abbrev lang-only keys (인하대, 서울여자대, ...) — matching verified_kb.lang_programs
keying. Preserves all enriched fields on other programs. Backs up first."""
import json, os, shutil, datetime

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
bak = DB.replace(".json", f"_bak_lang_{datetime.date.today().isoformat()}.json")
shutil.copy(DB, bak)
print("백업:", bak)

cdb = json.load(open(DB, encoding="utf-8"))
sch = cdb["schools"]
lang_only = {k for k, v in sch.items() if set(v.get('programs', {}).keys()) == {'어학연수'}}
print("기존 어학전용 키:", len(lang_only))

# abbrev lang-key -> session lang data
updates = {
  "가톨릭대": {"region":"경기도","tuition":{"min":1500000,"max":1500000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울: 12.07~2027.02.18(접수 8.1~9.23). 2027 봄: 3.08~5.14(접수 11.1~12.24). 2027 여름: 6.07~8.13(접수 2.1~3.26). 학비 150만/학기(부천)",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강\가톨릭대_한국어교육원_2027.pdf"},
  "이화여자대학교": {"region":"서울특별시","tuition":{"min":1800000,"max":1850000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h(09:10~13:00)"},
    "d4_eligible":True,"dorm":True,
    "period":"2027 봄 3.05~5.18(접수 12.7~1.26)/여름 6.03~8.12(3.8~4.27)/가을 9.02~11.17(6.7~7.27)/겨울 12.02~2028.2.15(9.6~10.26)",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강\이화여자대학교_한국어교육원_2027.pdf"},
  "서울여자대": {"region":"서울특별시","tuition":{"min":1500000,"max":1500000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h(09:00~13:00)"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울: 12.07~2027.02.18(접수마감 9.30). 2027 봄 3.8~5.18(마감 12.31). 학비 150만/학기",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\서울여자대_한국어교육원.pdf"},
  "덕성여자대": {"region":"서울특별시","tuition":{"min":1500000,"max":1500000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울: 11.30~2027.02.05(마감 10.16). 2027 봄 3.8~5.18(마감 12.31). 학비 300만/2학기, 전형료 10만",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\덕성여자대_한국어교육원.pdf"},
  "동의대": {"region":"부산광역시","tuition":{"min":1200000,"max":1200000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":False,
    "period":"2026 겨울: 11.16~2027.01.22. 2027봄 2차 접수 12.22~1.9 예정. 학비 240만/2학기",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\동의대_한국어교육원.pdf"},
  "부천대학교": {"region":"경기도","tuition":{"min":1300000,"max":1300000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울: 12.07~2027.02.12(접수 9.7~11.13). 학비 130만/학기",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\부천대학교_한국어교육원.pdf"},
  "인천대학교": {"region":"인천광역시","tuition":{"min":None,"max":None},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h(09:00~12:50)"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울: 12.07~2027.02.17(접수 8.31~10.2). 1년 4학기 10주",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\인천대학교_한국어교육원.pdf"},
  "인하대": {"region":"인천광역시","tuition":{"min":1400000,"max":1400000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":False,
    "period":"겨울학기 12월~2월. 해외지원 접수 ~9~11월. 학비 140만/학기",
    "guide_pdf": r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\인하대_한국어교육원.pdf"},
  "경인여자대학교": {"region":"인천광역시","tuition":{"min":1100000,"max":1100000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h(09:00~12:50)"},
    "d4_eligible":True,"dorm":True,
    "period":"2026 겨울(4학기): 12.07~2027.02.24. 학비 110만/학기(1년4학기 선납440만). ⚠️여대 어학당 남녀확인",
    "guide_pdf": "https://www.kiwu.ac.kr (국제교류원 032-540-0402~4)"},
  "경복대": {"region":"경기도","tuition":{"min":1100000,"max":1300000},
    "structure":{"per_term":"10주","total_hours":"200h","per_day":"4h"},
    "d4_eligible":True,"dorm":True,
    "period":"연 8학기. ⚠️캄보디아 D-4 미수용. 남양주/서울 130만, 포천 110만/학기",
    "guide_pdf": "https://eng.kbu.ac.kr (국제어학원 031-570-9882)"},
}

applied_new, applied_upd = [], []
for langkey, langdata in updates.items():
    # lang key target = abbrev (or existing full)
    # find existing key: exact, or a lang-only key that is an abbrev of it
    key = langkey
    if langkey not in sch:
        # try abbrev match among lang_only
        cand = [k for k in lang_only if langkey.replace('대학교','') == k.replace('대학교','').replace('대학','')]
        key = cand[0] if cand else langkey
    # if key doesn't exist as standalone lang, but a full degree school exists, create standalone? 
    # Design: lang lives under abbrev key. Create it if absent (as lang-only record)
    rec = sch.get(key)
    if rec is None:
        rec = {"name": key, "region": langdata.get("region"), "rank": None, "programs": {}}
        sch[key] = rec
        applied_new.append(key)
        progs = rec["programs"]
        progs["어학연수"] = langdata
    else:
        progs = rec.setdefault("programs", {})
        existed = "어학연수" in progs
        progs["어학연수"] = langdata
        (applied_upd if existed else applied_new).append(f"{key}({'기존'+key if existed else '신규'})")

cdb["meta"]["updated"] = "2026-09-08 (D-4 어학연수 세션 데이터, 기존 어학키에 반영)"
json.dump(cdb, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("신규 추가:", [x for x in applied_new if isinstance(x,str)])
print("기존 갱신:", applied_upd)
d2=json.load(open(DB,encoding='utf-8'))
pm=sum(1 for s in d2['schools'].values() for p in s.get('programs',{}).values() if p.get('popular_majors'))
print(f"\n보존 확인 — popular_majors 보유: {pm} | 총 학교: {len(d2['schools'])}")
