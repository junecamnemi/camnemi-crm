#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download PDFs for newly-detected 2027 guides, then re-parse into KB.
For each school in _guide_2027_detected.json (year==2027, not yet downloaded):
  - visit its page_url, find the 2027 외국인 모집요강 PDF link
  - download into guides/{level}/{2027}/
  - mark downloaded in state
Then run guide_auto_analyze.py to re-parse new PDFs into verified_kb.
"""
import os, re, json, datetime, urllib.request, ssl

BASE = r"C:\Users\wisew\camnemi-crm\backend"
UP = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
STATE = os.path.join(BASE, "_guide_2027_detected.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
           "Accept-Language": "ko-KR,ko;q=0.9"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
    return r.read()

def main():
    from playwright.sync_api import sync_playwright
    state = json.load(open(STATE, encoding="utf-8"))
    # targets: 2027 detected, not yet downloaded
    todo = {n: v for n, v in state.items()
            if v.get("year") == "2027" and not v.get("downloaded")}
    print(f"다운로드 대상: {len(todo)}교")
    downloaded = 0

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        ctx = b.new_context(user_agent="Mozilla/5.0", accept_downloads=True)
        pg = ctx.new_page()
        for name, v in todo.items():
            url = v.get("page_url", "")
            level = v.get("level", "ba")
            if not url.startswith("http"):
                continue
            try:
                try:
                    pg.goto(url, timeout=20000, wait_until="domcontentloaded")
                except Exception:
                    pg.wait_for_timeout(1500)
                pg.wait_for_timeout(1500)
                # find PDF link
                hrefs = pg.eval_on_selector_all("a", "els => els.map(e => e.href)")
                pdfs = [h for h in hrefs if ".pdf" in h.lower()]
                foreign = [h for h in pdfs if re.search(r"외국인|foreign|2027", h, re.I)] or pdfs
                if not foreign:
                    state[name]["note"] = "no_pdf_link"
                    continue
                src = foreign[0]
                d = os.path.join(UP, "guides", level, "2027")
                os.makedirs(d, exist_ok=True)
                fname = f"{name}_외국인모집요강_2027.pdf"
                path = os.path.join(d, fname)
                if not os.path.exists(path):
                    # try direct download via requests first
                    try:
                        b2 = fetch(src)
                        if b2[:4] == b"%PDF":
                            open(path, "wb").write(b2)
                        else:
                            # JS download -> playwright
                            with pg.expect_download(timeout=15000) as dl:
                                pg.goto(src, timeout=20000)
                            dl.value.save_as(path)
                    except Exception:
                        with pg.expect_download(timeout=15000) as dl:
                            pg.goto(src, timeout=20000)
                        dl.value.save_as(path)
                state[name]["downloaded"] = True
                state[name]["saved"] = path
                state[name]["downloaded_on"] = datetime.date.today().isoformat()
                downloaded += 1
            except Exception as e:
                state[name]["note"] = f"error:{type(e).__name__}"
        b.close()

    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"다운로드 완료: {downloaded}교")
    # re-parse into KB
    if downloaded:
        print("→ guide_auto_analyze.py 실행 (KB 재파싱)")
        import subprocess, sys
        r = subprocess.run([sys.executable, os.path.join(BASE, "guide_auto_analyze.py")],
                           capture_output=True, text=True, cwd=BASE, timeout=1800)
        print((r.stdout or "")[-500:])

if __name__ == "__main__":
    main()
