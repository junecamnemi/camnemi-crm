#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Promote ALL discovered candidates (tier A or B, best pick) into scrape_map for monitoring.
Tier A = direct guide PDF; Tier B = guide page (checker will resolve page->pdf)."""
import json, os, re, datetime
B = r"C:\Users\USER\camnemi-crm\backend"
batch = json.load(open(os.path.join(B, "_guide_review_batch.json"), encoding="utf-8"))
sm = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
today = datetime.date.today().isoformat()
GUIDE = re.compile(r"모집요강|외국인|재외국민|graduate|foreign|international|yogang|mojib|notice", re.I)
PDF = re.compile(r"\.(pdf|hwp|hml|docx?)([?#]|$)|download\.do|fileview", re.I)

def classify(p):
    u, a = p["url"], p.get("anchor","") or ""
    ispdf = bool(PDF.search(u)); isguide = bool(GUIDE.search(u+" "+a))
    if ispdf and isguide: return "A"
    if ispdf: return "B"
    if isguide: return "C"
    return "D"

added=0
for c in batch["candidates"]:
    picks=c["picks"]
    tA=[p for p in picks if classify(p)=="A"]; tB=[p for p in picks if classify(p) in ("B","C")]
    best = max(tA,key=lambda p:p["score"]) if tA else (max(tB,key=lambda p:p["score"]) if tB else picks[0])
    lvl=c["level"]
    if sm.get(c["school"],{}).get(lvl):
        continue  # already
    sm.setdefault(c["school"],{})[lvl]={"url":best["url"],"tier":("A" if tA else "B"),
                                        "anchor":best.get("anchor","")[:40],"promoted":today}
    added+=1
json.dump(sm,open(os.path.join(B,"scrape_map.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
import collections
lv=collections.Counter()
for s,d in sm.items():
    if s=="_meta":continue
    for k in d: lv[k]+=1
print(f"승격 {added}건 | scrape_map 총: {dict(lv)}")