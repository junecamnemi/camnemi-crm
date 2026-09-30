# -*- coding: utf-8 -*-
"""Test: find + click PDF Download button on a junior foreign page, capture download."""
import os
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project\guides\junior\_probe"
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(user_agent="Mozilla/5.0", accept_downloads=True)
    pg = ctx.new_page()
    pg.goto("https://dept.daelim.ac.kr/tax/cms/FrCon/index.do?MENU_ID=450",
            timeout=25000, wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)

    # list PDF/Download-ish buttons
    btns = pg.eval_on_selector_all(
        "a, button",
        "els => els.filter(e => /PDF|다운|download/i.test(e.innerText||'')).map(e => e.innerText.trim())")
    print("PDF/다운 버튼:", btns)

    # click the first 'PDF 다운로드' / '다운로드'
    clicked = False
    for sel in ["text=PDF 다운로드", "text=다운로드", "a:has-text('PDF')", "a:has-text('다운')"]:
        try:
            with pg.expect_download(timeout=15000) as dl:
                pg.click(sel, timeout=5000)
            f = dl.value
            print("다운로드됨:", f.suggested_filename)
            f.save_as(os.path.join(OUT, f.suggested_filename))
            clicked = True
            break
        except Exception as e:
            print("  skip", sel, "->", type(e).__name__)
    if not clicked:
        print("클릭 실패 — 버튼이 JS 팝업이거나 download 이벤트가 아님")
    b.close()
