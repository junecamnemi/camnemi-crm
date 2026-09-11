#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add the 8 previously-unmatched language schools to verified_kb.lang_programs.
Data sourced from OCR of their official 2026 한국어교육원 PDFs (rapidocr)."""
import json, os, shutil

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
shutil.copy(KB, os.path.join(B, "verified_kb_bak_addlang_2026-09-11.json"))

GPDF = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"

new = {
 "국립금오공과대학교": {
   "region": "경상북도",
   "tuition_range": 1100000,
   "tuition_note": "1,100,000원/학기(US$850 상당). 연 4학기(봄·여름·가을·겨울), 학기 200시간. 국제교류교육원. 출처: 2026 한국어연수과정 모집요강(OCR).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "2026 봄 03.03~05.12 / 여름 06.01~08.10 / 가을 09.01~11.13 / 겨울 12.01~2027.02.24 (접수: 2025.12.01~12.19 / 2026.03.03~03.20 / 06.01~06.19 / 09.01~09.21)",
   "guide_pdf": os.path.join(GPDF, "국립금오공과대학교_한국어교육원.pdf"),
   "lang_note": "국제교류교육원. Tel +82-54-478-7216 / namyong@kumoh.ac.kr · 구미. D-4 안내 포함."
 },
 "나사렛대학교": {
   "region": "충청남도",
   "tuition_range": {"min": 1300000, "max": 1900000},
   "tuition_note": "수강료 1,300,000원/학기. (기숙사 등 포함 시 1,900,000원 표기). 재정증명 KRW 10,000,000 이상. 출처: 2026 한국어교육원 모집요강(OCR).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "2026 봄 03.03~05.08 / 여름 06.01~08.07 / 가을 08.31~11.13 / 겨울 11.30~2027.02 (접수 2025.11.03~2026.01.02 / 2026.03.02~04.17 / 2026.07.16 등)",
   "guide_pdf": os.path.join(GPDF, "나사렛대학교_한국어교육원.pdf"),
   "lang_note": "Tel 041-570-1545 / education@kornu.ac.kr · 천안."
 },
 "부산대": {
   "region": "부산광역시",
   "tuition_range": 1500000,
   "tuition_note": "수강료 1,500,000원/학기(장학 전액 면제 기준액). 교내 기숙사 약 150만원/학기, 교외 1인실 약 120만·2인실 약 75만원. 출처: 부산대 언어교육원 한국어강좌 안내(OCR/리플릿).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "2026 봄 03.02~05.08 / 여름 06.01~08.07(추정) / 학기별 상이 — 공식 접수기간 확인 필요",
   "guide_pdf": os.path.join(GPDF, "부산대_한국어교육원.pdf"),
   "lang_note": "언어교육원. Tel +82-51-510-7143 / interedu@pusan.ac.kr · lei.pusan.ac.kr · 금정구."
 },
 "서울시립대": {
   "region": "서울특별시",
   "tuition_range": {"min": 1250000, "max": 1650000},
   "tuition_note": "수강료 1,600,000원(1,650,000원 표기 병존)/학기, 재학생 1,250,000~1,300,000원. 접수료 50,000원. 오전반 09:00~12:50 / 오후반 14:00~17:50, 학기 200시간. 출처: 2026-2027 한국어교육센터 모집요강(OCR).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": "4h"},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "2026-2027 연 4학기(봄/여름/가을/겨울) — 2026 가을 09.08~11.23, 겨울 12.10~2027.02.12 등. 2027 일정도 게시(2027 봄 03.08~05.18).",
   "guide_pdf": os.path.join(GPDF, "서울시립대_한국어교육원.pdf"),
   "lang_note": "한국어교육센터. Tel 02-6490-6670~6673 / uosklcp@uos.ac.kr / klcp.uos.ac.kr · 동대문구."
 },
 "서울신학대": {
   "region": "경기도",
   "tuition_range": None,
   "tuition_note": "PDF가 로그인 화면 캡처로 수강료 미확보. 공식 홈페이지 확인 필요.",
   "structure": {"per_term": None, "total_hours": None, "per_day": None},
   "is_200h_10wk": False, "d4_eligible": None, "dorm": None,
   "period": None,
   "guide_pdf": os.path.join(GPDF, "서울신학대_한국어교육원.pdf"),
   "lang_note": "⚠️ 수집 PDF 불완전(로그인 페이지 캡처). 어학원 요강 재수집 필요. 부천 소재."
 },
 "서일대학교": {
   "region": "서울특별시",
   "tuition_range": 1300000,
   "tuition_note": "수강료 1,300,000원/학기, 접수료 50,000원. 해외 지원자 재정증명 USD 10,000 이상. 최초 지원 시 4학기 일괄 신청(D-4-1 기준). 출처: 2026 한국어교육원 모집요강(OCR).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "연 4학기(봄/여름/가을/겨울) — 최초 4학기 일괄 지원",
   "guide_pdf": os.path.join(GPDF, "서일대학교_한국어교육원.pdf"),
   "lang_note": "Tel 02-490-2013 / korea@seoil.ac.kr · 중랑구."
 },
 "총신대": {
   "region": "서울특별시",
   "tuition_range": {"min": 1740000, "max": 1740000},
   "tuition_note": "학기당 1,740,000원×4학기=6,960,000원(1년). 부대비용 2,700,000원(450,000×6), 기타 150,000원 등 총 9,810,000원 표기. 출처: 2026 한국어교육원 모집요강(OCR).",
   "structure": {"per_term": "10주", "total_hours": "200h", "per_day": None},
   "is_200h_10wk": True, "d4_eligible": True, "dorm": True,
   "period": "2026 봄 03.04~05.15 / 여름 06.08~08.14 / 가을 09.01~11.13 / 겨울 11.30~2027.02 (접수 2025.11.28~ / 2026.03.20 / 06.05 / 06.20~08.31 등)",
   "guide_pdf": os.path.join(GPDF, "총신대_한국어교육원.pdf"),
   "lang_note": "Tel 02-3479-0612,0622 / korean@csu.ac.kr · 동작구."
 },
 "한성대학교": {
   "region": "서울특별시",
   "tuition_range": None,
   "tuition_note": "PDF가 2025학년도 기준 캡처로 2026 수강료 미확보. 재정증명 KRW 10,000,000 표기. 공식 확인 필요.",
   "structure": {"per_term": None, "total_hours": None, "per_day": None},
   "is_200h_10wk": False, "d4_eligible": None, "dorm": None,
   "period": "⚠️ 수집 PDF는 2025학년도 일정(2025 봄 03.03~05.09 등) — 2026 요강 미확보",
   "guide_pdf": os.path.join(GPDF, "한성대학교_한국어교육원.pdf"),
   "lang_note": "Tel 02-760-4374,5592 / klp4374@hansung.ac.kr · 성북구. 요강 재수집 필요."
 },
}

kb = json.load(open(KB, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]
added = []
for k, v in new.items():
    lp[k] = v
    added.append(k)
kb["lang_programs"]["updated"] = "2026-09-11 (매칭실패 8개교 어학 추가: 금오공대·나사렛·부산대·서울시립대·서울신학대·서일대·총신대·한성대)"
json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("추가:", added)
print("lang_programs 총:", len(lp))
