#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discover Korean-language-institute (KLI) 모집/공지 PAGE urls for lang schools.
Visits each lang guide_url (KLI homepage), finds the recruiting/요강/apply page
(공지/모집/입학), records the page URL (HTML announcements included), NOT just PDF.
Output: _lang_guide_pages.json {school: {page_url,title,year,pdf_url,html_only,status}}
"""
import os, re, json, datetime
from collections import Counter

BASE = r"C:\Users\USER\camnemi-crm\backend"
OUT = os.path.join(BASE, "_lang_guide_pages.json")

TITLE_KW = re.compile(r"(외국인|유학생|어학연수|연수|입학|모집|답),?", re.I)
YEAR_KW = re.compile(r"(20\d\d)")
# recruiting words for lang
RECRUIT = re.compile(r"(모집|입학|연수|apply|recruit|application|registration|admission)", re.I)
# leave-out words that are not what we want
BAD = re.compile(r"(역량|진로|학사일정|장학|기숙사|비자|채용|교수)", re.I)

def load():
    kb = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))
    L = kb.get("lang_programs", {}).get("schools", {})
    return {n: v.get("guide_url", "") for n, v in L.items() if v.get("guide_url", "").startswith("http")}

def main():
    from playwright.sync_api import sync_playwright
    targets = load()
    print(f"lang 대상: {len(targets)}")
    result = {}
    today = datetime.date.today().isoformat()

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36")
        pg = ctx.new_page()
        for name, url in targets.items():
            rec = {"url": url, "status": "no_page", "checked": today}
            try:
                try:
                    pg.goto(url, timeout=18000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(1500)
                pg.wait_for_timeout(1500)
                links = pg.eval_on_selector_all(
                    "a", "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.href})).filter(x => x.t && x.h)")
                # recruiting pages: title mentions recruit/apply/admission + not a BAD page
                cands = [x for x in links if RECRUIT.search(x["t"]) and not BAD.search(x["t"])]
                if not cands:
                    cands = [x for x in links if TITLE_KW.search(x["t"])]
                if not cands:
                    rec["title"] = pg.title()[:60]
                    result[name] = rec
                    continue
                def score(x):
                    t = x["t"] + x["h"]
                    s = 1
                    if re.search(r"(외국인|유학생|어학연수)", t, re.I): s += 3
                    if re.search(r"(모집|입학|application|recruit)", t, re.I): s += 2
                    if re.search(r"(20\d\d)", t): s += 1
                    if ".pdf" in x["h"].lower(): s += 2
                    return s
                best = sorted(cands, key=score, reverse=True)[0]
                rec["page_url"] = best["h"]
                rec["title"] = best["t"][:80]
                m = YEAR_KW.search(best["t"] + best["h"])
                rec["year"] = m.group(1) if m else "unknown"
                rec["pdf_url"] = best["h"] if ".pdf" in best["h"].lower() else None
                rec["html_only"] = rec["pdf_url"] is None
                rec["status"] = "page_found"
            except Exception as e:
                rec["status"] = f"error:{type(e).__name__}"
                rec["err"] = str(e)[:70]
            result[name] = rec
        b.close()

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    st = Counter(v["status"] for v in result.values())
    found = sum(1 for v in result.values() if v["status"] == "page_found")
    html = sum(1 for v in result.values() if v.get("html_only"))
    pdf = sum(1 for v in result.values() if v.get("pdf_url"))
    print(f"완료: {len(result)} | page_found {found} | 상태 {dict(st)}")
    print(f"  HTML공지 {html} / PDF {pdf}")

if __name__ == "__main__":
    main()
