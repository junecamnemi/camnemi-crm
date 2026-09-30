# -*- coding: utf-8 -*-
"""Build the HTML-only render/download target list across all 4 levels.

A target = a KB slot whose effective guide is NOT a real PDF:
  * file exists but is HTML saved as .pdf  (_fake_pdf_files.json)
  * file missing entirely but a page URL is known
Writes _htmlonly_collect_targets.json with {school, level, year, url, dest, backup}
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
SEC = {"ba": kb.get("schools", {}), "ma": kb.get("master", {}).get("schools", {}),
       "junior": kb.get("junior", {}).get("schools", {}),
       "lang": kb.get("lang_programs", {}).get("schools", {})}
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
BACKUP = os.path.join(HERE, "_pipeline_data", "reports", "html_backups")
os.makedirs(BACKUP, exist_ok=True)

rows, seen = [], set()
for lv, sec in SEC.items():
    for name, v in sec.items():
        if not isinstance(v, dict):
            continue
        dest = None
        for k in ("guide_effective_pdf", "guide_pdf"):
            x = v.get(k)
            if isinstance(x, str) and x.lower().endswith((".pdf", ".hwp")):
                dest = x
                break
        if not dest:
            continue
        real = os.path.exists(dest) and open(dest, "rb").read(4) == b"%PDF"
        if real:
            continue
        url = next((v.get(k) for k in ("guide_url", "guide_page_url", "lang_src")
                    if isinstance(v.get(k), str) and v[k].startswith("http")), None)
        if not url:
            # last resort: pull a URL out of the HTML stub itself (meta refresh / canonical)
            if os.path.exists(dest) and open(dest, "rb").read(4) != b"%PDF":
                try:
                    head = open(dest, "r", encoding="utf-8", errors="ignore").read(4000)
                    import re
                    m = re.search(r"""https?://[^"'\s>)]+""", head)
                    if m:
                        url = m.group(0)
                except Exception:
                    pass
        key = (name, lv)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"school": name, "level": lv,
                     "year": v.get("guide_effective_year") or v.get("guide_year") or "2026",
                     "url": url, "dest": dest, "exists_html": os.path.exists(dest),
                     "backup": os.path.join(BACKUP, os.path.basename(dest)) if os.path.exists(dest) else None})
# add slots that have a URL but no file path at all (url-only KB slots)
import re as _re
for r in json.load(open(os.path.join(HERE, "_htmlonly_targets.json"), encoding="utf-8")):
    key = (r["school"], r["level"])
    if key in seen:
        continue
    seen.add(key)
    yr = r.get("year") or "2026"
    lv = r["level"]
    if lv == "lang":
        dest = os.path.join(G, "lang", yr, f"{r['school']}_한국어교육원_{yr}.pdf")
    elif lv == "junior":
        dest = os.path.join(G, "junior", yr, f"{r['school']}_외국인모집요강_{yr}.pdf")
    else:
        dest = os.path.join(G, lv, yr, f"{r['school']}_외국인모집요강_{yr}.pdf")
    rows.append({"school": r["school"], "level": lv, "year": yr, "url": r["url"],
                 "dest": dest, "exists_html": os.path.exists(dest), "backup": None})

json.dump(rows, open(os.path.join(HERE, "_htmlonly_collect_targets.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
import collections
print("targets:", len(rows), collections.Counter(r["level"] for r in rows))
print("no url:", sum(1 for r in rows if not r["url"]))
print("html stub present:", sum(1 for r in rows if r["exists_html"]))