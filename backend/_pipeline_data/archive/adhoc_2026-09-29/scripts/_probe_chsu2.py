import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
URLS = ["https://www.chsu.ac.kr/index.do", "https://ipsi.chsu.ac.kr/", "http://ipsi.chsu.ac.kr/",
        "https://www.chsu.ac.kr/ipsi/index.do", "https://www.chsu.ac.kr/haksang/index.do"]
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
            links = pg.eval_on_selector_all("a", "e=>e.map(x=>[x.href||'',(x.innerText||'').replace(/\s+/g,' ').trim().slice(0,50)])")
            print(f"== {u[:55]} anchors={len(links)} final={pg.url[:55]}")
            for x, t in links[:25]:
                print("     ", (t or '')[:44], "|", x[:90])
        except Exception as e:
            print(f"== {u[:55]} ERR {type(e).__name__}")
        pg.close()
    b.close()
