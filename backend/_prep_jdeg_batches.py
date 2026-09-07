# -*- coding: utf-8 -*-
"""Create batches for junior degree-PDF download. Skip schools whose PDF already
exists in the local junior-guide folder. Batch into ~12 each."""
import json, os, re

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]

SRC_DEG = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
os.makedirs(SRC_DEG, exist_ok=True)
# existing PDFs
have = set()
if os.path.isdir(SRC_DEG):
    for fn in os.listdir(SRC_DEG):
        if fn.endswith(".pdf"):
            nm = re.sub(r"_(20\d\d|전문학사|모집요강|최종|외국인).*", "", fn)
            have.add(nm.replace("_", ""))

need = []
for n, v in js.items():
    if not v.get("guide_url"):
        continue
    # skip if pdf exists
    sn = re.sub(r"\[.*?\]", "", n).replace("대학교", "").replace("대학", "").replace(" ", "")
    if any(sn in h or h in sn for h in have):
        continue
    need.append({"school": n, "guide_url": v["guide_url"], "region": v.get("region"),
                 "topik_req": v.get("topik_req"), "ielts_req": v.get("ielts_req")})

print(f"PDF 확보 필요 전문대: {len(need)} (guide_url 보유 중 로컬 PDF 없는 것)")
json.dump(need, open(r"C:\Users\USER\camnemi-crm\backend\_junior_deg_need.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

BATCH = 10
batches = [need[i:i+BATCH] for i in range(0, len(need), BATCH)]
for i, b in enumerate(batches):
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_jdeg_batch{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"배치 {len(batches)}개")
for i, b in enumerate(batches):
    print(f"  batch{i} ({len(b)}): {', '.join(x['school'] for x in b)}")
