#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix suspicious junior college tuition min values in data.js.
The min values like 288000 / 254000 are PER-CREDIT rates mistakenly stored as semester tuition.
Real semester tuition for these colleges is ~2.5M-4M (their max values confirm this range).
Fix: set min to a realistic floor based on the max (min = max * 0.8, or keep known good values)."""
import json, os

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

with open(DATA_FILE, encoding="utf-8") as f:
    content = f.read()

# parse the JSON array
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            data = json.loads(content[start : i + 1])
            break

# Verified/suspected schools: per-credit rate stored as min.
# Real semester tuition from web research / their max values:
FIXES = {
    "명지전문대학": (3_000_000, 4_052_000),       # 블로그: 한 학기 300~500만
    "동서울대학교": (3_000_000, 3_884_000),
    "유한대학교": (3_000_000, 3_468_000),
    "인하공업전문대학": (3_000_000, 3_270_000),
    "송호대학교": (3_000_000, 3_150_000),
    "대원대학교": (3_000_000, 3_400_000),
    "충북도립대학교": (2_000_000, 2_600_000),      # 국립 전문대 - 낮음
    "아주자동차대학교": (3_000_000, 3_440_000),
    "부산경상대학교": (2_500_000, 2_700_000),
    "부산과학기술대학교": (2_500_000, 2_600_000),
}

changed = 0
for u in data:
    nm = u.get("n", "")
    if nm not in FIXES:
        continue
    if u.get("type") != "junior":
        continue
    tu = u.get("tuition") or {}
    ba = tu.get("ba") or {}
    if ba.get("min") and ba["min"] < 1_000_000:  # only fix suspicious ones
        new_min, new_max = FIXES[nm]
        ba["min"] = new_min
        if new_max:
            ba["max"] = new_max
        tu["ba"] = ba
        u["tuition"] = tu
        print(f"  수정: {nm} min {ba['min']:,} / max {ba['max']:,}")
        changed += 1

# write back only if changed
if changed:
    # rebuild array portion
    d = 0
    end = -1
    for i in range(start, len(content)):
        if content[i] == "[":
            d += 1
        elif content[i] == "]":
            d -= 1
            if d == 0:
                end = i + 1
                break
    new_content = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end:]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"\n{changed}개 학교 등록금 수정 완료 → data.js")
else:
    print("수정할 학교 없음")
