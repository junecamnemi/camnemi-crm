# -*- coding: utf-8 -*-
"""Create PDF-collection batches. MA(75) is the big one -> batches of 8.
BA(5), JR(7), LANG(16) also batched. Each agent downloads to the target folder."""
import json

def batches(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

MA = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_collect_MA.json",encoding="utf-8"))
BA = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_collect_BA.json",encoding="utf-8"))
JR = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_collect_JR.json",encoding="utf-8"))
LANG = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_collect_LANG.json",encoding="utf-8"))

# MA batches of 8
mb = batches(MA, 8)
for i,b in enumerate(mb):
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_ma_pdf_batch{i}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"MA 배치: {len(mb)}개")

# BA single batch
json.dump(BA, open(r"C:\Users\USER\camnemi-crm\backend\_ba_pdf_batch0.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(JR, open(r"C:\Users\USER\camnemi-crm\backend\_jr_pdf_batch0.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
lb = batches(LANG, 8)
for i,b in enumerate(lb):
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_lang_pdf_batch{i}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"BA {len(BA)} | JR {len(JR)} | LANG 배치 {len(lb)}")

# print batch contents for dispatch
for i,b in enumerate(mb):
    print(f"MA_{i} ({len(b)}): {', '.join(b)}")
