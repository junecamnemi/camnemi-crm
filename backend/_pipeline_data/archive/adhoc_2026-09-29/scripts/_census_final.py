# -*- coding: utf-8 -*-
"""모집요강 보유현황 (5 categories × 2026/2027) — counts only REAL guide files.

A file counts only if it is a real PDF (%PDF magic) or HWP; HTML saved as .pdf is reported
separately as 'not a real guide'. Year comes from the library folder, falling back to the
filename. Buckets: 학사 / 석사 / 어학연수(대학교) / 전문학사 / 어학연수(전문대학교).
"""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
univ = json.load(open(os.path.join(HERE, "_adiga_univ_list.json"), encoding="utf-8"))
junior = json.load(open(os.path.join(HERE, "_adiga_junior_list.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)

def norm(n): return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()
def key(n): return re.sub(r"(대학교|대학|대)$", "", norm(n))

US = {key(x) for x in univ.values()}
JS = {key(x) for x in junior.values()}
KB_SHORT = {key(s) for s in ms}

def school_of(f):
    parts = [p for p in re.sub(r"\.(pdf|hwp|html|do|php|asp|jsp)$", "", f, flags=re.I).split("_")
             if not re.fullmatch(r"\d{4,}", p)]
    for p in parts:
        q = norm(p)
        if q.endswith(("대학교", "대학")):
            return q
    for p in parts:
        q = norm(p)
        if q.endswith("대") and len(q) >= 2:
            return q
    return norm(parts[0]) if parts else f

def kind(name):
    k = key(school_of(name))
    if k in JS: return "junior"
    if k in US or k in KB_SHORT: return "univ"
    return "unknown"

LV = {"ba": "학사", "ma": "석사", "junior": "전문학사", "lang": "어학연수"}
rows = []
for root, dirs, files in os.walk(G):
    for f in files:
        if not f.lower().endswith((".pdf", ".hwp")):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, G).replace("\\", "/")
        parts = rel.split("/")
        rest = parts[parts.index("_archive") + 1:] if "_archive" in parts else parts
        lv = next((x for x in rest if x in LV), None)
        yr = next((x for x in rest if re.fullmatch(r"20\d\d", x)), None) or \
             (re.search(r"(20\d\d)", f).group(1) if re.search(r"(20\d\d)", f) else "unknown")
        try:
            head = open(p, "rb").read(4)
        except Exception:
            head = b""
        real = "pdf" if head == b"%PDF" else ("hwp" if head == b"\xd0\xcf\x11\xe0" else "html")
        rows.append(dict(level=lv, year=yr, sk=key(school_of(f)), real=real, rel=rel))

def bucket(r):
    if r["level"] == "lang":
        return {"univ": "어학연수(대학교)", "junior": "어학연수(전문대학교)"}.get(
            kind(os.path.basename(r["rel"])), "어학연수(미분류)")
    return LV.get(r["level"], "기타")

ORDER = ["학사", "석사", "어학연수(대학교)", "전문학사", "어학연수(전문대학교)", "어학연수(미분류)", "기타"]
print("%-20s %14s %14s %12s" % ("category", "2026 (files/schools)", "2027 (files/schools)", "total files"))
grand = collections.Counter()
for b in ORDER:
    rs = [r for r in rows if bucket(r) == b and r["real"] in ("pdf", "hwp")]
    if not rs:
        continue
    r26 = [r for r in rs if r["year"] == "2026"]
    r27 = [r for r in rs if r["year"] == "2027"]
    s26, s27 = {r["sk"] for r in r26}, {r["sk"] for r in r27}
    print("%-20s %6d / %-6d %6d / %-6d %6d" % (b, len(r26), len(s26), len(r27), len(s27), len(rs)))
    grand["2026"] += len(r26); grand["2027"] += len(r27); grand["total"] += len(rs)
    grand["s26"] += len(s26); grand["s27"] += len(s27)
print("%-20s %6d / %-6d %6d / %-6d %d" % ("TOTAL", grand["2026"], grand["s26"], grand["2027"], grand["s27"], grand["total"]))
html = [r for r in rows if r["real"] == "html"]
print("\nnon-guide files still in the library (HTML saved as .pdf): %d" % len(html))
print("  by bucket:", collections.Counter(bucket(r) for r in html))
other = [r for r in rows if r["year"] not in ("2026", "2027")]
print("files with other/unknown year:", len(other),
      collections.Counter((r["year"], r["level"]) for r in other))
print("\ndistinct schools over all real guide files:", len({r["sk"] for r in rows if r["real"] in ("pdf", "hwp")}))