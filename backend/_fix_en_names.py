#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix ambiguous English short-name mappings (KMU/KW/KWU) in _en_names.json."""
import json

PATH = r"C:\Users\USER\camnemi-crm\backend\_en_names.json"
with open(PATH, encoding="utf-8") as f:
    names = json.load(f)

FIXES = {
    "계명대학교": "Keimyung University",
    "광운대학교": "Kwangwoon University",
    "광주여자대학교": "Kwangju Women's University",
}

changed = 0
for k, v in FIXES.items():
    if names.get(k) != v:
        print(f"  수정: {k} → {v} (기존: {names.get(k)})")
        names[k] = v
        changed += 1

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(names, f, ensure_ascii=False, indent=2)
print(f"\n{changed}개 수정 완료")
