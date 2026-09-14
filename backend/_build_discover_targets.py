#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build _discover_targets.json: {school,level,url} from master + KB URLs (own-site only, http)."""
import os, re, json

B = r"C:\Users\USER\camnemi-crm\backend"
targets = []
seen = set()

def norm(s):
    return re.sub(r"\[.*?\]", "", str(s)).replace("대학교", "대학").strip()

master_p = os.path.join(B, "_guide_2027_master.json")
if os.path.exists(master_p):
    for rec in json.load(open(master_p, encoding="utf-8")):
        s = rec.get("school", "")
        for tr, lvl in (("ba", "ba"), ("ma", "ma")):
            u = rec.get(f"{tr}_url") or ""
            u = u.split(" ")[0] if u else ""
            if u.startswith("http") and "drive" not in u:
                k = (norm(s), lvl)
                if k not in seen:
                    seen.add(k); targets.append({"school": s, "level": lvl, "url": u})

kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
for lbl, sec, lvl in [("대학원", ["master", "schools"], "ma"), ("전문대", ["junior", "schools"], "junior"), ("어학", ["lang_programs", "schools"], "lang")]:
    d = kb[sec[0]][sec[1]]
    for s, v in d.items():
        for kf in ("guide_url", "guide_pdf"):
            u = v.get(kf) or ""
            if isinstance(u, str) and u.startswith("http"):
                u = u.split(" ")[0]
                if "/download" in u or u.endswith((".pdf", ".hwp")):  # direct file, not a page
                    continue
                k = (norm(s), lvl)
                if k not in seen:
                    seen.add(k); targets.append({"school": s, "level": lvl, "url": u})

out = os.path.join(B, "_discover_targets.json")
json.dump(targets, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(f"타깃 {len(targets)}개 | 레벨: {dict(Counter(t['level'] for t in targets))}")
print("저장:", out)