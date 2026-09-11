#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract lang-program details for the 8 unmatched schools from their PDFs."""
import pymupdf, os, re
D = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
files = ["국립금오공과대학교_한국어교육원.pdf","나사렛대학교_한국어교육원.pdf","부산대_한국어교육원.pdf",
         "서울시립대_한국어교육원.pdf","서울신학대_한국어교육원.pdf","서일대학교_한국어교육원.pdf",
         "총신대_한국어교육원.pdf","한성대학교_한국어교육원.pdf"]
for fn in files:
    p = os.path.join(D, fn)
    if not os.path.exists(p):
        print(f"### {fn}: 없음"); continue
    doc = pymupdf.open(p)
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    print(f"\n{'='*70}\n### {fn} ({len(txt)}자)")
    # tuition
    for m in re.finditer(r'(수강료|등록금|수업료|연수비|학비)[^\n]{0,70}', txt):
        print("  💰", m.group(0).strip()[:90])
    # period
    for m in re.finditer(r'(접수|모집기간|원서)[^\n]{0,60}', txt):
        print("  📅", m.group(0).strip()[:90])
    # structure
    for m in re.finditer(r'(\d+\s*주|\d+\s*시간|주\s*\d+\s*회|주\s*\d+\s*일)', txt):
        print("  ⏱", m.group(0).strip())
        break
