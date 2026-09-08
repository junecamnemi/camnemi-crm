#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grep 2027 dates in the 4 PDFs to confirm 2027 schedule captured."""
import pymupdf, os, re
DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강"
files = ["가톨릭대_한국어교육원_2027.pdf","서강대_한국어교육원_2027.pdf",
         "연세대_한국어교육원_2027.pdf","이화여자대학교_한국어교육원_2027.pdf"]
for fn in files:
    doc = pymupdf.open(os.path.join(DIR,fn))
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    # find all 2027-2028 patterns
    pats = re.findall(r'20(?:26|27|28)[\.\-년 ]+\d+[\.\-월 ]*\d*', txt)
    has2027 = re.search(r'20(?:27|28)[\.\-년]\s*\d', txt)
    print(f"\n### {fn}")
    print(f"  2027/2028 패턴: {'있음' if has2027 else '없음'}")
    if pats:
        print("  날짜:", pats[:12])
