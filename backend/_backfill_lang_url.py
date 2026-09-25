# -*- coding: utf-8 -*-
"""Backfill lang_programs guide_url from _guide_2027_master.json lang_url."""
import json, os

BASE = r"C:\Users\wisew\camnemi-crm\backend"
KB = os.path.join(BASE, "verified_kb.json")
M = os.path.join(BASE, "_guide_2027_master.json")

kb = json.load(open(KB, encoding="utf-8"))
master = json.load(open(M, encoding="utf-8"))
L = kb["lang_programs"]["schools"]

# build lookup: master school key -> lang_url
lu = {}
for r in master:
    u = r.get("lang_url", "")
    if isinstance(u, str) and u.startswith("http"):
        lu[r.get("school", "")] = u.split(" ")[0]

def resolve(name):
    """Map a lang KB key (short) to a master lang_url."""
    if name in lu:
        return lu[name]
    # short name likely ends in 대 / 대학교; master uses full 대학교
    for cand in (name + "대학교", name + "학교", name + "대학"):
        if cand in lu:
            return lu[cand]
    # master key might be '가천대학교' while KB is '가천대' — try stripping
    return None

filled = 0
already = 0
remain = []
for n, v in L.items():
    if v.get("guide_url") and v["guide_url"].startswith("http"):
        already += 1
        continue
    url = resolve(n)
    if url:
        v["guide_url"] = url
        filled += 1
    else:
        remain.append(n)

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"lang guide_url: 기존 {already} + 채움 {filled} = {already+filled}/{len(L)}")
print(f"못 찾음: {len(remain)}")
for n in remain[:20]:
    print("  ", n)
