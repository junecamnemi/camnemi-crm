#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""All-level (BA/MA/lang/junior) 모집요강 PAGE discovery via Playwright.
Goal (user 2026-09-22): find each school's 모집요강 page/notice URL so that
HTML-only announcements are captured too, not just PDF links. Covers 4년제(BA),
대학원(MA), 어학연수(lang), 전문대(junior) — every level.

Sources:
  BA  : _guide_2027_master.json  ba_url
  MA  : _guide_2027_master.json  ma_url  + verified_kb master guide_url
  lang: verified_kb lang_programs guide_url (sparse) — also try guide_pdf
  junior: verified_kb junior guide_url

Saves `_guide_pages.json`: {school: {page_url, pdf_url, year, title, html_only, status}}
"""
import os, re, json, datetime
from collections import Counter

BASE = r"C:\Users\wisew\camnemi-crm\backend"
OUT = os.path.join(BASE, "_guide_pages.json")

TITLE_KW = re.compile(r"(외국인|순수외국인|유학생|국제|foreign|international).{0,8}(모집|입학|요강)", re.I)
YEAR_KW = re.compile(r"(20\d\d)")

def load_targets():
    kb = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))
    master = json.load(open(os.path.join(BASE, "_guide_2027_master.json"), encoding="utf-8"))
    targets = {}  # school -> (level, url)
    # BA
    for rec in master:
        s = rec.get("school", "")
        u = str(rec.get("ba_url", "")).split(" ")[0]
        if s and u.startswith("http") and "drive.google" not in u:
            targets.setdefault(s, ("ba", u))
    # MA
    for rec in master:
        s = rec.get("school", "")
        u = str(rec.get("ma_url", "")).split(" ")[0]
        if s and u.startswith("http"):
            targets.setdefault(s, ("ma", u))
    try:
        ma = kb["master"]["schools"]
        for n, v in ma.items():
            u = v.get("guide_url", "")
            if isinstance(u, str) and u.startswith("http"):
                targets.setdefault(n, ("ma", u.split(" ")[0]))
    except Exception:
        pass
    # lang
    for n, v in kb.get("lang_programs", {}).get("schools", {}).items():
        u = v.get("guide_url", "") or v.get("guide_pdf", "")
        if isinstance(u, str) and u.startswith("http"):
            targets.setdefault(n, ("lang", u.split(" ")[0]))
        elif isinstance(u, str) and os.path.exists(u):
            targets.setdefault(n, ("lang", ""))  # local file, no page
    # junior
    for n, v in kb.get("junior", {}).get("schools", {}).items():
        u = v.get("guide_url", "")
        if isinstance(u, str) and u.startswith("http"):
            targets.setdefault(n, ("junior", u.split(" ")[0]))
    return targets

def main():
    from playwright.sync_api import sync_playwright
    targets = load_targets()
    print(f"대상 {len(targets)}교 (BA {sum(1 for l,_ in targets.values() if l=='ba')} / MA {sum(1 for l,_ in targets.values() if l=='ma')} / lang {sum(1 for l,_ in targets.values() if l=='lang')} / junior {sum(1 for l,_ in targets.values() if l=='junior')})")
    result = {}
    today = datetime.date.today().isoformat()

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                            accept_downloads=True)
        pg = ctx.new_page()
        for name, (level, url) in targets.items():
            rec = {"level": level, "status": "no_page", "checked": today}
            if not url:
                rec["status"] = "no_url"; result[name] = rec; continue
            try:
                try:
                    pg.goto(url, timeout=18000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(2000)
                pg.wait_for_timeout(1800)
                links = pg.eval_on_selector_all(
                    "a", "els => els.map(e => ({t:(e.innerText||'').trim(), h:e.href})).filter(x => x.t && x.h)")
                cands = [x for x in links if TITLE_KW.search(x["t"]) or re.search(r"(외국인|foreign|international)", x["h"], re.I)]
                if not cands:
                    cands = [x for x in links if re.search(r"(모집|입학|요강)", x["t"], re.I)]
                if not cands:
                    rec["title"] = pg.title()[:80]
                    result[name] = rec; continue
                def score(x):
                    s = 1
                    if re.search(r"(외국인|순수외국인|유학생|foreign|international)", x["t"] + x["h"], re.I): s += 3
                    if re.search(r"(2027|2026)", x["t"] + x["h"]): s += 2
                    if ".pdf" in x["h"].lower(): s += 1
                    if re.search(r"(모집요강|요강)", x["t"], re.I): s += 1
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
                rec["err"] = str(e)[:80]
            result[name] = rec
        b.close()

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    st = Counter(v["status"] for v in result.values())
    found = sum(1 for v in result.values() if v["status"] == "page_found")
    by_level = Counter(v.get("level") for v in result.values() if v["status"] == "page_found")
    print(f"완료: {len(result)} | page_found {found} | 상태 {dict(st)}")
    print(f"  레벨별 발견: {dict(by_level)}")

if __name__ == "__main__":
    main()