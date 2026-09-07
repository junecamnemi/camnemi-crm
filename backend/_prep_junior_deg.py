# -*- coding: utf-8 -*-
"""Build batches of junior college (전문학사/전문대) degree-program PDF downloads.
Each school's guide_url is the admission site; agents find+download the 모집요강 PDF."""
import json, os

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]

# entries with guide_url (degree admission page)
need = []
for n, v in js.items():
    if v.get("guide_url"):
        need.append({"school": n, "name_en": v.get("name_en"), "region": v.get("region"),
                     "guide_url": v["guide_url"], "type": "junior", "topik_req": v.get("topik_req"),
                     "ielts_req": v.get("ielts_req")})

print(f"guide_url 보유 전문대: {len(need)}")
# save full need list
json.dump(need, open(r"C:\Users\USER\camnemi-crm\backend\_junior_deg_need.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# save a mapping of school->guide_url for reference (no PDF dir yet)
# Note: previously 126 junior colleges were enumerated; include those WITHOUT guide_url too? They have no source URL -> mark.
no_url = [n for n, v in js.items() if not v.get("guide_url")]
print("guide_url 없는 전문대:", len(no_url), no_url)
