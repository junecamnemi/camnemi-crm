#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove duplicate legacy '인하대' key (language-only) — merged into '인하대학교'.
Backup first. Only removes if '인하대학교' has 어학연수 (the canonical record)."""
import json, os, shutil, datetime

DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
bak = DB.replace(".json", f"_dedupe_{datetime.date.today().isoformat()}.json")
shutil.copy(DB, bak)

cdb = json.load(open(DB, encoding="utf-8"))
sch = cdb["schools"]

# safety: only proceed if canonical '인하대학교' exists and has 어학연수
if "인하대학교" in sch and "어학연수" in sch["인하대학교"].get("programs", {}):
    if "인하대" in sch:
        del sch["인하대"]
        print("✓ 중복 '인하대'(어학전용 레거시키) 제거 — '인하대학교'로 통합됨")
    else:
        print("'인하대' 키 없음")
    json.dump(cdb, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("저장 완료. 총 학교:", len(sch))
else:
    print("⚠ 안전장치: '인하대학교' 어학연수 확인 안됨 - 중단")
