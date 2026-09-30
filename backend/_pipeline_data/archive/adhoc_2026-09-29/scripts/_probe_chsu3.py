import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
KW = re.compile(r"(한국어|어학|연수|유학생|외국인|국제|korean|language|international)", re.I)
URLS = ["https://enter.chsu.ac.kr/", "https://enter.chsu.ac.kr/page.jsp?menuId=4000000216"]
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    c = b.new_context(ignore_https_errors=True, locale="ko-KR",
                      user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                      viewport={"width": 1400, "height": 1000})
    for u in URLS:
        pg = c.new_page(); pg.set_default_timeout(25000)
        try:
            pg.goto(u, timeout=25000, wait_until="commit")
        except Exception:
            pass
        pg.wait_for_timeout(4000)
        try:
            links = pg.eval_on_selector_all("a", "e=>e.map(x=>[x.href||'',(x.innerText||'').replace(/\s+/g,' ').trim().slice(0,45)])")
            hits = [(x, t) for x, t in links if KW.search(t or '') or KW.search(x)]
            print(f"== {u[:60]} anchors={len(links)} kw={len(hits)} final={pg.url[:55]}")
            for x, t in hits[:15]:
                print("     ", (t or '')[:40], "|", x[:95])
        except Exception as e:
            print(f"== {u[:60]} ERR {type(e).__name__}")
        pg.close()
    b.close()
