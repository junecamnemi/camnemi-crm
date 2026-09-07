#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add student count (stu) to verified_kb.json schools from data.js, for transparency."""
import json, os, re

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")
DATA = r"C:\Users\USER\camnemi-crm\data.js"

with open(DATA, encoding="utf-8") as f:
    content = f.read()
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

stu_map = {u.get("n"): u.get("stu") for u in data}

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

n = 0
for sec in ["schools"]:
    for name, s in kb.get(sec, {}).items():
        base = name.replace("(ERICA)", "").strip()
        for dname, stu in stu_map.items():
            if dname == base or (dname in base and len(dname) > 4):
                s["student_count"] = stu
                n += 1
                break

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)
print(f"학생수 필드 추가: {n}개 학교")
