#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Progressive merge helper for batch 15 (2026-09-05). Merges new track entries
into the per-track daily result files, replacing any existing entry per school."""
import json, io, os

BASE = "C:/Users/USER/camnemi-crm/backend"
FILES = {
    "BA":   os.path.join(BASE, "_ba_batches",   "BA_daily_20260905_result.json"),
    "MA":   os.path.join(BASE, "_ma_batches",   "MA_daily_20260905_result.json"),
    "lang": os.path.join(BASE, "_lang_batches", "lang_daily_20260905_result.json"),
}

NEW = {
    # track -> list of entries
    "BA": [
        {
            "school": "호남대학교",
            "status": "2026_or_older",
            "url": "https://enter.honam.ac.kr/foreignerPDF",
            "title": "2026학년도 후기 신·편입학 학부 외국인특별전형 모집요강 (호남대학교 입학안내 외국인 모집요강)",
            "note": "입학안내(enter.honam.ac.kr) 외국인 모집요강 페이지의 최신 PDF가 2026학년도 후기(2026.9월 입학, 원서 2026.5~7월) 학부 외국인특별전형 모집요강으로 2027학년도 외국인 모집요강은 아직 미게시. 2027 수시 모집요강(일반 전형)은 게시되어 있으나 외국인 전용 요강 아님."
        },
    ],
    "MA": [
        {
            "school": "호남대학교",
            "status": "2026_or_older",
            "url": "https://graduate.honam.ac.kr/attach/pdfgraduate/20251111092550VRjmouFGFP7LJEWvZiR9.pdf",
            "title": "2026학년도 전기 대학원 석·박사 학위과정 외국인 신(편)입생 모집 요강",
            "note": "공식 대학원 사이트(graduate.honam.ac.kr) 최신 외국인 모집요강은 2026학년도 전기(2025.11.17~12.5 원서접수) PDF이며 2027학년도 전기 외국인 모집요강은 아직 미게시(통상 10~11월 공고 예정)."
        },
    ],
    "lang": [
        {
            "school": "호남대학교",
            "status": "2026_or_older",
            "url": "https://global.honam.ac.kr/KoreanAdmissionGuide/pdfdownload",
            "title": "[PDF] 한국어교육원 외국인 유학생(한국어 연수 과정) 모집요강 - 호남대학교",
            "note": "국제교류처(global.honam.ac.kr) 한국어교육원 모집요강 PDF 최신은 2026학년도 봄·여름학기(2026.03.03 개강) 일정으로 2027학년도 정규과정 일정은 아직 미게시."
        },
    ],
}

def merge(track):
    path = FILES[track]
    data = []
    if os.path.exists(path):
        with io.open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    by_school = {e.get("school"): i for i, e in enumerate(data)}
    for entry in NEW.get(track, []):
        s = entry["school"]
        if s in by_school:
            data[by_school[s]] = entry
        else:
            data.append(entry)
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # verify
    with io.open(path, "r", encoding="utf-8") as f:
        json.load(f)
    print("OK", track, len(data), "entries;",
          [e["school"] for e in data if e["school"] in [x["school"] for x in NEW.get(track, [])]])

if __name__ == "__main__":
    for t in ["BA", "MA", "lang"]:
        merge(t)
