#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify + fix MASTER's language requirements in the KB using ACTUAL grad guides.

Verified sources (web research this session):
- 연세대 대학원: TOPIK 3 / TOEFL iBT 71 / TOEIC 750 / TEPS 285 / IELTS 5.5
- 서강대 대학원: 한국어트랙 TOPIK 5~6 / 영어트랙 IELTS 7.0 / TOEFL 100 (서강글로벌장학 기준)
- 부산대 대학원: TOPIK 3 / IELTS 5.5 / TOEFL iBT 80 / NEW TEPS 326 / TOEIC 675
"""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

MA_FIXES = {
    "연세대학교": {
        "lang_req": "TOPIK 3 OR English (TOEFL iBT 71 / IELTS 5.5 / TOEIC 750 / TEPS 285)",
        "scholarship": "대학원 외국인 장학 (성적/어학 기반) — 정확한 기준은 학과별 확인",
        "note": "2026~2027 대학원 외국인 입학: 한국어 TOPIK 3 / 영어 IELTS 5.5 이상. 석사 지원 가능.",
    },
    "서강대학교": {
        "lang_req": "한국어트랙 TOPIK 5~6 / 영어트랙 IELTS 7.0 / TOEFL iBT 100 / NEW TEPS 419",
        "scholarship": "[재학] 서강글로벌장학금: TOPIK 6/IELTS 7.0+ → 등록금 80%, TOPIK 5 → 차등 (매학기 GPA 유지)",
        "note": "서강글로벌장학 등록금 80%까지. 영어트랙은 IELTS 7.0 필요 (5.5 불가).",
    },
    "부산대학교": {
        "lang_req": "TOPIK 3 OR English (IELTS 5.5 / TOEFL iBT 80 / NEW TEPS 326 / TOEIC 675)",
        "scholarship": "[입학] 국제학생장학: 영어점수+성적 → 등록금 전액~반액 / [재학] 성적우수 장학",
        "note": "대학원 외국인: TOPIK 3 또는 IELTS 5.5 이상. 입학 시 영어점수로 등록금 전액~반액 장학 가능.",
    },
}

for name, ch in MA_FIXES.items():
    if name in kb.get("master", {}).get("schools", {}):
        kb["master"]["schools"][name].update(ch)
        print(f"석사 수정: {name}")
    else:
        print(f"석사 없음: {name}")

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print("저장 완료")
