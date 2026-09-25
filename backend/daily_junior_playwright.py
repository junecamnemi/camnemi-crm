#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Junior-foreigner-guide reinforcement via Playwright: navigate school admission
page -> find 외국인/모집 insert -> click PDF download button -> save to guides/junior/{year}/.
Handles JS-rendered pages and JS download buttons that `requests` can't.
Output: _junior_playwright_collected.json
"""
import os, re, json, datetime

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = os.path.join(BASE, "_junior_playwright_collected.json")

def load_targets():
    r = json.load(open(os.path.join(BASE, "_junior_direct_collected.json"), encoding="utf-8"))
    bad = {}
    for n, v in r.items():
        if v.get("status") in ("no_pdf_link", "no_url") or str(v.get("status", "")).startswith("error"):
            bad[n] = v.get("url", "")
    return bad

def norm_year(fname):
    m = re.search(r"(20\d\d)", fname)
    return m.group(1) if m else "unknown"

def main():
    from playwright.sync_api import sync_playwright
    targets = load_targets()
    print(f"보강 대상: {len(targets)}")
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
            got = {"status": "no_guide", "url": url, "checked": today}
            try:
                try:
                    pg.goto(url, timeout=25000, wait_until="domcontentloaded")
                except Exception:
                    # interrupted by redirect/new-window — wait & re-read current page
                    pg.wait_for_timeout(3000)
                pg.wait_for_timeout(2500)
                # 1) prefer a download button (has-text needs quotes)
                dl_selectors = ["text=PDF 다운로드", "text=다운로드", "text=PDF뷰어 다운로드",
                                "a:has-text('외국인')", "a:has-text('모집요강')", "a:has-text('요강')"]
                for sel in dl_selectors:
                    # first check if selector/text exists
                    try:
                        if pg.locator(sel).count() == 0:
                            continue
                        with pg.expect_download(timeout=12000) as dl:
                            pg.click(sel, timeout=6000)
                        f = dl.value
                        year = norm_year(f.suggested_filename)
                        ydir = "2027" if year == "2027" else ("2026" if year == "2026" else "unknown")
                        d = os.path.join(UP, "guides", "junior", ydir)
                        os.makedirs(d, exist_ok=True)
                        path = os.path.join(d, f"{name}_외국인모집요강_{year}.pdf")
                        f.save_as(path)
                        got = {"status": "downloaded", "year": year, "saved": path,
                               "url": url, "file": f.suggested_filename, "checked": today}
                        break
                    except Exception as e:
                        continue  # try next selector
                # 2) fallback: any attached PDF link
                if got["status"] != "downloaded":
                    hrefs = pg.eval_on_selector_all("a", "els => els.map(e => e.href)")
                    pdfs = [h for h in hrefs if ".pdf" in h.lower()]
                    foreign = [h for h in pdfs if re.search(r"외국인|foreign|2027", h, re.I)] or pdfs
                    if foreign:
                        src = foreign[0]
                        year = "2027" if "2027" in src else ("2026" if "2026" in src else "unknown")
                        ydir = "2027" if year == "2027" else "2026"
                        d = os.path.join(UP, "guides", "junior", ydir)
                        os.makedirs(d, exist_ok=True)
                        path = os.path.join(d, f"{name}_외국인모집요강_{year}.pdf")
                        if not os.path.exists(path):
                            pg.goto(src, timeout=25000)
                            with pg.expect_download(timeout=12000) as dl:
                                pg.wait_for_timeout(1000)
                            try:
                                dl.value.save_as(path)
                            except Exception:
                                pass
                        got = {"status": "downloaded", "year": year, "saved": path, "url": src, "checked": today}
            except Exception as e:
                got = {"status": f"error:{type(e).__name__}", "err": str(e)[:120], "url": url, "checked": today}
            result[name] = got
        b.close()

    json.dump(result, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    st = Counter(v["status"] for v in result.values())
    dl = sum(1 for v in result.values() if v["status"] == "downloaded")
    print(f"완료: {len(result)} | 다운로드 {dl} | 상태 {dict(st)}")

if __name__ == "__main__":
    main()
