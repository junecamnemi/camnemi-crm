# -*- coding: utf-8 -*-
"""Create MA tuition gap batches (each writes to a UNIQUE output file to avoid concurrency)."""
import json

need = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_all_gaps.json", encoding="utf-8"))["MA"]
# dedupe by school name
seen=set(); ma=[]
for x in need:
    if x['school'] not in seen:
        seen.add(x['school']); ma.append(x)
print(f"MA 고유 {len(ma)}개")
# batches of 7
for i in range(0,len(ma),7):
    b=ma[i:i+7]
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_ma2_batch{i//7}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"batch{i//7} ({len(b)}): {[x['school'] for x in b]}")
