# -*- coding: utf-8 -*-
import json, os, collections
kb = json.load(open("verified_kb.json", encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)
fields = ["guide_pdf", "guide_effective_pdf"]
bad, tot = [], 0
for s, v in ms.items():
    if not isinstance(v, dict):
        continue
    for f in fields:
        p = v.get(f)
        if isinstance(p, str) and p:
            tot += 1
            if not os.path.exists(p):
                bad.append((s, f, p))
print(f"guide_pdf/guide_effective_pdf paths: {tot}, missing on disk: {len(bad)}")
for s, f, p in bad:
    print(f"  MISSING {s} {f}: {p}")