# -*- coding: utf-8 -*-
"""Add Kyungwoon Univ foreigner graduate(MA) data to verified_kb.json master section,
verified from official graduate guide (2026 후기 추가2차 모집요강)."""
import json

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
ma = kb["master"]["schools"]

entry = {
    "name": "경운대학교",
    "region": "경상북도",
    "rank": None,
    "guide_status": "2026",
    "guide_url": "https://www.ikw.ac.kr/graduate",
    "lang_req": "외국인 일반과정: 한국어트랙 TOPIK 3급 이상 또는 이중언어(사회통합프로그램 3단계/사전평가 61점=TOPIK3, 4단계/81점=TOPIK4, 세종학당 중급1B=TOPIK3, 중급2B=TOPIK4) / 영어트랙: IELTS 5.5, TEPS 600(NEW 326), TOEFL 530(CBT 197, iBT 71), CEFR B2, TOEIC 600 이상. 이중언어과정: TOEFL 530(iBT 71), IELTS 5.5, TEPS 600, CEFR B2, TOEIC 600",
    "topik_req": "TOPIK 3급 (KIIP 3단계/사전평가 61점 동등 인정)",
    "ielts_req": "IELTS 5.5",
    "tuition": None,
    "tuition_semester": None,
    "majors": ["멀티미디어학과", "일반대학원 전공", "산업정보대학원 전공", "사회복지대학원 전공"],
    "guide_pdf": "경운대 대학원 2026 후기 추가2차 모집요강 (https://www.ikw.ac.kr/graduate)",
    "kiip": "KIIP 3단계(사전평가61점)=TOPIK3, KIIP 4단계(81점)=TOPIK4 인정",
    "note": "부모 모두 외국국적 외국인 + 어학기준 1개 충족. 졸업 전 TOPIK 4급 취득 필수. TOPIK 3급 미충족 시 300시간 한국어교육 조건부 입학. 외국인 장학금: TOPIK5+GPA3.5(최상위)~TOPIK3+GPA3.0(기본), IELTS 5.5~7.0 대응. 세종학당 중급1B=TOPIK3, 중급2B=TOPIK4 인정.",
    "foreign_guide_verified": "2026-09-06",
}

ma[entry["name"]] = entry
kb["master"]["schools"] = ma
json.dump(kb, open(KB_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"경운대 MA 추가 완료 (master {len(ma)}개)")
