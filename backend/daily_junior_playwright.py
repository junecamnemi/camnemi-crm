#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Junior-foreigner-guide reinforcement collection via Playwright (browser).
Handles the ~80 'no_pdf_link' + error 전문대 whose admission pages are JS-rendered
or serve the guide through a JS download button that `requests` cannot follow.
Saves any found 2027/2026 외국인 guide into guides/junior/{year}/.
Output: _junior_playwright_collected.json (status: downloaded / no_guide / error)
"""
import os, re, json, datetime, urllib.request, ssl

BASE = r"C:\Users\USER\camnemi-crm\backend"
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = os.path.join(BASE, "_junior_playwright_collected.json")

def load_targets():
    """Load the failed junior schools from the requests-based collector."""
    r = json.load(open(os.path.join(BASE, "_junior_direct_collected.json"), encoding="utf-8"))
    bad = {n: v for n, v in r.items()
           if v.get("status") in ("no_pdf_link",) or str(v.get("status", "")).startswith("error")}
    # also include no_url
    for n, v in r.items():
        if v.get("status") == "no_url":
            bad.setdefault(n, v)
    return {n: v.get("url", "") for n, v in bad.items()}

def main():
    from playwright.sync_api import sync_playwright
    targets = load_targets()
    print(f"보강 대상: {len(targets)}개 전문대")
    result = {}
    today = datetime.date.today().isoformat()

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                            accept_downloads=True)
        pg = ctx.new_page()
        for name, url in targets.items():
            if not url or not url.startswith("http"):
                result[name] = {"status": "no_url", "checked": today}
                continue
            try:
                pg.goto(url, timeout=30000, wait_until="domcontentloaded")
                pg.wait_for_timeout(2500)
                # find PDF/HWP links (direct href)
                cands = pg.eval_on_selector_all(
                    "a[href*='.pdf'], a[href*='.hwp'], a[href*='FileDown'], a[href*='download'], a[href*='attach']",
                    "els => els.map(e => e.href)")
                # prefer foreigner/2027
                picks = [c for c in cands if re.search(r'외국인|foreign|international|2027', c, re.I)]
                if not picks:
                    picks = cands
                if not picks:
                    result[name] = {"status": "no_guide", "url": url, "checked": today}
                    continue
                src = picks[0]
                year = "2027" if "2027" in src else ("2026" if "2026" in src else "unknown")
                d = os.path.join(UP, "guides", "junior", "2027" if year == "2027" else "2026")
                os.makedirs(d, exist_ok=True)
                fname = f"{name}_외국인모집요강_{year}.pdf"
                path = os.path.join(d, fname)
                if not os.path.exists(path):
                    with pg.expect_download(timeout=30000) as dl:
                        try:
                            pg.click(f"a[href='{src}']")
                        except Exception:
                            pg.goto(src, timeout=30000)
                    dl.value.save_as(path)
                result[name] = {"status": "downloaded", "year": year, "saved": path, "url": src, "checked": today}
            except Exception as e:
                result[name] = {"status": f"error:{type(e).__name__}", "url": url, "checked": today}
        b.close()

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    st = Counter(v["status"] for v in result.values())
    dl = sum(1 for v in result.values() if v["status"] == "downloaded")
    print(f"완료: {len(result)} | 다운로드 {dl} | 상태 {dict(st)}")
    print(f"저장: {OUT}")

if __name__ == "__main__":
    main()
