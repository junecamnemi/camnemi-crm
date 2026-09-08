#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Kyungin Women's Univ D-4 Korean program details."""
import pymupdf, re
doc = pymupdf.open(r"C:\Users\USER\AppData\Local\Temp\kiwu.pdf")
txt = "".join(doc[i].get_text() for i in range(len(doc)))
print("pages:", len(doc))
# find 한국어과정(D-4) section
idx = txt.find("한국어과정 (D-4)")
print("D-4 위치:", idx)
if idx>=0:
    print(txt[idx:idx+2500])
else:
    # search section markers
    for kw in ["한국어과정","D-4","학사일정","모집요강"]:
        for m in re.finditer(kw,txt):
            print(f"\n[{kw}] ...{txt[m.start():m.start()+200]}...")
