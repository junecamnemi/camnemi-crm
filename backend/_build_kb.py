#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a consolidated knowledge base (verified_kb.json) merging:
- verified English-track / Korean-track schools (from this session's research)
- tuition (per semester)
- scholarships split into 입학/재학
- application periods
- guide year + track
This lets future queries answer instantly without re-researching PDFs."""
import json
import re
import os

BASE = r"C:\Users\USER\camnemi-crm\backend"
DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

# --- load data.js ---
with open(DATA_FILE, encoding="utf-8") as f:
    content = f.read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            data = json.loads(content[start:i + 1])
            break
data_by_name = {u.get("n", ""): u for u in data}

# --- load verified analyses ---
with open(os.path.join(BASE, "_scholarship_parsed.json"), encoding="utf-8") as f:
    SCH = json.load(f)
with open(os.path.join(BASE, "_tuition_final.json"), encoding="utf-8") as f:
    TUITION = json.load(f)
with open(os.path.join(BASE, "recommend_ultimate.csv"), encoding="utf-8") as f:
    ult_lines = f.read().strip().splitlines()

# --- English-track school list (from our PDF research) ---
# school -> {loc, rank, majors_eng, lang, period, year}
ENGLISH_TRACK = {
    "중앙대학교": {"loc": "서울", "rank": "#8", "majors_eng": "게임융합학과 (100% 영어수업) / 융합공학부", "lang": "IELTS 5.5 / TOEFL iBT 60", "period": "2026.8.31~9.18", "year": "2027"},
    "인하대학교": {"loc": "인천", "rank": "#12", "majors_eng": "IBT학과 / ISE학과 / 글로벌자유전공학부", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2026.9.30~11.5", "year": "2027"},
    "숙명여자대학교": {"loc": "서울", "rank": "#20", "majors_eng": "글로벌서비스학부 / 영어영문학부", "lang": "IELTS 5.5(영어트랙)", "period": "1차 10.7~16 / 2차 11.6~20 / 3차 12.3~18", "year": "2027"},
    "가천대학교": {"loc": "경기", "rank": "#25", "majors_eng": "경영학과(ENG) / 컴퓨터공학과(ENG) / 반도체공학과(ENG) / 시스템반도체학과(ENG)", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2026.10.12~10.23", "year": "2027"},
    "광운대학교": {"loc": "서울", "rank": "-", "majors_eng": "반도체시스템공학부(영어트랙만) / 정보융합학부 데이터사이언스전공 / 로봇학부 AI로봇 / 소프트웨어학부 / 국제통상학부 / 빅데이터경영", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2027-1", "year": "2027"},
    "한양대학교(ERICA)": {"loc": "경기(안산)", "rank": "-", "majors_eng": "컴퓨터학부(영어트랙) / ICT융합학부 / 인공지능학과 / 수리데이터사이언스학과 / 경제·경영학부(영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2027-1", "year": "2027"},
    "한경국립대학교": {"loc": "경기(안성)", "rank": "-", "majors_eng": "글로벌경영전공 / English Language", "lang": "IELTS 5.5 / TOEFL iBT", "period": "2027", "year": "2027"},
    "단국대학교": {"loc": "경기", "rank": "-", "majors_eng": "국제경영학과 / 모바일시스템공학과 / 바이오소재융합공학과 / 한국학과", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "1차 10.1~16 / 2차 12.2~18", "year": "2027"},
    "계명대학교": {"loc": "대구", "rank": "-", "majors_eng": "Keimyung Adams College(5.5) / 디지펜게임공학과(5.0!)", "lang": "IELTS 5.0~5.5 / TOEFL iBT 61~80", "period": "2026.9.21~10.23", "year": "2027", "note": "디지펜게임공학과는 IELTS 5.0 허용"},
    "전북대학교": {"loc": "전북(전주)", "rank": "-", "majors_eng": "국제이공학부(엔지니어링사이언스) 4년 영어강의 / 국제학부(국제협력)", "lang": "IELTS 5.5 / TEPS 600", "period": "2026 전기: 1차 9.22~10.3 / 2차 11.5~19", "year": "2027"},
    "목원대학교": {"loc": "대전", "rank": "-", "majors_eng": "글로벌융합학부: 글로벌IT공학 / 글로벌경제·개발협력", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "1차 9.16~10.7 / 2차 11.23~12.23", "year": "2027"},
    "배재대학교": {"loc": "대전", "rank": "-", "majors_eng": "글로벌융합학부: 글로벌경영 / 글로벌IT", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2026.10.16~10.22", "year": "2027"},
    "우송대학교": {"loc": "대전", "rank": "-", "majors_eng": "솔브릿지경영학부 / AI·빅데이터학과 / 글로벌철도학과 / 글로벌미디어AI영상학과 / 글로벌호텔관광 (100% 영어)", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2026.7.16~", "year": "2027"},
    "을지대학교": {"loc": "대전", "rank": "-", "majors_eng": "글로벌빅데이터AI학과 (외국인 전담 영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2026.9.7~9.11", "year": "2027"},
    "인제대학교": {"loc": "경남", "rank": "-", "majors_eng": "외국인 전담학과: AI컴퓨터 / 글로벌경영", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2026.9.7~9.11", "year": "2027"},
    "선문대학교": {"loc": "충남", "rank": "-", "majors_eng": "컴퓨터공학부(영어트랙) / 글로벌자유전공학부", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2027", "year": "2027"},
    "한동대학교": {"loc": "경북(포항)", "rank": "-", "majors_eng": "영어강의 학과 (전 과정)", "lang": "IELTS 5.5 / TOEFL iBT 85", "period": "2027", "year": "2027"},
    "고신대학교": {"loc": "부산", "rank": "-", "majors_eng": "영어트랙 전학과", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2027", "year": "2027"},
    "동신대학교": {"loc": "전남(나주)", "rank": "-", "majors_eng": "국제학부(글로벌경영·호텔투어리즘·IT)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2027", "year": "2027"},
    "중원대학교": {"loc": "충북", "rank": "-", "majors_eng": "국제대학 (경영·항공서비스·기계·전기전자·뷰티·생명공학)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2027", "year": "2027"},
    "창신대학교": {"loc": "경남(창원)", "rank": "-", "majors_eng": "글로벌학부(스마트경영·IT제조)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2027", "year": "2027"},
    "제주국제대학교": {"loc": "제주", "rank": "-", "majors_eng": "영어트랙 (항공경영·호텔관광·소방방재)", "lang": "IELTS 5.5 / TOEFL iBT 3.5", "period": "2026-2 순수외국인", "year": "2027"},
    "한일장신대학교": {"loc": "전북", "rank": "-", "majors_eng": "AI융합혁신경영학과 (영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2027", "year": "2027"},
    "평택대학교": {"loc": "경기", "rank": "-", "majors_eng": "AI융합학과 / 데이터정보학과 / 융합소프트웨어 / 경영(이중언어)", "lang": "IELTS 5.5 / TOEFL iBT 71", "period": "2025.11.10~12.19", "year": "2026"},
    "한국외국어대학교": {"loc": "서울", "rank": "#17", "majors_eng": "AI데이터융합학부 / Finance&AI / 컴퓨터공학부 / 국제학부", "lang": "IELTS 5.5 / TOEFL iBT 59", "period": "2025.9.1~9.12", "year": "2026"},
    "세종대학교": {"loc": "서울", "rank": "#19", "majors_eng": "인공지능데이터사이언스학과 / 컴퓨터공학 / 소프트웨어", "lang": "IELTS 5.5 / TOPIK 3", "period": "2025.9.8~9.19", "year": "2026"},
    "건국대학교": {"loc": "서울", "rank": "#8", "majors_eng": "컴퓨터소프트웨어학과 / 컴퓨터공학부 / 응용통계학과", "lang": "IELTS 5.5 / TOPIK 3", "period": "2025.9.4~9.11", "year": "2026"},
    "한림대학교": {"loc": "강원", "rank": "-", "majors_eng": "데이터사이언스학부 / 소프트웨어학부 / AI융합학부", "lang": "IELTS 5.5 / TOPIK 2", "period": "2025.11.17~12.23", "year": "2026"},
}

# --- Korean-track schools that accept foreigner (English not required, TOPIK-based) ---
# From _ielts50_scan2: no English requirement + TOPIK track
KOREAN_TRACK = {
    "국립경국대학교": {"loc": "경북(안동)", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "국립창원대학교": {"loc": "경남(창원)", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "덕성여자대학교": {"loc": "서울", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "서울여자대학교": {"loc": "서울", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "영남대학교": {"loc": "경북(경산)", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "가톨릭관동대학교": {"loc": "강원(강릉)", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "감리교신학대학교": {"loc": "서울", "rank": "-", "majors": "신학 등", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "수원가톨릭대학교": {"loc": "경기", "rank": "-", "majors": "전 학과", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
    "장로회신학대학교": {"loc": "서울", "rank": "-", "majors": "신학 등", "lang": "TOPIK 기반 (영어 불요)", "period": "2027", "year": "2027"},
}

# --- Build KB ---
kb = {"meta": {"generated": "2026-08-27", "note": "2027/2026 외국인 전형 요강 검증 데이터. 외국인(정규) 전형 기준, 재외국민 특별전형 제외."}, "schools": {}}

for name, info in ENGLISH_TRACK.items():
    u = data_by_name.get(name, {})
    entry = {
        "name": name,
        "loc": info["loc"],
        "rank": info["rank"],
        "track": "영어트랙",
        "year": info["year"],
        "majors": info["majors_eng"],
        "lang_req": info["lang"],
        "period": info["period"],
        "tuition_semester": TUITION.get(name, "확인 필요"),
        "scholarships": SCH.get(name, {"enroll": [], "existing": []}),
    }
    if "note" in info:
        entry["note"] = info["note"]
    kb["schools"][name] = entry

for name, info in KOREAN_TRACK.items():
    u = data_by_name.get(name, {})
    entry = {
        "name": name,
        "loc": info["loc"],
        "rank": info["rank"],
        "track": "한국어트랙",
        "year": info["year"],
        "majors": info["majors"],
        "lang_req": info["lang"],
        "period": info["period"],
        "tuition_semester": TUITION.get(name, "확인 필요"),
        "scholarships": SCH.get(name, {"enroll": [], "existing": []}),
    }
    kb["schools"][name] = entry

out = os.path.join(BASE, "verified_kb.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"통합 KB 생성 완료: {out}")
print(f"영어트랙: {len(ENGLISH_TRACK)}개, 한국어트랙: {len(KOREAN_TRACK)}개, 총 {len(kb['schools'])}개 학교")
