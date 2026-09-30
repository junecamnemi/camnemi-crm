import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_paths as pp
from _retry_htmlonly import live_links, render_strong, pdf_year, page_text, PDFHINT, DLHINT
from playwright.sync_api import sync_playwright
GOOD = re.compile(r"(한국어|어학연수|한국어학원|한국어교육|어학당|연수생|유학생|Korean\s*(Language|Course|Program)|Language\s*(Course|Program))", re.I)
U = "https://enter.chsu.ac.kr/page.jsp?menuId=3000000193"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    c = b.new_context(ignore_https_errors=True, locale="ko-KR",
                      user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                      viewport={"width": 1400, "height": 1000}, accept_downloads=True)
    pg = c.new_page(); pg.set_default_timeout(25000)
    ls = live_links(pg, U)
    print("anchors:", len(ls))
    for x, t in ls:
        if re.search(r"(한국어|어학|유학생|모집요강|외국인|pdf|download)", (t or '') + x, re.I):
            print("   ", (t or '')[:40], "|", x[:100])
    probe = pp.library_root() / "lang" / "2027" / ".충북보건과학대학교.probe.pdf"
    probe.parent.mkdir(parents=True, exist_ok=True)
    d, st = render_strong(pg, U, probe)
    for j in (pp.library_root() / "lang" / "2027").glob(".충북보건과학대학교.probe*"):
        j.unlink(missing_ok=True)
    if d:
        t = page_text(d)
        print("rendered chars:", len(t.strip()), "| lang kw:", bool(GOOD.search(t)))
        print("sample:", t.strip()[:400].replace("\n", " "))
        if GOOD.search(t):
            yr = pdf_year(d, "2027")
            dd = pp.library_root() / "lang" / yr
            dd.mkdir(parents=True, exist_ok=True)
            dest = dd / f"충북보건과학대학교_한국어교육원_{yr}.pdf"
            dest.write_bytes(d)
            print("SAVED", dest)
    else:
        print("render failed:", st)
    b.close()
