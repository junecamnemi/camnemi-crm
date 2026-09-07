# -*- coding: utf-8 -*-
"""DEEP extractor v3 — BA (2026/2027) + MA guides.
Fixes: period scanning per-page (전형일정 tables), tuition only from 등록금 table
pages (exclude dorm/admission fees by min threshold & section context),
lang req searched across whole doc but anchored on TOPIK N급/IELTS X patterns.
Writes backend/_deep_all_v3.json keyed by school name.
"""
import os, re, json, glob
import pymupdf

FOLDERS = {
    "ba2027": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인",
    "ba2026": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인",
    "ma": r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강",
}
OUT = r"C:\Users\USER\camnemi-crm\backend\_deep_all_v3.json"


def school_key(fn, kind):
    s = fn
    if kind == "ma":
        s = s.replace("_대학원_모집요강", "").replace("_2026전기_일반대학원_국문", "").replace("_2026전기_일반대학원_영문", "").replace("_2026후기1차_일반대학원", "").replace("_외국인전형_일반대학원", "")
    else:
        s = re.sub(r"^0000\d+_", "", s)
        s = re.sub(r"_20(26|27)_외국인.*", "", s)
        s = re.sub(r"\[.*?\]", "", s)
    return s.replace(".pdf", "").strip()


def norm(t):
    return re.sub(r"[ \t]+", " ", t)


def find_period_pages(pages):
    """Scan each page for a 접수 date line (전형일정)."""
    for p in pages:
        t = norm(p)
        if not re.search(r"접수|모집기간", t):
            continue
        pats = [
            r"(?:원서접수|접수기간|인터넷\s*접수)[^.]{0,120}?((?:20[0-9]{2})[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20[0-9]{2})?[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
            r"((?:20[0-9]{2})[.\-년]\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?\s*[~～\-]\s*(?:20[0-9]{2})[.\-년]?\s*\d{1,2}[.\-월]\s*\d{1,2}[.\-일]?)",
        ]
        for pat in pats:
            m = re.search(pat, t)
            if m:
                return re.sub(r"\s+", "", m.group(1))
    return None


def extract_lang(t):
    res = {}
    zone = t
    for kw in ["지원자격", "입학자격"]:
        i = t.find(kw)
        if i >= 0:
            zone = t[i:i + 3500]
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
    # fall back to whole doc if not found in zone
    if "topik" not in res:
        m = re.search(r"TOPIK\s*(\d+)\s*급", t)
        if m:
            res["topik"] = m.group(1)
    if "ielts" not in res:
        m = re.search(r"IELTS\s*(\d+\.?\d*)", t)
        if m:
            res["ielts"] = m.group(1)
    res["english_track"] = bool(re.search(r"영어트랙|영어능력시험|영어과정|English Track", t))
    res["kiip"] = bool(re.search(r"사회통합프로그램|KIIP", t))
    res["sejong"] = bool(re.search(r"세종학당", t))
    return res


def extract_tuition(pages):
    """Find pages whose main topic is 등록금/수업료 table; collect per-semester values.
    Exclude dorm/living (~<1.2M) and admission-fee-only rows via context checks."""
    best = None
    for p in pages:
        t = norm(p)
        # page must be about tuition, not just mention it
        if not re.search(r"등록금|수업료\s*일람|학기당|등록금표", t):
            continue
        # heuristics: many distinct 7-digit numbers and 계열 words
        tt = t.replace(",", "")
        nums = [int(x) for x in re.findall(r"(?<!\d)(\d{6,8})(?!\d)", tt)]
        nums = [x for x in nums if 1_200_000 <= x <= 15_000_000]
        dept_words = sum(1 for w in ["인문", "사회", "공학", "자연", "예체능", "이학", "보건", "간호", "경영"] if w in t)
        if len(nums) >= 2 and dept_words >= 1:
            # filter obvious non-tuition (dorm amounts ~1.03M, meal etc.) - min 1.2M already
            cand = nums
            # If page ALSO has dorm info w/ larger spread, still keep min/max of full-tuition cluster:
            # use numbers that repeat in same magnitude band -> simply min/max
            if best is None or (max(cand) - min(cand)) <= (best[1] - best[0]) or len(cand) > 3:
                best = (min(cand), max(cand), len(set(cand)))
    if best:
        return {"tuition_min": best[0], "tuition_max": best[1], "n": best[2]}
    return None


def extract_scholarship(t):
    tier_hits = []
    for m in re.finditer(r"(TOPIK|IELTS)[^0-9]{0,25}?(\d{1,2}(?:\.\d)?)[^0-9%]{0,45}?(\d{1,3})\s*%", t):
        s = m.group(1).upper()
        try:
            val = float(m.group(2))
        except ValueError:
            continue
        if s == "TOPIK" and val <= 6:
            tier_hits.append(f"TOPIK {m.group(2)} → {m.group(3)}%")
        elif s == "IELTS" and val <= 9:
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
    results = {}  # key = f"{level}:{school_name}"
    for kind, folder in FOLDERS.items():
        for fp in sorted(glob.glob(os.path.join(folder, "*.pdf"))):
            fn = os.path.basename(fp)
            key = school_key(fn, kind)
            if not key:
                continue
            level = "ma" if kind == "ma" else "ba"
            year = "2026" if kind == "ba2026" else ("2027" if kind == "ba2027" else "ma")
            fkey = f"{level}:{key}"
            if level == "ba" and fkey in results:
                # keep newest: 2027 overrides 2026
                if results[fkey].get("year") == "2027":
                    continue
            try:
                doc = pymupdf.open(fp)
                pages = [p.get_text() for p in doc]
                doc.close()
            except Exception as e:
                results.setdefault(fkey, {"level": level, "school": key, "year": year})["error"] = str(e)
                continue
            full = "\n".join(pages)
            n = norm(full)
            prev = results.get(fkey, {})
            results[fkey] = {
                "level": level,
                "school": key,
                "year": year,
                "period": find_period_pages(pages) or prev.get("period"),
                "lang": extract_lang(n),
                "majors": sorted(set(prev.get("majors", []) + [m for m in re.findall(r"([가-힣A-Za-z·&()0-9]{2,28}(?:학과|학부|전공|스쿨))", n) if len(m) >= 3][:50])),
                "tuition": extract_tuition(pages) or prev.get("tuition"),
                "scholarship": extract_scholarship(n),
                "text_chars": len(full),
            }
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ba = {k: v for k, v in results.items() if k.startswith("ba:")}
    ma = {k: v for k, v in results.items() if k.startswith("ma:")}
    n_per = sum(1 for v in results.values() if v.get("period"))
    n_tuit = sum(1 for v in results.values() if v.get("tuition"))
    n_tier = sum(1 for v in results.values() if v.get("scholarship", {}).get("tiers"))
    n_topik = sum(1 for v in results.values() if v.get("lang", {}).get("topik"))
    print(f"BA: {len(ba)} | MA: {len(ma)}")
    print(f"기간: {n_per} | 학비: {n_tuit} | 장학등급: {n_tier} | TOPIK: {n_topik}")


if __name__ == "__main__":
    main()
