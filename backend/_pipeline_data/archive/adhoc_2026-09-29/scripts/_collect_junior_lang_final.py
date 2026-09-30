#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final pass for the 6 uncovered 전문대 어학연수 — curated candidate URLs per school.

These 6 homepages are splash/intro screens (2~10 anchors, body <500 chars), so the live menu
tree gives nothing. Instead: hand-picked entry URLs (department pages, 입시 main, English site),
render each in a real browser, keep the first page whose text actually talks about
한국어/어학/연수/Korean/Language, and file it as a verified PDF. PDF attachments found on the
page win over a render.

Log: backend/_junior_lang_final_report.jsonl
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline_paths as pp  # noqa: E402
from _retry_htmlonly import live_links, render_strong, pdf_year, page_text, PDFHINT, DLHINT  # noqa

CAND = {
    "강동대학교": ["https://www.gangdong.ac.kr/global/contents/GLO0201.do",
                "https://ipsi.gangdong.ac.kr/intro/main/index.do",
                "https://www.gangdong.ac.kr/global/contents/GLO0202.do"],
    "경민대학교": ["https://www.kyungmin.ac.kr/homepage/page.do?menu=147",
                "https://www.kyungmin.ac.kr/homepage/main.do",
                "https://wld.kyungmin.ac.kr/"],
    "목포과학대학교": ["https://www.msu.ac.kr/base/contents/view?contentsNo=592&menuLevel=3&menuNo=434",
                  "https://ipsi.msu.ac.kr/", "http://www.msu.ac.kr/index"],
    "여주대학교": ["https://info.yit.ac.kr/ko/index.do", "https://www.yit.ac.kr/main.do",
                "https://ipsi.yit.ac.kr/"],
    "충북보건과학대학교": ["https://english.chsu.ac.kr/CmsHome/admission05.aspx",
                   "https://chsu.ac.kr/index.do?INTRO_PASS=Y", "https://www.chsu.ac.kr/index.do"],
    "한림성심대학교": ["https://global.hsc.ac.kr/eng/index.do", "http://global.hsc.ac.kr/",
                 "https://ipsi.hsc.ac.kr/"],
}
GOOD = re.compile(r"(한국어|어학연수|한국어교육원|국제교육원|어학당|연수생|유학생|Korean\s*(Language|Course|Program)|Language\s*(Course|Program|Institute)|International\s*(Office|Center))", re.I)
MIN = 250
REPORT = HERE / "_junior_lang_final_report.jsonl"

from playwright.sync_api import sync_playwright  # noqa: E402
ok = fail = 0
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome", headless=True)
    ctx = br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                         accept_downloads=True, locale="ko-KR", ignore_https_errors=True,
                         viewport={"width": 1400, "height": 1000})
    page = ctx.new_page()
    page.set_default_timeout(30000)
    for school, urls in CAND.items():
        row = {"school": school, "status": None, "saved": None, "source": None,
               "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "tried": []}
        data = used = None
        for u in urls:
            row["tried"].append(u)
            try:
                # 1) PDF attachment on this page?
                for link, txt in live_links(page, u):
                    if PDFHINT.search(link.lower()) or DLHINT.search(link.lower()):
                        try:
                            import requests
                            rr = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
                            if rr.status_code < 400 and rr.content[:4] == b"%PDF":
                                data, used, row["status"] = rr.content, link, "pdf_attachment"
                                break
                        except Exception:
                            pass
                if data:
                    break
                probe = pp.library_root() / "lang" / "2027" / f".{school}.probe.pdf"
                probe.parent.mkdir(parents=True, exist_ok=True)
                d2, st = render_strong(page, u, probe)
                if d2:
                    txt = page_text(d2)
                    if GOOD.search(txt):
                        data, used, row["status"] = d2, u, "page_render"
                        break
                    row["tried"].append(f"rejected(no lang keyword): {u}")
            except Exception as e:
                row["tried"].append(f"err {type(e).__name__}: {u}")
        try:
            for junk in (pp.library_root() / "lang" / "2027").glob(f".{school}.probe*"):
                junk.unlink(missing_ok=True)
        except Exception:
            pass
        if data:
            yr = pdf_year(data, "2027")
            libdir = pp.library_root() / "lang" / yr
            libdir.mkdir(parents=True, exist_ok=True)
            dest = libdir / f"{school}_한국어교육원_{yr}.pdf"
            dest.write_bytes(data)
            row.update(saved=str(dest), source=used, year=yr, bytes=len(data),
                       chars=len(page_text(data).strip()))
            ok += 1
            print(f"  OK   {school} -> {dest.name} ({row['status']}, {row['chars']} chars)", flush=True)
        else:
            row["status"] = "not_found"
            fail += 1
            print(f"  ---  {school} not found ({len(urls)} candidates)", flush=True)
        with open(REPORT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    br.close()
print(f"\nDONE final: ok={ok} fail={fail} of {len(CAND)}")