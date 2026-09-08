#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detail dump for the top near-Namyangju candidates."""
import pymupdf, os
DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
for fn in ["대진대_한국어교육원.pdf","신한대_한국어교육원.pdf","서정대학교_한국어교육원.pdf"]:
    p = os.path.join(DIR, fn)
    doc = pymupdf.open(p)
    print(f"\n\n########## {fn} ({len(doc)} pages) ##########")
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    # print first 2000 chars
    print(txt[:2500])
    doc.close()
