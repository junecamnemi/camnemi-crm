import re, shutil, sys
from pathlib import Path
sys.path.insert(0, '.')
import guide_page_collect as g
DEST = Path(r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides/_archive/2026/ba/광주여자대학교[본교]_2026_외국인.pdf")
PAGES = ["https://globalgate.kwu.ac.kr/mod/board/view.do?MID=GLOBALGATE_B05030101&DOC_NO=175124558739505&page=1",
         "https://globalgate.kwu.ac.kr/mod/page/view.do?MID=GLOBALGATE_C05030101",
         "https://globalgate.kwu.ac.kr/mod/board/view.do?MID=GLOBALGATE_B05030101"]
GOOD = re.compile(r"(외국인|유학생|모집요강|입학|전형|한국어)", re.I)
from playwright.sync_api import sync_playwright
best = None
with sync_playwright() as pw:
    br = pw.chromium.launch(channel="chrome", headless=True)
    ctx = br.new_context(user_agent=g.UA, ignore_https_errors=True, locale="ko-KR",
                         viewport={"width": 1400, "height": 1000}, accept_downloads=True)
    page = ctx.new_page(); page.set_default_timeout(25000)
    for u in PAGES:
        try:
            for link, text in g.live_links(page, u):
                if g.PDF_HINT.search(link.lower()) or g.DL_HINT.search(link.lower()):
                    data = g.fetch_pdf(link)
                    if data and data[:4] == g.PDF_MAGIC:
                        t = g.page_text(data)
                        print(f"   {link[:110]} -> {len(data):,} B text={len(t.strip())} good={bool(GOOD.search(t))}")
                        if GOOD.search(t) and (best is None or len(data) > len(best[0])):
                            best = (data, link)
        except Exception as e:
            print("   ERR", u[:60], type(e).__name__)
    br.close()
if best:
    shutil.copy2(DEST, g.BACKUPS / ("광주여대_prerender_" + DEST.name))
    DEST.write_bytes(best[0])
    print("FIXED 광주여대 슬롯 from official PDF:", best[1][:95], "->", DEST.stat().st_size, "bytes")
else:
    print("could not find an official 광주여대 외국인 모집요강 PDF on kwu.ac.kr boards")
