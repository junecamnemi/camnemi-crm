#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add master's (석사) section to the verified knowledge base, merging:
- _ma_rich.json (schools, region, rank, tuition, majors)
- _ma_batches guide status/URLs
- verified language req (부산대 IELTS 5.5 / TOPIK 3, 서강 IELTS 7.0 등)
- verified scholarships (부산대, 서강 글로벌장학 등)
"""
import json, re, os, glob

BASE = r"C:\Users\USER\camnemi-crm\backend"

# load rich MA data
with open(os.path.join(BASE, "_ma_rich.json"), encoding="utf-8") as f:
    ma_schools = json.load(f)

# load guide status
ma_guide = {}
for fn in glob.glob(os.path.join(BASE, "_ma_batches", "MA_batch_*_result.json")) + \
          glob.glob(os.path.join(BASE, "_ma_batches", "MA_fill_*_result.json")):
    try:
        with open(fn, encoding="utf-8") as f:
            r = json.load(f)
        if isinstance(r, list):
            for item in r:
                if isinstance(item, dict) and item.get("school"):
                    ma_guide[item["school"]] = item
    except Exception:
        pass

# Verified master's scholarships / language from this session's research
# (from actual grad guides)
MA_VERIFIED = {
    "부산대학교": {
        "lang": "TOPIK 3 / IELTS 5.5 / TOEFL iBT 80 / NEW TEPS 326 / TOEIC 675",
        "scholarship": "[입학] 국제학생장학: 영어점수(TOEFL iBT 80/IELTS 5.5 등)+GPA → 등록금 전액~반액 / [재학] 성적우수 장학 (GPA별 차등)",
        "note": "Graduate admissions: Admission A(외국인) / B(재외국민 제외주의), 언어요건 면제 가능(지도교수 서명)"
    },
    "인하대학교": {
        "lang": "한국어 트랙: 한국어 요구 / 영어 트랙(경영학과 Digital 등): 영어만",
        "scholarship": "대학원 외국인 장학금 (학과/성적별)",
        "note": "2026 Fall Graduate admissions: 원서 4.14~5.11, 영어전용학과(경영학 Digital)는 영어성적만 인정"
    },
    "서강대학교": {
        "lang": "TOPIK 5~6 / IELTS 7.0 / TOEFL iBT 100 / NEW TEPS 419",
        "scholarship": "[재학] 서강글로벌장학금: TOPIK 6/IELTS 7.0+ → 등록금 80%, TOPIK 5 → 차등 (매학기 GPA 유지)",
        "note": "외국인 재학생 대상, 등록금 80%까지"
    },
}

# General language requirement defaults (verified)
# 영어트랙: IELTS 5.5~6.5 / 한국어트랙: TOPIK 3~4 (elite는 TOPIK 4~5)
GENERAL_LANG = "한국어트랙 TOPIK 3~4 (상위권 TOPIK 4~5) / 영어트랙 IELTS 5.5~6.5"

kb_path = os.path.join(BASE, "verified_kb.json")
with open(kb_path, encoding="utf-8") as f:
    kb = json.load(f)

# add master's section
kb["master"] = {"meta": "석사(대학원) 외국인 전형. 학부와 별도 요강. 영어트랙 IELTS 5.5~6.5 / 한국어트랙 TOPIK 3~4 표준. 장학금은 대부분 재학 중 성적/어학 기반.", "schools": {}}

def rk_key(x):
    try:
        return (0, int(re.sub(r"[^0-9]", "", str(x["rank"])))) if x["rank"] not in (None, "-", "") else (1, 999)
    except:
        return (1, 999)

for s in sorted(ma_schools, key=rk_key):
    name = s["name"]
    guide = ma_guide.get(name, {})
    verified = MA_VERIFIED.get(name, {})
    entry = {
        "name": name,
        "region": s["loc"],
        "rank": s["rank"],
        "n_majors": len(s["majors"]),
        "majors": s["majors"],  # full list for keyword search
        "majors_sample": s["majors"][:8],
        "tuition_min": s["tuition_min"],
        "tuition_max": s["tuition_max"],
        "guide_status": guide.get("status", "unknown"),
        "guide_url": guide.get("url", ""),
        "lang_req": verified.get("lang", GENERAL_LANG),
        "scholarship": verified.get("scholarship", "대학별 확인 필요 (보통 재학 중 성적/어학 기반)"),
    }
    if "note" in verified:
        entry["note"] = verified["note"]
    kb["master"]["schools"][name] = entry

with open(kb_path, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"지식베이스에 석사 섹션 추가 완료: {len(kb['master']['schools'])}개 학교")
print(f"\n=== 샘플 (상위 랭크) ===")
cnt = 0
for name, s in kb["master"]["schools"].items():
    if s["rank"] not in (None, "-", "") and cnt < 10:
        print(f"  #{s['rank']} {name} ({s['region']}) - 등록금 {s['tuition_min']} - 요건: {s['lang_req'][:40]}")
        cnt += 1

print(f"\n=== 검증된 석사 장학금/요건 학교 ===")
for name in MA_VERIFIED:
    s = kb["master"]["schools"].get(name)
    if s:
        print(f"  {name}: {s['lang_req'][:60]} | {s['scholarship'][:60]}")
