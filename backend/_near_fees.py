#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract fees + country/admission from Shinhan & Seojeong PDFs."""
import pymupdf, os, re
DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
for fn in ["신한대_한국어교육원.pdf","서정대학교_한국어교육원.pdf"]:
    doc = pymupdf.open(os.path.join(DIR,fn))
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    print(f"\n########## {fn} ##########")
    # fees & admission relevant
    for kw in ["수강료","등록금","학비","원","입학","모집","접수","개강","문의","전화","캄보","학력","잔고","D-4"]:
        for m in re.finditer(kw, txt):
            s=max(0,m.start()-60); e=min(len(txt),m.end()+130)
            print(f"  [{kw}] ...{txt[s:e].strip()}...")
    doc.close()
