import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
KW = re.compile(r"(한국어|어학|연수|유학생|외국인|국제|korean|language|international)", re.I)
URLS = ["https://klec.chsu.ac.kr/", "https://global.chsu.ac.kr/", "https://intl.chsu.ac.kr/",
        "https://korean.chsu.ac.kr/", "https://www.chsu.ac.kr/", "https://www.chsu.ac.kr/index.do",
        "https://studyinkorea.go.kr/ko/sub/college_info/college_info.do?ei_code=731230"]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    c = b.new_context(ignore_https_errors=True, locale="ko-KR",
                      user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                      viewport={"width": 1400, "height": 1000})
    for u in URLS:
        pg = c.new_page(); pg.set_default_timeout(20000)
        try:
            pg.goto(u, timeout=20000, wait_until="commit")
        except Exception:
            pass
        pg.wait_for_timeout(3500)
        try:
            body = pg.evaluate("document.body ? document.body.innerText.replace(/\s+/g,' ').length : -1")
            links = pg.eval_on_selector_all("a", "e=>e.map(x=>[x.href||'',(x.innerText||'').replace(/\s+/g,' ').trim().slice(0,40)])")
            hits = [(x, t) for x, t in links if KW.search(t) or KW.search(x)]
            print(f"== {u[:62]} body={body} a={len(links)} kw={len(hits)} final={pg.url[:55]}")
            for x, t in hits[:8]:
                print("     ", (t or '')[:36], "|", x[:95])
        except Exception as e:
            print(f"== {u[:62]} ERR {type(e).__name__}")
        pg.close()
    b.close()
