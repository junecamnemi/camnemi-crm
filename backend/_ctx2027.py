#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the 2027-specific schedule context from each PDF."""
import pymupdf, os, re
DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강"
for fn in ["서강대_한국어교육원_2027.pdf","이화여자대학교_한국어교육원_2027.pdf",
           "가톨릭대_한국어교육원_2027.pdf","연세대_한국어교육원_2027.pdf"]:
    doc = pymupdf.open(os.path.join(DIR,fn))
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    print(f"\n\n########## {fn} — 2027 맥락 ##########")
    # find context around 2027
    for m in re.finditer(r'2027', txt):
        s=max(0,m.start()-80); e=min(len(txt),m.end()+160)
        print(f"  ...{txt[s:e].replace(chr(10),' ')}...")
        # limit output
        if m.start()> 6000: break
