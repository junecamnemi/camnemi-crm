#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Daily 04:00 NEW-2027-guide detector.
For every school/program that does NOT yet have a 2027 guide, visit its
guide_page_url and check whether a 2027 모집공고 has appeared. Only reports
NEWLY-detected 2027 (not already-known). Skips schools that already have 2027.

State: _guide_2027_detected.json  {school: {level, year, page_url, title, first_seen}}
Output: prints NEW detections (cron delivers); silent if none.
"""
import os, re, json, datetime
from collections import Counter

BASE = r"C:\Users\wisew\camnemi-crm\backend"
STATE = os.path.join(BASE, "_guide_2027_detected.json")
YEAR_KW = re.compile(r"(20\d\d)")

def load_known_2027():
    """Schools already known to have a 2027 guide (from page-discovery results)."""
    known = set()
    for f in ["_guide_pages.json", "_junior_guide_pages.json", "_lang_guide_pages.json"]:
        p = os.path.join(BASE, f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for n, v in d.items():
            if v.get("year") == "2027":
                known.add(n)
    return known

def load_targets():
    """All schools with a guide_page_url, grouped by level."""
    kb = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))
    targets = {}  # school -> (level, page_url)
    for sec, sub, lvl in [("schools", None, "ba"), ("master", "schools", "ma"),
                          ("junior", "schools", "junior"), ("lang_programs", "schools", "lang")]:
        try:
            d = kb[sec][sub] if sub else kb[sec]
        except Exception:
            continue
        for n, v in d.items():
            u = v.get("guide_page_url", "")
            if isinstance(u, str) and u.startswith("http"):
                targets.setdefault(n, (lvl, u))
    return targets

def main():
    from playwright.sync_api import sync_playwright
    known = load_known_2027()
    targets = load_targets()
    # only schools WITHOUT 2027
    todo = {n: v for n, v in targets.items() if n not in known}
    print(f"2027 미보유 대상: {len(todo)}교 (전체 {len(targets)}, 이미 2027 {len(known)})")

    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    today = datetime.date.today().isoformat()
    new_found = []

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36")
        pg = ctx.new_page()
        for name, (level, url) in todo.items():
            # skip if already detected in a prior run
            if name in state and state[name].get("year") == "2027":
                continue
            try:
                try:
                    pg.goto(url, timeout=15000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(1200)
                pg.wait_for_timeout(1200)
                txt = pg.inner_text("body")[:4000]
                # 2027 + recruiting keywords
                if "2027" in txt and re.search(r"(모집|입학|요강|외국인|유학생)", txt):
                    m = YEAR_KW.search(txt)
                    year = m.group(1) if m else "2027"
                    state[name] = {"level": level, "year": year, "page_url": url,
                                   "title": pg.title()[:80], "first_seen": today}
                    new_found.append((name, level, url))
            except Exception:
                pass  # unreachable/error -> skip silently
        b.close()

    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    if not new_found:
        print("[SILENT]")
        return
    print(f"🆕 2027 신규 모집공고 감지: {len(new_found)}교")
    for n, lvl, u in new_found:
        print(f"  [{lvl}] {n} -> {u[:80]}")

if __name__ == "__main__":
    main()
