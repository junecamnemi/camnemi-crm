#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect Sejong 2027 PDF - confirm year + extract real dates/foreigner info."""
import pymupdf, os, re
p = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_외국인_모집요강\외국인\0000138_세종대학교[본교]_2027_외국인.pdf"
doc = pymupdf.open(p)
print("pages:", len(doc))
txt = "".join(doc[i].get_text() for i in range(len(doc)))
# key signals
print("=== year signals ===")
for kw in ["2027","2026","재외국민","외국인","모집요강","원서접수"]:
    c = txt.count(kw)
    print(f"  '{kw}': {c}회")
# show first 1500 chars
print("\n=== 앞부분 ===")
print(txt[:1500])
