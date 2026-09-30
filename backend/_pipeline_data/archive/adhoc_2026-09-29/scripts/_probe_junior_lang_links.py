#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump the live link tree of the 6 remaining 전문대 (home + 입시 + common lang subdomains).

  python _probe_junior_lang_links.py
Writes _junior_lang_linktree.json : {school: [{url,text,src}]}
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _retry_htmlonly import live_links  # noqa: E402

TARGETS = {
    "강동대학교": ["http://www.gangdong.ac.kr", "http://ipsi.gangdong.ac.kr"],
    "경민대학교": ["http://www.kyungmin.ac.kr", "https://wld.kyungmin.ac.kr/"],
    "목포과학대학교": ["http://www.msu.ac.kr", "http://ipsi.msu.ac.kr"],
    "여주대학교": ["https://www.yit.ac.kr", "https://ipsi.yit.ac.kr"],
    "충북보건과학대학교": ["http://www.chsu.ac.kr", "https://english.chsu.ac.kr/"],
    "한림성심대학교": ["http://www.hsc.ac.kr", "http://global.hsc.ac.kr/", "https://ipsi.hsc.ac.kr/"],
}
SUBS = ["global", "intl", "international", "kli", "klec", "enter", "edu", "korean", "oia", "iiee", "exchange"]

out = {}
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome", headless=True)
    ctx = br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
                         locale="ko-KR", ignore_https_errors=True, viewport={"width": 1400, "height": 1000})
    page = ctx.new_page()
    page.set_default_timeout(25000)
    for school, urls in TARGETS.items():
        rows = []
        dom = urls[0].split("//")[-1].split("/")[0]
        base = dom.split(".")[-2] + "." + dom.split(".")[-1]
        for u in urls + [f"https://{s}.{base}/" for s in SUBS]:
            try:
                links = live_links(page, u)
            except Exception:
                links = []
            if links:
                rows.append({"src": u, "n": len(links),
                             "links": [{"u": x, "t": t} for x, t in links][:120]})
                print(f"  {school:14s} {u[:52]:52s} {len(links)} links", flush=True)
        out[school] = rows
    br.close()
json.dump(out, open(HERE / "_junior_lang_linktree.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote _junior_lang_linktree.json")