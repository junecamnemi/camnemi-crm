#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deep verification of all adiga 2027 foreigner PDFs:
1) Actual year label (2027학년도 vs 2026학년도 vs unknown)
2) Precise application period (원서접수/전형일정 section) with exact dates
3) Language requirements (TOPIK/IELTS/TOEFL) mentioned in guide"""
import os
import re
import json
import pymupdf

DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"

results = {}
for fn in sorted(os.listdir(DIR)):
    if not fn.lower().endswith(".pdf"):
        continue
    path = os.path.join(DIR, fn)
    m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", fn)
    school = m.group(1) if m else fn.replace(".pdf", "")
    try:
        doc = pymupdf.open(path)
        pages = [p.get_text() for p in doc]
        doc.close()
    except Exception as e:
        results[school] = {"file": fn, "error": str(e)}
        continue

    full = "\n".join(pages)
    first = "\n".join(pages[:3])

    # 1) Year label
    y2027 = ("2027학년도" in first) or ("2027 학년도" in first) or ("2027년 3월" in first and "2026학년도" not in first[:200])
    y2026 = "2026학년도" in first
    if y2027 and not y2026:
        year = "2027"
    elif y2026 and not y2027:
        year = "2026"
    elif y2027 and y2026:
        year = "2027(혼재)"
    else:
        # search more broadly
        if re.search(r"2027\s*학년도|2027\s*년\s*[0-9]월 입학|2027 Admission", full[:2000]):
            year = "2027(추정)"
        elif re.search(r"2026\s*학년도|2026\s*년\s*[0-9]월 입학", full[:2000]):
            year = "2026(추정)"
        else:
            year = "?"

    # 2) Precise application period: find the schedule section and grab the row after '원서접수'
    period = None
    lines = full.split("\n")
    # Find a line containing 원서접수 or 접수 or 모집일정 that is followed by a real date
    DATE_PAT = re.compile(
        r"(?:20\d{2}\s*[.\-/년]\s*)?\d{1,2}\s*[.\-/월]\s*\d{1,2}"
        r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?"
        r"(?:\s*[~∼\-–]\s*(?:20\d{2}\s*[.\-/년]\s*)?\d{1,2}\s*[.\-/월]\s*\d{1,2}"
        r"(?:\s*[\(（]\s*[월화수목금토일]\s*[\)）])?)?"
    )
    for i, line in enumerate(lines):
        if not re.search(r"원서\s*접수|접수\s*기간|모집\s*일정|전형\s*일정|입학\s*지원서|인터넷\s*접수|접수\s*일정", line):
            continue
        # look at this line and next 3 lines for a real date (containing 20xx or a month-day with ~)
        ctx = " ".join(x.strip() for x in lines[i:i+4])
        dates = DATE_PAT.findall(ctx)
        # filter: require at least one token with a year OR a clear day.month.day with ~
        real = []
        for d in dates:
            d = d.strip()
            if re.match(r"^\d{1,2}\s*-\s*\d{1,2}$", d):  # page range
                continue
            if re.match(r"^\d{1,2}\s*\.\s*\d{1,2}$", d) and "~" not in d and "–" not in d:
                # bare month.day without range and without year - likely page num
                continue
            if re.search(r"20\d{2}", d) or ("~" in d) or ("–" in d) or ("∼" in d) or ("-" in d):
                real.append(d)
        if real:
            period = {"kw": line.strip(), "ctx": ctx[:200], "dates": real[:4]}
            break

    # 3) Language requirements
    lang = []
    for kw in ["TOPIK", "한국어능력시험", "IELTS", "TOEFL", "TEPS", "TOEIC"]:
        for mm in re.finditer(kw, full):
            ctx = full[max(0, mm.start()-30): mm.start()+80].replace("\n", " ")
            if kw not in " ".join(lang):
                lang.append(ctx[:90])
            break  # first occurrence per kw
    results[school] = {
        "file": fn, "year": year, "period": period, "lang": lang[:6], "chars": len(full),
    }

# Save
with open(r"C:\Users\USER\camnemi-crm\backend\_deep_verify.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Summary
from collections import Counter
ycount = Counter(v.get("year") for v in results.values())
print("연도 분포:", dict(ycount))
print()
print("== 연도가 2027이 아닌 PDF ==")
for s, v in sorted(results.items()):
    if v.get("year") and v["year"] != "2027":
        print(f"  {s}: {v['year']}")
print()
print("== 연도 확인 불가 ==")
for s, v in sorted(results.items()):
    if not v.get("year") or v["year"] == "?":
        print(f"  {s}")
print()
print("== 모집기간 추출됨/미추출 ==")
pcount = Counter("OK" if v.get("period") else "NO" for v in results.values())
print(dict(pcount))
print()
print("== 모집기간 미추출 ==")
for s, v in sorted(results.items()):
    if not v.get("period") and not v.get("error"):
        print(f"  {s}: year={v.get('year')}")
print()
print("== 언어요건 표본 ==")
for s in ["인하대학교", "가천대학교", "숙명여자대학교", "단국대학교", "영남대학교"]:
    if s in results:
        print(f"  {s}: {results[s].get('lang')}")
