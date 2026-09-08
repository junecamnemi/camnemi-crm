# -*- coding: utf-8 -*-
"""Create lang-tuition gap batches. Each school lacks 어학연수 tuition in KB.
Each batch writes to a UNIQUE output file (concurrency-safe)."""
import json, re

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
lp = KB["lang_programs"]["schools"]

# lang schools missing tuition
lang = []
for n, v in lp.items():
    if not v.get("tuition_range"):
        lang.append({"school": n, "region": v.get("region"),
                     "guide_pdf": v.get("guide_pdf",""), "url": v.get("guide_url","")})
print(f"어학연수 수업료 갭: {len(lang)}개")
# batches of 8
for i in range(0, len(lang), 8):
    b = lang[i:i+8]
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_langtui_{i//8}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  batch{i//8} ({len(b)}): {[x['school'] for x in b]}")
