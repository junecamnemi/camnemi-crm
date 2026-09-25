#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the 63 Tier-A candidate URLs: download, check valid PDF, check guide content.
Output _scrape_verified.json {school,level,url,ok,reason,size}."""
import json, os, re, urllib.request, ssl

B = r"C:\Users\wisew\camnemi-crm\backend"
suggest = json.load(open(os.path.join(B, "_scrape_suggest_A.json"), encoding="utf-8"))
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

def check(url):
    try:
        import requests
        r = requests.get(url, headers=HEADERS, timeout=45, verify=False, allow_redirects=True)
        b = r.content
        if b[:5] != b"%PDF-":
            return False, f"not-pdf({r.status_code}/{len(b)}b)", len(b)
        import pymupdf
        doc = pymupdf.open(stream=b, filetype="pdf")
        t = "\n".join(doc[i].get_text() for i in range(min(len(doc), 20)))
        np = len(doc); doc.close()
        ok = bool(re.search(r"모집요강|외국인|재외국민|입학|원서|전형", re.sub(r"\s+", "", t)))
        return ok, f"pdf-{np}p-{len(t)}c", len(b)
    except Exception as e:
        return False, f"err:{type(e).__name__}:{str(e)[:40]}", 0

res = {}
ok = fail = 0
for school, lv in suggest.items():
    for level, info in lv.items():
        url = info["url"]
        good, note, size = check(url)
        res.setdefault(school, {})[level] = {"url": url, "ok": good, "note": note, "size": size}
        if good: ok += 1
        else: fail += 1
        print(f"  {'✅' if good else '❌'} {school[:18]:18s}[{level}] {note}")

json.dump(res, open(os.path.join(B, "_scrape_verified.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n검증: 유효 {ok} / 실패·오탐 {fail}")