# -*- coding: utf-8 -*-
"""Re-prep batches for the remaining uncollected: junior(7) + BA(4). One per task to avoid rate limits."""
import json

junior = ["계원예술대학교","농협대학교","대구과학대학교","부산여자대학교","영남외국어대학","영남이공대학교","충남도립대학교"]
ba = ["대구예술대학교","호서대학교","세한대학교","광주가톨릭대학교"]

# lookup guide_url from junior KB
KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
jr = KB["junior"]["schools"]

for s in junior:
    gu = jr.get(s,{}).get("guide_url","")
    entry = {"school": s, "guide_url": gu, "region": jr.get(s,{}).get("region","")}
    json.dump([entry], open(rf"C:\Users\USER\camnemi-crm\backend\_jr_retry_{s}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"jr: {s} | {gu}")

for s in ba:
    json.dump([s], open(rf"C:\Users\USER\camnemi-crm\backend\_ba_retry_{s}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ba: {s}")
