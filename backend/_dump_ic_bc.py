#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump full text of 4 Incheon/Bucheon lang PDFs."""
import pymupdf, os
D = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
for fn in ["인천대학교_한국어교육원.pdf","인하대_한국어교육원.pdf","가톨릭대_한국어교육원.pdf","부천대학교_한국어교육원.pdf"]:
    p=os.path.join(D,fn)
    doc=pymupdf.open(p)
    print(f"\n\n################## {fn} ({len(doc)}p) ##################")
    txt="".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    print(txt[:1800])
