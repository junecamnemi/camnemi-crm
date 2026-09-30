# -*- coding: utf-8 -*-
"""Audit the guide library against the level rule:
   4-year univ  -> ba, ma, lang   (ma only if offered)
   2-year junior-> junior, lang
   keep only the latest guide per (school, level).
Read-only. Writes _pipeline_data/reports/_library_level_audit.json
"""
import json, os, re, collections, sys

GUIDES = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_pipeline_data", "reports", "_library_level_audit.json")

manifest = json.load(open(os.path.join(GUIDES, "_library_manifest.json"), encoding="utf-8"))
entries = [e for e in manifest["entries"] if not e.get("archived")]
archived = [e for e in manifest["entries"] if e.get("archived")]

univ = json.load(open(os.path.join(HERE, "_adiga_univ_list.json"), encoding="utf-8"))
junior = json.load(open(os.path.join(HERE, "_adiga_junior_list.json"), encoding="utf-8"))

def norm_campus(n):
    return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()

UNIV = {norm_campus(v) for v in univ.values()}
JUNIOR = {norm_campus(v) for v in junior.values()}

# short-name index
def short(n):
    n = norm_campus(n)
    if n.endswith("대학교"):
        return n[:-3]
    if n.endswith("대학"):
        return n[:-2]
    return n

UNIV_SHORT = {short(x): x for x in UNIV}
JUNIOR_SHORT = {short(x): x for x in JUNIOR}

_ALIAS = {
    "명지전문대학": "명지전문대학", "인하공업전문대학": "인하공업전문대학", "우송정보대학": "우송정보대학",
    "대전보건대학": "대전보건대학교", "경기과학기술대학교": "경기과학기술대학교",
}

def classify(name):
    """return (school_key, type) type in univ/junior/unknown"""
    n = norm_campus(name)
    if n in UNIV: return n, "univ"
    if n in JUNIOR: return n, "junior"
    s = short(n)
    if n in UNIV_SHORT.values(): return n, "univ"
    if n in JUNIOR_SHORT.values(): return n, "junior"
    if s in UNIV_SHORT: return UNIV_SHORT[s], "univ"
    if s in JUNIOR_SHORT: return JUNIOR_SHORT[s], "junior"
    return n, "unknown"

def school_of(fname):
    base = re.sub(r"\.(pdf|hwp|html|docx|do|hwpx|txt)$", "", fname, flags=re.I)
    # drop a leading numeric adiga code
    parts = base.split("_")
    parts = [p for p in parts if not re.fullmatch(r"\d{4,}", p)]
    for p in parts:
        q = norm_campus(p)
        if q.endswith("대학교") or q.endswith("대학"):
            return q
    for p in parts:
        q = norm_campus(p)
        if q.endswith("대") and len(q) >= 2:
            return q
    # generic: <school>_ba / <school>_외국인모집요강_2027
    if parts:
        return norm_campus(parts[0])
    return base

rows = []
for e in entries:
    sc = school_of(e["name"])
    key, typ = classify(sc)
    if key == "2027" or key == "외국인모집요강":
        typ = "unknown"
    rows.append({"name": e["name"], "level": e["level"], "year": e["year"],
                 "bytes": e["bytes"], "school": sc, "school_norm": key, "type": typ,
                 "path": e.get("library_path") or e["path"],
                 "ext": os.path.splitext(e["name"])[1].lower(),
                 "is_pdf": e["name"].lower().endswith(".pdf")})

# level rule
def allowed(typ):
    if typ == "univ": return {"ba", "ma", "lang"}
    if typ == "junior": return {"junior", "lang"}
    return {"ba", "ma", "junior", "lang"}

vi = [r for r in rows if r["level"] not in allowed(r["type"])]
nonpdf = [r for r in rows if not r["is_pdf"]]

g = collections.defaultdict(list)
for r in rows:
    g[(r["school_norm"], r["level"])].append(r)
multi_year = {k: sorted({x["year"] for x in v}) for k, v in g.items() if len({x["year"] for x in v}) > 1}
dupes = {k: [x["name"] for x in v] for k, v in g.items() if len(v) > 1}

summary = {
    "active_entries": len(entries),
    "archived_entries": len(archived),
    "unknown_type": sum(1 for r in rows if r["type"] == "unknown"),
    "level_violations": len(vi),
    "non_pdf_active": len(nonpdf),
    "school_level_groups": len(g),
    "multi_year_groups": len(multi_year),
    "duplicate_groups": len(dupes),
    "univ_active": sum(1 for r in rows if r["type"] == "univ"),
    "junior_active": sum(1 for r in rows if r["type"] == "junior"),
}
out = {"summary": summary, "violations": vi, "non_pdf": nonpdf,
       "multi_year": {f"{k[0]}|{k[1]}": v for k, v in multi_year.items()},
       "duplicates": {f"{k[0]}|{k[1]}": v for k, v in dupes.items()},
       "unknown_schools": sorted({r["school"] for r in rows if r["type"] == "unknown"})}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(json.dumps(summary, ensure_ascii=False, indent=1))
print("\n-- violations (type vs level) --")
for r in vi: print(f"  {r['type']:8} {r['level']:6} {r['name']}")
print("\n-- non-pdf active --")
for r in nonpdf: print(f"  {r['level']:6} {r['name']}")
print("\n-- unknown-school names --")
print("  " + ", ".join(out["unknown_schools"]))
print("\n-- multi-year groups --")
for k, v in multi_year.items(): print("  ", k, v)
print("\n-- duplicates (same school+level, >1 file) --")
for k, v in sorted(dupes.items()): print("  ", k, "->", v)