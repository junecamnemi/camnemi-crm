# -*- coding: utf-8 -*-
"""Split _bypass_raw.json into batches for pro-model structuring."""
import json, os

raw = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_bypass_raw.json", encoding="utf-8"))
items = list(raw.items())
B = 20
os.makedirs(r"C:\Users\USER\camnemi-crm\backend\_bypass_batches", exist_ok=True)
for i in range(0, len(items), B):
    batch = dict(items[i:i+B])
    json.dump(batch, open(rf"C:\Users\USER\camnemi-crm\backend\_bypass_batches\bypass_{i//B:02d}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(items)}개 → {(len(items)+B-1)//B} 배치 (각 {B}개)")
