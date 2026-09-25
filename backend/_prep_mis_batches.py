# -*- coding: utf-8 -*-
"""Split _bypass_missing_raw.json into batches for pro structuring."""
import json, os
raw = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\_bypass_missing_raw.json", encoding="utf-8"))
items = list(raw.items())
B = 20
os.makedirs(r"C:\Users\wisew\camnemi-crm\backend\_bypass_mis_batches", exist_ok=True)
for i in range(0,len(items),B):
    json.dump(dict(items[i:i+B]), open(rf"C:\Users\wisew\camnemi-crm\backend\_bypass_mis_batches\mis_{i//B:02d}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(items)} → {(len(items)+B-1)//B} 배치")
