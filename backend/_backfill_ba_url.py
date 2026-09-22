# -*- coding: utf-8 -*-
"""Backfill BA/MA urls in _guide_2027_master.json from scrape_map.json."""
import json, os

BASE = r"C:\Users\USER\camnemi-crm\backend"
MP = os.path.join(BASE, "_guide_2027_master.json")

master = json.load(open(MP, encoding="utf-8"))
sm = json.load(open(os.path.join(BASE, "scrape_map.json"), encoding="utf-8"))

ba_fill = ma_fill = 0
remain_ba = remain_ma = []
for rec in master:
    s = rec["school"]
    e = sm.get(s, {})
    # BA
    if not (rec.get("ba_url") or "").startswith("http"):
        u = e.get("ba", {}).get("url", "")
        if u.startswith("http"):
            rec["ba_url"] = u.split(";")[0]
            ba_fill += 1
        else:
            remain_ba.append(s)
    # MA
    if not (rec.get("ma_url") or "").startswith("http"):
        u = e.get("ma", {}).get("url", "")
        if u.startswith("http"):
            rec["ma_url"] = u.split(";")[0]
            ma_fill += 1
        else:
            remain_ma.append(s)

json.dump(master, open(MP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"BA 보강 {ba_fill} (여전히 없음 {len(remain_ba)})")
print(f"MA 보강 {ma_fill} (여전히 없음 {len(remain_ma)})")
print("BA 남음:", remain_ba)