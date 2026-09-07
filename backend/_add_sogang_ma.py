#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add Sogang (서강대) to the master's KB — it was missed because majors_ma is empty."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

kb["master"]["schools"]["서강대학교"] = {
    "name": "서강대학교",
    "region": "서울특별시",
    "rank": 11,
    "n_majors": 0,
    "majors": [],
    "majors_sample": [],
    "tuition_min": 5256000,
    "tuition_max": 6977000,
    "guide_status": "unknown",
    "guide_url": "",
    "lang_req": "한국어트랙 TOPIK 5~6 / 영어트랙 IELTS 7.0 / TOEFL iBT 100 / NEW TEPS 419",
    "scholarship": "[재학] 서강글로벌장학금: TOPIK 6/IELTS 7.0+ → 등록금 80%, TOPIK 5 → 차등 (매학기 GPA 유지)",
    "note": "서강글로벌장학 등록금 80%까지. 영어트랙은 IELTS 7.0 필요 (5.5 불가).",
}

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print("서강대 석사 추가 완료")
