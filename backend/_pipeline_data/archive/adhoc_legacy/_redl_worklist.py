# -*- coding: utf-8 -*-
"""For each target school+level needing a (re)download, show the URLs we already know."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
scrape = json.load(open(os.path.join(HERE, "scrape_map.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)

TARGETS = [
    ("동국대학교", "ba"), ("수원대학교", "ba"), ("신경주대학교", "ba"), ("차의과학대학교", "ba"),
    ("부산경상대학교", "junior"), ("극동대학교", "ma"),
    ("경북대학교", "ba"), ("고신대학교", "ba"), ("국립공주대학교", "ba"), ("선문대학교", "ba"),
    ("신구대학교", "junior"), ("연세대학교", "lang"), ("연세대학교", "ma"), ("우송대학교", "ba"),
    ("이화여자대학교", "lang"), ("장안대학교", "junior"), ("한세대학교", "ba"),
]

def find(school):
    out = {}
    for k in (school, school.replace("대학교", "대")):
        if k in scrape:
            out[k] = scrape[k]
    return out

n_url = 0
for school, lv in TARGETS:
    hits = find(school)
    url = None
    for k, v in hits.items():
        ent = v.get(lv)
        if isinstance(ent, dict) and ent.get("url"):
            url = ent["url"]; src = f"scrape_map[{k}][{lv}]"
            break
        if isinstance(ent, str) and ent.startswith("http"):
            url = ent; src = f"scrape_map[{k}][{lv}]"
            break
    if not url:
        v = ms.get(school, {})
        u = None
        for f in (f"guide_url_{lv}", f"guide_url_lang" if lv == "lang" else None,
                  "guide_url", f"guide_url_{lv}_kr"):
            if f and isinstance(v, dict) and isinstance(v.get(f), str) and v[f].startswith("http"):
                u = v[f]; break
        if u:
            url, src = u, f"verified_kb[{school}].guide_url*"
    if url:
        n_url += 1
        print(f"OK   {school} [{lv}]  <- {src}\n     {url}")
    else:
        keys = list(hits) or "NOT IN scrape_map"
        print(f"NONE {school} [{lv}]  (scrape_map keys tried: {keys})")

print(f"\ntargets with a known URL: {n_url}/{len(TARGETS)}")
print("scrape_map schools:", len(scrape), "| KB schools:", len(ms))