#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Last-3 pass: 여주대 (한국어학원 입학안내 notice), 충북보건과학대 (StudyinKorea lang URL),
한림성심대 (probe 입시 + 국제교류 menus). Collects a verified PDF where a lang page exists.
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402
from _retry_htmlonly import live_links, render_strong, pdf_year, page_text, PDFHINT, DLHINT  # noqa
from playwright.sync_api import sync_playwright  # noqa: E402

GOOD = re.compile(r"(한국어|어학연수|한국어학원|한국어교육|국제교육원|어학당|연수생|유학생|Korean\s*(Language|Course|Program)|Language\s*(Course|Program|Institute))", re.I)
REPORT = HERE / "_junior_lang_final_report.jsonl"


def save(school, data, status, used):
    yr = pdf_year(data, "2027")
    d = pp.library_root() / "lang" / yr
    d.mkdir(parents=True, exist_ok=True)
    dest = d / f"{school}_한국어교육원_{yr}.pdf"
    dest.write_bytes(data)
    return {"school": school, "status": status, "saved": str(dest), "source": used, "year": yr,
            "chars": len(page_text(data).strip()), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}


def try_url(page, school, u, good=GOOD):
    """PDF attachment on the page first, else render + verify."""
    try:
        for link, txt in live_links(page, u):
            if PDFHINT.search(link.lower()) or DLHINT.search(link.lower()):
                try:
                    import requests
                    rr = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
                    if rr.status_code < 400 and rr.content[:4] == b"%PDF" and len(page_text(rr.content).strip()) >= 250:
                        return save(school, rr.content, "pdf_attachment", link)
                except Exception:
                    pass
        probe = pp.library_root() / "lang" / "2027" / f".{school}.probe.pdf"
        probe.parent.mkdir(parents=True, exist_ok=True)
        d2, st = render_strong(page, u, probe)
        for junk in (pp.library_root() / "lang" / "2027").glob(f".{school}.probe*"):
            junk.unlink(missing_ok=True)
        if d2 and good.search(page_text(d2)):
            return save(school, d2, "page_render", u)
    except Exception as e:
        return {"school": school, "status": f"error:{type(e).__name__}", "source": u}
    return None


TASKS = {
    "여주대학교": ["https://iec.yit.ac.kr/exchange/cms/CM_BB01_CON/CM_BB01_V01.do?MENU_SN=2495&BBS_SN=33759",
               "https://iec.yit.ac.kr/exchange/cms/CM_CN01_CON/index.do?MENU_SN=2498",
               "https://iec.yit.ac.kr/exchange/cms/menu.do?MENU_SN=2497"],
    "충북보건과학대학교": [],
    "한림성심대학교": ["https://ipsi.hsc.ac.kr/", "https://global.hsc.ac.kr/global/",
                 "https://www.hsc.ac.kr/intro_ipsi2_2.jsp"],
}
results = []
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome", headless=True)
    ctx = br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                         accept_downloads=True, locale="ko-KR", ignore_https_errors=True,
                         viewport={"width": 1400, "height": 1000})
    page = ctx.new_page(); page.set_default_timeout(30000)

    for school, urls in TASKS.items():
        if school == "충북보건과학대학교":
            continue
        got = None
        for u in urls:
            if school == "한림성심대학교":
                # probe: list lang-ish links only
                try:
                    ls = live_links(page, u)
                    hits = [(x, t) for x, t in ls if GOOD.search(t or "") or GOOD.search(x)]
                    print(f"  [{school}] {u[:55]} anchors={len(ls)} kw={len(hits)}")
                    for x, t in hits[:8]:
                        print("        ", (t or '')[:34], "|", x[:95])
                except Exception as e:
                    print(f"  [{school}] {u[:55]} ERR {type(e).__name__}")
                continue
            got = try_url(page, school, u)
            if got:
                break
        if got:
            results.append(got)
            print(f"  OK  {school} -> {Path(got['saved']).name} ({got['status']})", flush=True)
        elif school != "한림성심대학교":
            results.append({"school": school, "status": "not_found"})
            print(f"  --- {school} not found")

    # 충북보건과학대: StudyinKorea college page -> language institute website field
    try:
        r = page.goto("https://studyinkorea.go.kr/ko/sub/college_info/college_info.do?ei_code=731230",
                      timeout=30000, wait_until="commit")
        page.wait_for_timeout(4000)
        txt = page.evaluate("document.body ? document.body.innerText : ''")
        urls_found = re.findall(r"https?://[^\s\"'<>]+", txt)
        print("  [충북보건과학대] studyinkorea text len", len(txt))
        for u in urls_found[:12]:
            print("       url:", u[:110])
        m = re.search(r"(?:Language Institute|어학|한국어)[^\n]{0,200}", txt)
        if m:
            print("       field:", m.group(0)[:200].replace("\n", " "))
    except Exception as e:
        print("  [충북보건과학대] studyinkorea ERR", type(e).__name__, str(e)[:80])
    br.close()

with open(REPORT, "a", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("\nresults:", json.dumps(results, ensure_ascii=False)[:600])