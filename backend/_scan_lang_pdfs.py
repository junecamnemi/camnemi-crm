# -*- coding: utf-8 -*-
"""Scan all 170 Korean-language-program PDFs (어학연수) and extract structured facts:
period, tuition/fees, duration(weeks/hours), levels, entry, D-4 info, refund.
Writes backend/_lang_scan.json keyed by school."""
import os, re, json, glob
import pymupdf

SRC = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_어학연수_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_lang_scan.json"

def norm(t):
    return re.sub(r"[ \t]+", " ", t)

def extract_period(full):
    # 접수기간/모집기간 with dates
    pats = [
        r"(?:접수기간|원서접수|모집기간|신청기간|접수일정)[^.]{0,120}?((?:20\d\d)[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
        r"((?:20\d\d)[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20\d\d)[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
    ]
    for p in pats:
        m = re.search(p, norm(full))
        if m:
            return re.sub(r"\s+", "", m.group(1))
    return None

def extract_fee(full):
    """Find tuition amounts: 입학금, 수업료/등록금 per term."""
    tt = full.replace(",", "")
    # find 입학금, 수업료/등록금/학비 amounts
    amounts = []
    for m in re.finditer(r"(입학금|수업료|등록금|교육비|학비|1학기당|학기당)[^0-9]{0,20}([0-9]{5,7})", norm(full)):
        amounts.append(f"{m.group(1)} {m.group(2)}")
    # general big numbers in tuition range 300000-2000000
    if not amounts:
        for m in re.finditer(r"(?<!\d)(\d{6,7})(?!\d)", tt):
            v = int(m.group(1))
            if 400000 <= v <= 2500000:
                amounts.append(str(v))
    return list(dict.fromkeys(amounts))[:10]

def extract_duration(full):
    n = norm(full)
    m = re.search(r"(\d+)\s*주", n)
    weeks = m.group(1) if m else None
    m = re.search(r"총\s*(\d+)\s*시간", n)
    hours = m.group(1) if m else None
    m = re.search(r"(1일|하루)\s*(\d+)시간", n)
    perday = m.group(2) if m else None
    return {"weeks": weeks, "total_hours": hours, "per_day_hours": perday}

def extract_levels(full):
    n = norm(full)
    if re.search(r"초급|중급|고급|1급.*6급|레벨테스트|level test", n):
        return True
    m = re.search(r"(\d+)\s*개?\s*레벨|레벨\s*(\d+)", n)
    return m.group(0) if m else None

results = {}
for fp in sorted(glob.glob(os.path.join(SRC, "*.pdf"))):
    fn = os.path.basename(fp)
    school = fn.replace("_한국어교육원.pdf", "").replace("_한국어교육원_2026가을겨울.pdf", "").replace("_한국어교육원_2026.pdf", "")
    try:
        doc = pymupdf.open(fp)
        full = "\n".join(p.get_text() for p in doc)
        doc.close()
    except Exception as e:
        results[school] = {"error": str(e)}
        continue
    results[school] = {
        "file": fn,
        "chars": len(full),
        "period": extract_period(full),
        "fees": extract_fee(full),
        "duration": extract_duration(full),
        "levels_note": extract_levels(full),
        "has_200h": "200시간" in full or "200 시간" in full,
        "has_10week": bool(re.search(r"10주", full)),
        "has_d4": bool(re.search(r"D-4|D4|어학연수\(D", full)),
        "has_dorm": bool(re.search(r"기숙사|생활관", full)),
    }

json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_text = sum(1 for v in results.values() if v.get("chars", 0) > 100)
n_period = sum(1 for v in results.values() if v.get("period"))
n_fee = sum(1 for v in results.values() if v.get("fees"))
n_d4 = sum(1 for v in results.values() if v.get("has_d4"))
print(f"총 {len(results)}개 PDF | 텍스트있음 {n_text} | 기간 {n_period} | 수업료 {n_fee} | D-4언급 {n_d4}")
