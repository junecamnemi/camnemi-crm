#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Correct 경운대학교 학부 record: add scholarship PROVENANCE + tuition (from official intl office page).

Verified 2026-09-12 against https://www.ikw.ac.kr/worldle/page/link.tc?mn=3874&pageSeq=2748
(국제처 > 외국인입학 > 학부입학 > 등록금 및 장학금)
Values matched the existing scholarships_categorized — the gap was missing source, not wrong data.
"""
import json, os, shutil, datetime

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
CDB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
URL = "https://www.ikw.ac.kr/worldle/page/link.tc?mn=3874&pageSeq=2748"

kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, KB.replace(".json", f"_bak_kw_{datetime.date.today()}.json"))
v = kb["schools"]["경운대학교"]

v["scholarship_source"] = {
    "url": URL,
    "verified": "2026-09-12",
    "note": "모집요강 PDF에는 장학금 표 없음 → 공식 국제처 학부입학 페이지에서 확인. 기존 값과 일치.",
}
v["scholarships_verified"] = True

# official tuition (2023 기준, 1학년 입학학기) in KRW
v["tuition_official_2023"] = {
    "note": "경운대 국제처 학부입학 등록금 안내 (2023학년도 기준, 1학년 입학학기). 최신은 학교 확인 필요.",
    "공학계열": 4120000, "자연계열": 4045000, "인문계열": 3170000,
    "체육계열": 4070000, "예능계열": 4320000, "자연2계열(항공운항)": 5005000,
}

# fix the misleading curated note
old = v.get("notes_curated", "")
if "장학금 표기 없음" in old:
    v["notes_curated"] = old.replace(
        "모집요강에 등록금·장학금 표기 없음.",
        "모집요강 PDF에는 등록금·장학금 표 없음 → 공식 국제처 학부입학 페이지에서 확인(출처 기록)."
    )

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print("verified_kb 경운대 정정 완료:")
print("  scholarship_source:", v["scholarship_source"]["url"])
print("  scholarships_verified:", v["scholarships_verified"])
print("  tuition_official_2023 키:", list(v["tuition_official_2023"].keys()))

# mirror to consulting_db if school exists
cdb = json.load(open(CDB, encoding="utf-8"))
if "경운대학교" in cdb["schools"]:
    cdb["schools"]["경운대학교"]["scholarship_source"] = URL
    open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
    print("consulting_db 반영 완료")
