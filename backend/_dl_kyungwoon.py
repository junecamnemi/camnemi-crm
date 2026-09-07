#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download Kyungwoon Univ foreigner admission guide PDF (Korean URL escaped)."""
import urllib.request, urllib.parse, os

base = "https://www.ikw.ac.kr/resources/templates/ipsi/assets/file/"
fn = "2026 2학기 외국인 모집요강_신입 국문260727_3차.pdf"
url = base + urllib.parse.quote(fn)

out = r"C:\Users\USER\camnemi-crm\backend\_guide_pdfs\kyungwoon_2026.pdf"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=90)
    data = resp.read()
    with open(out, "wb") as f:
        f.write(data)
    print(f"다운로드 완료: {len(data)} bytes → {out}")
except Exception as e:
    print("실패:", e)
