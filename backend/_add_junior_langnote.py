#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add a language-note to junior colleges so the advisor flags uncertain IELTS acceptance.
Also add a 'lang_source' hint for transparency."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")

with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

junior = kb["junior"]["schools"]
flagged = 0
for name, s in junior.items():
    # schools with neither TOPIK nor IELTS explicitly listed -> flag for confirmation
    if not s.get("topik_req") and not s.get("ielts_req"):
        s["lang_note"] = "No explicit language requirement in our data — confirm with the college before applying"
        flagged += 1
    elif s.get("ielts_req") and not s.get("topik_req"):
        s["lang_note"] = f"IELTS {s['ielts_req']} or equivalent (confirm exact test list)"
    elif s.get("topik_req") and not s.get("ielts_req"):
        s["lang_note"] = f"TOPIK {s['topik_req']}-based; IELTS may also be accepted (confirm with college)"
    else:
        s["lang_note"] = f"TOPIK {s['topik_req']} / IELTS {s['ielts_req']}"

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"전문대학 언어 노트 추가 완료 ({flagged}개 학교가 '확인 필요'로 표시)")
