#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze the review batch: auto-flag high-confidence guide URLs for scrape_map.

Tier A = direct guide PDF (url .pdf/.hwp or download endpoint + guide anchor)
Tier B = guide-list/department page (guide keyword in url/anchor, likely the guide page)
Candidates -> each school a single best guess.
"""
import json, re, os

B = r"C:\Users\wisew\camnemi-crm\backend"
batch = json.load(open(os.path.join(B, "_guide_review_batch.json"), encoding="utf-8"))
GUIDE = re.compile(r"모집요강|외국인|재외국민|graduate|general|foreign|international|yogang|mojib|notice", re.I)
PDF = re.compile(r"\.(pdf|hwp|hml|docx?)([?#]|$)|download\.do|fileview|/file/|filedown|boiled|nullFile", re.I)

def classify(p):
    u = p["url"]; a = p.get("anchor", "") or ""
    ispdf = bool(PDF.search(u))
    isguide = bool(GUIDE.search(u + " " + a))
    if ispdf and isguide:
        return "A"
    if ispdf and not isguide:
        return "B"
    if isguide and not ispdf:
        return "C"
    return "D"

tierA = {}; tierB = {}; result = []
for c in batch["candidates"]:
    picks = c["picks"]
    tA = [p for p in picks if classify(p) == "A"]
    tB = [p for p in picks if classify(p) == "B"]
    # choose best: A then B (prefer highest score, prefer guide anchor)
    best = None; tier = None
    if tA:
        best = max(tA, key=lambda p: (p["score"], len(p.get("anchor") or "")))
        tier = "A"
    elif tB:
        best = max(tB, key=lambda p: (p["score"], len(p.get("anchor") or "")))
        tier = "B"
    run = {"school": c["school"], "level": c["level"], "tier": tier,
           "url": best["url"] if best else picks[0]["url"],
           "anchor": (best or picks[0]).get("anchor", "")[:40]}
    if tier == "A":
        tierA.setdefault(c["level"], []).append(run)
    elif tier == "B":
        tierB.setdefault(c["level"], []).append(run)
    result.append(run)

# summary
for lvl in ["ba", "ma", "junior", "lang"]:
    a = tierA.get(lvl, []); b = tierB.get(lvl, [])
    print(f"[{lvl}] TierA(직접PDF) {len(a)} | TierB(페이지) {len(b)}")
    for r in a[:8]:
        print(f"    A ▸ {r['school'][:20]:20s} {r['url'][:60]}")

# save a confirm-ready scrape_map (only tier A as auto-suggest)
sm_path = os.path.join(B, "scrape_map.json")
sm = json.load(open(sm_path, encoding="utf-8")) if os.path.exists(sm_path) else {}
suggest = {}
for r in result:
    if r["tier"] == "A":
        suggest.setdefault(r["school"], {})[r["level"]] = {"url": r["url"], "tier": "A",
                                                           "anchor": r["anchor"], "review": "auto-suggested"}
json.dump(batch_meta := {"tierA": tierA, "tierB": tierB},
          open(os.path.join(B, "_guide_review_tiers.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# DON'T auto-apply — write a separate suggestion for review
json.dump(suggest, open(os.path.join(B, "_scrape_suggest_A.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nTier A 자동제안: {sum(len(v) for v in suggest.values())}건 → _scrape_suggest_A.json (검토용)")