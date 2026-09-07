#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix missing scholarship conditions in data.js for 한양대, 한국외대, 을지대, 배재대.
Adds tier conditions extracted from the actual 2027 guides."""
import re
import json

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"

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
            data = json.loads(content[start:i + 1])
            break

# FIXES: school -> {scholarship_name: [tiers]}
FIXES = {
    "한양대학교": {
        "신입생 외국인 장학금": [
            {"score_type": "TOEFL", "score": "iBT 79~93 / IELTS 6.5", "amount": "등록금 30% (첫 학기)"},
            {"score_type": "TOEFL", "score": "iBT 94~109 / IELTS 7~7.5", "amount": "등록금 50% (첫 학기)"},
            {"score_type": "TOEFL", "score": "iBT 110~120 / IELTS 8 이상", "amount": "등록금 100% (첫 학기)"},
        ],
        "국제교육원 장학금": [
            {"score_type": "한국어", "score": "국제교육원 4급 수료", "amount": "등록금 30% (첫 학기)"},
            {"score_type": "한국어", "score": "국제교육원 5급 수료", "amount": "등록금 50% (첫 학기)"},
            {"score_type": "한국어", "score": "국제교육원 6급 수료", "amount": "등록금 100% (첫 학기)"},
        ],
    },
    "한국외국어대학교": {
        "총장 장학": [{"score_type": "성적", "score": "입학전형 점수 상위 5%", "amount": "등록금 100% (첫 학기)"}],
        "학장 장학": [{"score_type": "성적", "score": "입학전형 점수 상위 10%", "amount": "등록금 50% (첫 학기)"}],
        "국제교류처장 장학": [{"score_type": "성적", "score": "입학전형 점수 상위 20%", "amount": "1,000,000원 (첫 학기)"}],
        "글로벌인재 A": [{"score_type": "성적", "score": "입학전형 상위자", "amount": "1,700,000원 또는 등록금 100% (첫 학기)"}],
        "글로벌인재 B": [{"score_type": "성적", "score": "입학전형 우수자", "amount": "등록금 50% (1년간)"}],
        "언어능력 우수 A": [
            {"score_type": "TOPIK", "score": "TOPIK 6급", "amount": "등록금 100% (첫 학기)"},
            {"score_type": "TOEFL", "score": "iBT 110~120", "amount": "등록금 100% (첫 학기)"},
            {"score_type": "IELTS", "score": "8.0~9.0", "amount": "등록금 100% (첫 학기)"},
        ],
        "언어능력 우수 B": [
            {"score_type": "TOPIK", "score": "TOPIK 5급", "amount": "등록금 50% (첫 학기)"},
            {"score_type": "TOEFL", "score": "iBT 100~109", "amount": "등록금 50% (첫 학기)"},
            {"score_type": "IELTS", "score": "7.0~7.5", "amount": "등록금 50% (첫 학기)"},
        ],
    },
    "을지대학교": {
        "순수 외국인 입학자 장학금": [
            {"score_type": "TOEFL", "score": "iBT 59 이상", "amount": "전 학년 수업료 지원 (성적별)"},
            {"score_type": "IELTS", "score": "5.5 이상", "amount": "전 학년 수업료 지원 (성적별)"},
        ],
    },
    "배재대학교": {
        "정부초청장학생(GKS)": [
            {"score_type": "GKS", "score": "정부초청장학생 선발자", "amount": "등록금·체재비 전액 (정부)"},
        ],
    },
}

changed = 0
for u in data:
    nm = u.get("n")
    if nm not in FIXES:
        continue
    for s in (u.get("scholarships") or []):
        sname = s.get("name", "")
        for key, tiers in FIXES[nm].items():
            if key in sname:
                s["tiers"] = tiers
                changed += 1
                print(f"  수정: {nm} - {sname} ({len(tiers)} 조건)")

# write back - replace only the array portion
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

print(f"\n총 {changed}개 장학금 조건 보완 완료")
