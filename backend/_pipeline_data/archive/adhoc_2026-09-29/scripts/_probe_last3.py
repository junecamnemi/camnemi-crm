#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Probe v2: fresh page per URL + wait_until=commit (these splash sites JS-redirect and
break page.goto's load wait)."""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from playwright.sync_api import sync_playwright  # noqa: E402

URLS = [
 "https://iec.yit.ac.kr/",
 "https://www.yit.ac.kr/main.do",
 "https://www.chsu.ac.kr/",
 "https://chsu.ac.kr/index.do?INTRO_PASS=Y",
 "https://www.chsu.ac.kr/index.do",
 "http://global.hsc.ac.kr/",
 "https://global.hsc.ac.kr/korean/",
 "https://www.hsc.ac.kr/intro_ipsi2_2.jsp",
]
KW = re.compile(r"(한국어|어학|연수|유학생|외국인|국제|korean|language|international)", re.I)
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    c = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                      locale="ko-KR", ignore_https_errors=True, viewport={"width": 1400, "height": 1000})
    for u in URLS:
        pg = c.new_page(); pg.set_default_timeout(25000)
        try:
            pg.goto(u, timeout=25000, wait_until="commit")
        except Exception:
            pass
        pg.wait_for_timeout(4000)
        try:
            body = pg.evaluate("document.body ? document.body.innerText.replace(/\\s+/g,' ').length : -1")
            links = pg.eval_on_selector_all("a", "e=>e.map(x=>[x.href||'',(x.innerText||'').replace(/\\s+/g,' ').trim().slice(0,40)])")
            hits = [(x, t) for x, t in links if KW.search(t) or KW.search(x)]
            print(f"== {u[:58]} body={body} anchors={len(links)} kw={len(hits)} url={pg.url[:58]}")
            for x, t in hits[:10]:
                print("     ", t[:38], "|", x[:95])
        except Exception as e:
            print(f"== {u[:58]} ERR {type(e).__name__}: {str(e)[:70]}")
        pg.close()
    b.close()