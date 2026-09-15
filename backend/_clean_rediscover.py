#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean scrape_map: drop 오탐 lang picks; re-pick error entries from the review batch (best candidate).
Outputs updated scrape_map + a list for fresh discovery (error&uncovered with no usable candidate)."""
import json, re, os, datetime
B = r"C:\Users\USER\camnemi-crm\backend"
BADS = re.compile(r"\.css|\.js\b|korean\.net|\.png|\.jpg|smLogon|depart_intro", re.I)
GUIDE = re.compile(r"모집요강|외국인|재외국민|graduate|foreign|international|yogang|mojib|notice|입학", re.I)
PDF = re.compile(r"\.(pdf|hwp|hml|docx?)([?#]|$)|download\.do|fileview", re.I)

sm = json.load(open(os.path.join(B,"scrape_map.json"),encoding="utf-8"))
fp = json.load(open(os.path.join(B,"_guide_fingerprint.json"),encoding="utf-8"))
batch = json.load(open(os.path.join(B,"_guide_review_batch.json"),encoding="utf-8"))

def classify(p):
    u, a = p["url"], (p.get("anchor","") or "")
    ip = bool(PDF.search(u)); ig = bool(GUIDE.search(u+" "+a))
    if ip and ig: return "A"
    if ip: return "B"
    if ig: return "C"
    return "D"

def find_key(school, level):
    # match batch school to a scrape_map key (adiga/prefix)
    import school_keys as SK
    return school  # batch school name is already usable

removed=[]
for s, lv in list(sm.items()):
    if s=="_meta": continue
    li=lv.get("lang",{})
    u=li.get("url","")
    if BADS.search(u):
        del sm[s]["lang"]
        removed.append((s,u[:40]))
print("오탐 lang 제거:", len(removed))
for s,u in removed: print(f"  ✂ {s}: {u}")

# re-pick error entries from review batch
err_keys=[k for k,v in fp.items() if "error" in str(v.get("status",""))]
repicked=0; for_disc=set()
for k in err_keys:
    school, level = k.rsplit("_",1)
    # find candidate for this school+level in batch
    best=None
    for c in batch["candidates"]:
        if c["level"]==level and (c["school"] in school or school in c["school"]):
            picks=c["picks"]; tA=[p for p in picks if classify(p)=="A"]; tB=[p for p in picks if classify(p) in("B","C")]
            cand=max(tA,key=lambda p:p["score"]) if tA else (max(tB,key=lambda p:p["score"]) if tB else None)
            if cand: best=(c["school"], cand)
    if best and not BADS.search(best[1]["url"]):
        sm.setdefault(school,{})[level]={"url":best[1]["url"],"tier":classify(best[1]),
                                          "repicked":datetime.date.today().isoformat()}
        repicked+=1
    else:
        for_disc.add((school,level))
print(f"\n오류 항목 재선택: {repicked} | 신규 발견 필요: {len(for_disc)}")

json.dump(sm, open(os.path.join(B,"scrape_map.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
json.dump(sorted(list(for_disc)), open(os.path.join(B,"_rediscover_list.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("저장: scrape_map (정리) + _rediscover_list.json")