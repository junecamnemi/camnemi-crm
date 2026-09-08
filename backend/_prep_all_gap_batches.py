# -*- coding: utf-8 -*-
"""Prepare comprehensive online-lookup batches for ALL remaining gaps:
- BA 수업료 갭 (46) + MA 수업료 갭 (23)  -> online official tuition lookup
- 어학연수 수업료 갭 (87)
- 전문학사 지원시기 갭 (117)
Each entry gets school, level, and the guide_url / known source if available."""
import json, re, os

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
db = json.load(open(r"C:\Users\USER\camnemi-crm\backend\consulting_db.json", encoding="utf-8"))

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")

# source URL lookups
guide_map = KB.get("guide",{})   # school -> ref_url (drive)
junior_url = {n: v.get("guide_url","") for n,v in KB["junior"]["schools"].items()}
lang_pdf = KB["lang_programs"]["schools"]

# 1) BA tuition gap
ba_need=[]
for name, s in db["schools"].items():
    prog=s["programs"].get("BA")
    if prog and not prog.get("tuition"):
        gu = guide_map.get(name,{}).get("ref_url","") if isinstance(guide_map.get(name),dict) else ""
        ba_need.append({"school":name,"level":"BA","source":gu or s.get("region","")})
print(f"BA 수업료 갭: {len(ba_need)}")

# 2) MA tuition gap
ma_need=[]
for name, s in db["schools"].items():
    prog=s["programs"].get("MA")
    if prog and not prog.get("tuition"):
        ma_need.append({"school":name,"level":"MA","source":s.get("region","")})
print(f"MA 수업료 갭: {len(ma_need)}")

# 3) lang tuition gap
lang_need=[]
for name, s in db["schools"].items():
    prog=s["programs"].get("어학연수")
    if prog and not prog.get("tuition"):
        lang_need.append({"school":name,"level":"어학","source":lang_pdf.get(name,{}).get("guide_pdf","")})
print(f"어학 수업료 갭: {len(lang_need)}")

# 4) junior period gap
jr_need=[]
for name, s in db["schools"].items():
    prog=s["programs"].get("전문학사")
    if prog and not prog.get("period"):
        jr_need.append({"school":name,"level":"전문학사","source":junior_url.get(name,"")})
print(f"전문학사 지원시기 갭: {len(jr_need)}")

# save all
json.dump({"BA":ba_need,"MA":ma_need,"lang":lang_need,"junior":jr_need},
          open(r"C:\Users\USER\camnemi-crm\backend\_all_gaps.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# make per-level batch files (10 each)
all_levels = {"BA":ba_need,"MA":ma_need,"lang":lang_need,"junior":jr_need}
for lv, items in all_levels.items():
    B=10
    n_batch=(len(items)+B-1)//B
    for i in range(n_batch):
        json.dump(items[i*B:(i+1)*B], open(rf"C:\Users\USER\camnemi-crm\backend\_gap_{lv}_{i}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{lv}: {len(items)}개 → {n_batch} 배치")
