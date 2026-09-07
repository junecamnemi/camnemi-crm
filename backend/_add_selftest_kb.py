#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add a selftest section to the verified KB: schools where 자체시험(own Korean test) is accepted,
with the majors available via that route. Confirmed: selftest is usually limited to specific majors."""
import json, re, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

# load data.js
with open(DATA_FILE, encoding="utf-8") as f:
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

# Verified selftest info from this session's PDF scan
SELFTEST_NOTES = {
    "경남대학교": "자체 한국어시험(KKPT) 합격자 → 조건부 입학, 입학 후 한국어 보충반 수강 필수",
    "경동대학교": "자체 한국어능력시험 / 자체 영어능력시험 통과자 (졸업 전 IELTS 5.5 이상 요구)",
    "선문대학교": "자체 한국어시험 합격자 → 등록금(수업료) 50% 장학",
    "영남대학교": "YU TOPIK(자체 한국어시험) 합격 → 외국인 전담 11개 전공만 (휴먼서비스, 차세대반도체, 의생명, 디자인 등)",
    "을지대학교": "본교 자체 한국어능력시험 3급 이상 합격자 가능 (TOPIK 대체)",
    "중원대학교": "자체 한국어시험 2급 이상 (예체능 2급) / 한국어학당 3급 수료 대체",
    "칼빈대학교": "TOPIK 3급 미소지자 → 본교 자체 3급 수준 한국어시험 합격으로 대체",
    "가야대학교": "TOPIK 미실시 시 본교 자체시험으로 한국어 자격 대체",
}

# collect selftest schools with majors
selftest = {}
for u in data:
    req = u.get("req") or {}
    if not req.get("selftest"):
        continue
    if u.get("type") != "univ":
        continue
    nm = u.get("n", "")
    ba = u.get("majors_ba") or []
    majors = []
    if isinstance(ba, list):
        for m in ba:
            if isinstance(m, str):
                majors.append(m)
            elif isinstance(m, dict):
                majors.append(m.get("kr", ""))
    flat = u.get("majors") or []
    if not majors and isinstance(flat, list):
        majors = [m for m in flat if isinstance(m, str)]
    # clean leading markers
    majors = [re.sub(r"^[·ㆍ\s]+", "", m) for m in majors if m]
    selftest[nm] = {
        "name": nm,
        "region": u.get("loc", ""),
        "rank": u.get("rk", "-"),
        "topik_req": req.get("topik"),
        "ielts_req": req.get("ielts"),
        "n_majors": len(majors),
        "majors_sample": majors[:10],
        "selftest_note": SELFTEST_NOTES.get(nm, "자체 한국어시험으로 TOPIK 대체 가능 (요강 확인 필요)"),
    }

# save to KB
kb_path = os.path.join(BASE, "verified_kb.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

kb["selftest"] = {
    "meta": "자체시험(학교 자체 한국어시험)으로 TOPIK 없이 지원 가능한 학교. 주의: 자체시험으로 지원 시 전공이 제한되는 경우가 많음(외국인 전담학부/특정 계열). 요강별로 확인 필요.",
    "schools": selftest,
}

with open(kb_path, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"자체시험 섹션 추가 완료: {len(selftest)}개 학교")
print("\n=== 자체시험 학교 (전공 제한 확인됨) ===")
for nm, s in sorted(selftest.items(), key=lambda kv: (kv[1]["rank"] not in ('-', ''), str(kv[1]["rank"]))):
    note = s["selftest_note"][:50]
    print(f"  {nm} ({s['region']}) 전공{s['n_majors']}개 | {note}")
