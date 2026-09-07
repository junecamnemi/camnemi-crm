# -*- coding: utf-8 -*-
"""DEEP extractor v2 — all BA guide PDFs (2026+2027). Prefers 2027 over 2026.
Robust tuition parsing (comma numbers, multiple table rows), lang req scoped to
지원자격 section, scholarship tier lines, majors.
"""
import os, re, json, glob
import pymupdf

FOLDERS = {
    "2027": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인",
    "2026": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인",
}
OUT = r"C:\Users\USER\camnemi-crm\backend\_deep_all.json"


def school_key(fn):
    s = re.sub(r"^0000\d+_", "", fn)
    s = re.sub(r"_20(26|27)_외국인.*", "", s)
    s = re.sub(r"\.pdf$", "", s)
    s = re.sub(r"\[.*?\]", "", s)
    return s.strip()


def norm(t):
    return re.sub(r"[ \t]+", " ", t)


def find_period(t):
    pats = [
        r"(?:원서접수|접수기간)[^.]{0,80}?((?:202[5-7])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[5-7])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
        r"((?:202[5-7])[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:202[5-7])?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
    ]
    for p in pats:
        m = re.search(p, t)
        if m:
            return re.sub(r"\s+", "", m.group(1))
    return None


def extract_lang(t):
    """Scope to 지원자격/입학자격 area if present, else whole text."""
    res = {}
    zone = t
    for kw in ["지원자격", "입학자격", "응시자격"]:
        i = t.find(kw)
        if i >= 0:
            zone = t[i:i + 3000]
            break
    m = re.search(r"TOPIK\s*(\d+)\s*급", zone)
    if m:
        res["topik"] = m.group(1)
    m = re.search(r"IELTS\s*(\d+\.?\d*)", zone)
    if m:
        res["ielts"] = m.group(1)
    m = re.search(r"TOEFL\s*(?:iBT|IBT)?\s*(\d{2,3})", zone)
    if m:
        res["toefl"] = m.group(1)
    m = re.search(r"TOEIC\s*(\d{3})", zone)
    if m:
        res["toeic"] = m.group(1)
    res["english_track"] = bool(re.search(r"영어트랙|영어능력시험|영어과정", t))
    res["kiip"] = bool(re.search(r"사회통합프로그램|KIIP", t))
    res["sejong"] = bool(re.search(r"세종학당", t))
    return res


def extract_majors(t):
    hits, seen = [], set()
    for m in re.finditer(r"([가-힣A-Za-z·&()0-9]{2,28}(?:학과|학부|전공|스쿨))", t):
        s = m.group(1)
        if len(s) >= 3 and s not in seen and not re.match(r"^(학과|학부|전공)", s):
            seen.add(s)
            hits.append(s)
    return hits[:60]


def extract_tuition(pages):
    """Find the 등록금 table page(s); collect plausible semester numbers -> min/max."""
    nums_all = []
    for p in pages:
        t = norm(p)
        if not re.search(r"등록금|수업료", t):
            continue
        # strip commas then find 6-8 digit numbers
        tt = t.replace(",", "").replace("원", " ")
        cand = [int(x) for x in re.findall(r"(?<!\d)(\d{6,8})(?!\d)", tt)]
        # plausible per-semester tuition: 1,000,000 ~ 15,000,000
        cand = [x for x in cand if 1_000_000 <= x <= 15_000_000]
        if len(cand) >= 2:
            nums_all.extend(cand)
    if len(nums_all) >= 2:
        return {"tuition_min": min(nums_all), "tuition_max": max(nums_all), "n": len(set(nums_all))}
    return None


def extract_scholarship(t):
    tier_hits = []
    # TOPIK 3급 이상 -> 40%  / TOPIK 3급 소지자 40% / IELTS 5.5 이상: 30%
    for m in re.finditer(r"(TOPIK|IELTS)[^0-9]{0,25}?(\d{1,2}(?:\.\d)?)[^0-9%]{0,40}?(\d{1,3})\s*%", t):
        s = m.group(1).upper()
        if s == "TOPIK" and float(m.group(2)) <= 6:
            tier_hits.append(f"TOPIK {m.group(2)} → {m.group(3)}%")
        elif s == "IELTS" and float(m.group(2)) <= 9:
            tier_hits.append(f"IELTS {m.group(2)} → {m.group(3)}%")
    seen, tiers = set(), []
    for x in tier_hits:
        if x not in seen:
            seen.add(x)
            tiers.append(x)
    names = []
    for m in re.finditer(r"([가-힣A-Za-z·]{2,25}장학금)", t):
        n = m.group(1)
        if n not in names and len(n) >= 4:
            names.append(n)
    return {"names": names[:15], "tiers": tiers[:30]}


def main():
    # process 2026 first, then 2027 OVERWRITES (prefer newest)
    results = {}
    for year in ("2026", "2027"):
        folder = FOLDERS[year]
        for fp in sorted(glob.glob(os.path.join(folder, "*.pdf"))):
            fn = os.path.basename(fp)
            key = school_key(fn)
            if not key:
                continue
            try:
                doc = pymupdf.open(fp)
                pages = [p.get_text() for p in doc]
                doc.close()
            except Exception as e:
                results[key] = {"year": year, "error": str(e)}
                continue
            full = "\n".join(pages)
            n = norm(full)
            results[key] = {
                "year": year,
                "period": find_period(n),
                "lang": extract_lang(n),
                "majors": extract_majors(n),
                "tuition": extract_tuition(pages),
                "scholarship": extract_scholarship(n),
                "pages": len(pages),
                "text_chars": len(full),
            }
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n2027 = sum(1 for v in results.values() if v.get("year") == "2027")
    n_tuit = sum(1 for v in results.values() if v.get("tuition"))
    n_per = sum(1 for v in results.values() if v.get("period"))
    n_tier = sum(1 for v in results.values() if v.get("scholarship", {}).get("tiers"))
    n_topik = sum(1 for v in results.values() if v.get("lang", {}).get("topik"))
    n_ielts = sum(1 for v in results.values() if v.get("lang", {}).get("ielts"))
    print(f"총 {len(results)}개 학교 | 2027 우선 반영: {n2027}")
    print(f"기간: {n_per} | 학비: {n_tuit} | 장학등급: {n_tier} | TOPIK: {n_topik} | IELTS: {n_ielts}")


if __name__ == "__main__":
    main()
