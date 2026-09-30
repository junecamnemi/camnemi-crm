# -*- coding: utf-8 -*-
"""HTML-only audit across all 4 levels: KB slots whose guide is a page (no PDF on disk).

Output: _htmlonly_targets.json  = [{school, level, year, url, src}]
"""
import json, os, re, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))

SECTIONS = {
    "ba": kb.get("schools", {}),
    "ma": kb.get("master", {}).get("schools", {}),
    "junior": kb.get("junior", {}).get("schools", {}),
    "lang": kb.get("lang_programs", {}).get("schools", {}),
}

def is_http(u):
    return isinstance(u, str) and u.startswith("http")

rows = []
for lv, sec in SECTIONS.items():
    n = has_pdf = url_only = neither = 0
    for name, v in sec.items():
        if not isinstance(v, dict):
            continue
        n += 1
        cands = [v.get("guide_effective_pdf"), v.get("guide_pdf")]
        pdf = None
        for c in cands:
            if isinstance(c, str) and c.lower().endswith((".pdf", ".hwp")) and os.path.exists(c):
                pdf = c
                break
        urls = [v.get("guide_url"), v.get("guide_page_url"), v.get("lang_src"),
                v.get("guide_pdf") if is_http(v.get("guide_pdf")) else None,
                v.get("ba_src"), v.get("lang_src")]
        url = next((u for u in urls if is_http(u)), None)
        if pdf:
            has_pdf += 1
            continue
        if url:
            url_only += 1
            rows.append({"school": name, "level": lv,
                         "year": v.get("guide_effective_year") or v.get("guide_year") or "2026",
                         "url": url, "note": v.get("note") or v.get("lang_note") or v.get("tuition_note")})
        else:
            neither += 1
    print("%-7s slots=%-4d pdf=%-4d url_only(HTML)=%-4d neither=%d" % (lv, n, has_pdf, url_only, neither))

print("\ntotal HTML-only targets:", len(rows))
print(collections.Counter(r["level"] for r in rows))
json.dump(rows, open(os.path.join(HERE, "_htmlonly_targets.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote _htmlonly_targets.json")