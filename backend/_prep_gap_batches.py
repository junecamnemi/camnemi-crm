# -*- coding: utf-8 -*-
"""Prepare batches for filling 2 gaps via online lookup:
1) 어학연수 수업료 (87 schools missing tuition)
2) 전문학사 지원시기 (junior colleges missing period)
Each agent handles ~10 schools, looks up official lang-program tuition / junior admission period."""
import json, os, re

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
lp = KB["lang_programs"]["schools"]
jr = KB["junior"]["schools"]

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")

# 1) lang tuition gap - schools with guide_url or a lang page we can check
lang_gap = []
for n, v in lp.items():
    if v.get("tuition_range"): continue
    lang_gap.append({"school": n, "region": v.get("region"), "guide_pdf": v.get("guide_pdf"),
                     "guide_url": v.get("guide_url","")})
print(f"어학연수 수업료 갭: {len(lang_gap)}개")

# 2) junior period gap - not_checked or missing period
jr_gap = []
for n, v in jr.items():
    if v.get("period"): continue
    # skip closed/merged
    if v.get("foreign_guide") in ("closed","merged"): continue
    if v.get("guide_url"):
        jr_gap.append({"school": n, "region": v.get("region"), "guide_url": v["guide_url"]})
print(f"전문학사 지원시기 갭: {len(jr_gap)}개")

# write full lists
json.dump(lang_gap, open(r"C:\Users\USER\camnemi-crm\backend\_gap_lang_tuition.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(jr_gap, open(r"C:\Users\USER\camnemi-crm\backend\_gap_junior_period.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# batches of 10 for lang
B=10
for i in range(0, len(lang_gap), B):
    json.dump(lang_gap[i:i+B], open(rf"C:\Users\USER\camnemi-crm\backend\_langtui_batch{i//B}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"어학 수업료 배치: {(len(lang_gap)+B-1)//B}개")
for i in range(0, len(jr_gap), B):
    json.dump(jr_gap[i:i+B], open(rf"C:\Users\USER\camnemi-crm\backend\_jrperiod_batch{i//B}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"전문학사 지원시기 배치: {(len(jr_gap)+B-1)//B}개")
