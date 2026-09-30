# -*- coding: utf-8 -*-
"""Campus-aware final check: exactly one active guide per (school, campus, level, year)."""
import json, os, re, collections
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
man = json.load(open(os.path.join(G, "_library_manifest.json"), encoding="utf-8"))
act = [e for e in man["entries"] if not e.get("archived")]


def norm(n):
    return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()


def sc(f):
    parts = [p for p in re.sub(r"\.(pdf|hwp|html|docx|do)$", "", f, flags=re.I).split("_")
             if not re.fullmatch(r"\d{4,}", p)]
    name = ""
    for p in parts:
        q = norm(p)
        if q.endswith(("대학교", "대학")):
            name = q; break
    if not name:
        for p in parts:
            q = norm(p)
            if q.endswith("대") and len(q) >= 2:
                name = q; break
    if not name:
        name = norm(parts[0]) if parts else f
    cam = ""
    for p in parts:
        if norm(p) == name:
            m = re.search(r"[\[(](.*?)[\])]", p)
            if m:
                cam = m.group(1)
    return name, ("" if cam == "본교" else cam)


g = collections.defaultdict(list)
for e in act:
    g[(sc(e["name"]), e["level"], e["year"])].append(e["name"])
dups = {k: v for k, v in g.items() if len(v) > 1}
print(f"active entries: {len(act)}   (school,campus,level,year) groups: {len(g)}")
print(f"groups with >1 file: {len(dups)}")
for k, v in sorted(dups.items()):
    print("  ", k, v)
lv = collections.Counter(e["level"] for e in act)
print("active by level:", dict(lv))