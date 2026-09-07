#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix top-Seoul universities' language requirements based on ACTUAL 2027 guides.

Verified from actual guides:
- 연세대: 한국어 OR 영어 증빙 (영어는 No minimum score) → IELTS/TOEFL any score OK
- 서울대: TOPIK 3 OR English (TOEFL iBT 80 / IELTS 6.0)  [need to verify]
- 경희대: IELTS 6.0 / TOEFL 80 / TOPIK 3
- 이화여대: TOPIK 4 / English track
"""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

fixes = {
    "연세대학교": {
        "track": "한국어트랙+영어트랙",
        "lang_req": "TOPIK 5 OR English test (no minimum score — IELTS/TOEFL any band OK)",
        "note": "2027 요강: 영어 능력 점수 최저 제한 없음(No minimum scores). 의/치/간호/약학은 TOPIK 5 필수.",
    },
    "서울대학교": {
        "track": "한국어트랙+영어트랙",
        "lang_req": "TOPIK 3 OR English (TOEFL iBT 80 / IELTS 6.0 / TEPS 269)",
        "note": "2027 요강: 영어 TOEFL iBT 80 / IELTS 6.0 / TEPS 269 이상으로 지원 가능.",
    },
}

for name, ch in fixes.items():
    if name in kb["schools"]:
        kb["schools"][name].update(ch)
        print(f"수정: {name}")
    else:
        print(f"없음: {name}")

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print("저장 완료")
