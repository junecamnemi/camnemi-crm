# -*- coding: utf-8 -*-
"""Build KB section 'lang_programs' from the language-PDF scan + language_school_urls.
For each school: region (from data.js or url DB), tuition info, duration structure,
period, D-4, plus the local PDF path for reference."""
import json, re, os

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
SCAN = r"C:\Users\USER\camnemi-crm\backend\_lang_scan.json"
URLS = r"C:\Users\USER\camnemi-crm\backend\language_school_urls.json"

kb = json.load(open(KB, encoding="utf-8"))
scan = json.load(open(SCAN, encoding="utf-8"))
urls = json.load(open(URLS, encoding="utf-8"))

# url DB school->region/type (region mostly empty) + data.js loc
content = open(r"C:\Users\USER\camnemi-crm\data.js", encoding="utf-8").read()
s = content.find("[")
d = 0
for i in range(s, len(content)):
    if content[i] == "[": d += 1
    elif content[i] == "]":
        d -= 1
        if d == 0:
            data = json.loads(content[s:i + 1])
            break
loc = {u.get("n"): u.get("loc") for u in data if u.get("type") == "univ"}
url_loc = {}
for x in urls:
    url_loc[x["school"]] = x.get("region", "") or ""

def find_school_loc(scan_key):
    for name in (scan_key, scan_key + "학교", scan_key + "대학교"):
        if name in loc: return loc[name]
        if name in url_loc: return url_loc[name]
    # fuzzy
    for name, l in loc.items():
        if scan_key in name: return l
    for name, l in url_loc.items():
        if scan_key in name: return l
    return ""

def clean_fees(fees):
    """fees list may have big noise; keep 5-digit amounts in KRW 30만~250만 range"""
    out = []
    for f in fees:
        m = re.findall(r"\d{5,7}", f)
        if not m: continue
        v = int(m[-1])
        if 300000 <= v <= 2500000:
            out.append(v)
    return sorted(set(out)) if out else None

progs = {}
for key, v in scan.items():
    if v.get("chars", 0) <= 100:
        continue  # empty/image PDF, skip (note separately)
    fees = clean_fees(v.get("fees", []))
    dur = v.get("duration") or {}
    progs[key] = {
        "region": find_school_loc(key),
        "tuition_range": {"min": fees[0], "max": fees[-1]} if fees else None,
        "tuition_note": "수업료(학기/term) 원본 PDF 기반",
        "structure": {
            "per_term": f"{dur.get('weeks')}주" if dur.get("weeks") and dur.get("weeks") not in ("0",) else "10주(기본)",
            "total_hours": f"{dur.get('total_hours')}h" if dur.get("total_hours") else "200h(표준 10주)",
            "per_day": f"{dur.get('per_day_hours')}h/day" if dur.get("per_day_hours") else None,
        },
        "is_200h_10wk": bool(v.get("has_200h") or v.get("has_10week")),
        "d4_eligible": v.get("has_d4", False),
        "dorm": v.get("has_dorm", False),
        "period": v.get("period"),
        "guide_pdf": os.path.join(r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강", v.get("file", "")),
    }

# empty-text PDFs (image-based) — note separately
empty = {key: v.get("file") for key, v in scan.items() if v.get("chars", 0) <= 100}

kb["lang_programs"] = {
    "note": "한국어연수(D-4) 프로그램. 170개 학교 PDF 스캔(2026-09-06). tuition_range=수업료(학기). 대부분 1학기 10주/200시간 표준.",
    "updated": "2026-09-06",
    "schools": progs,
    "image_only_pdfs_no_text": empty,
}
json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"lang_programs 반영: {len(progs)}개 학교 (텍스트 추출된 것)")
print(f"이미지전용(미추출): {len(empty)}개 — {list(empty.keys())}")
n_fee = sum(1 for v in progs.values() if v.get("tuition_range"))
n_d4 = sum(1 for v in progs.values() if v.get("d4_eligible"))
print(f"수업료 확보: {n_fee} | D-4 확인: {n_d4}")
