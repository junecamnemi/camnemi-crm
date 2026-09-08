#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full text page 2 of SWU lang PDF - the document list + fees."""
import pymupdf
p = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\서울여자대_한국어교육원.pdf"
doc = pymupdf.open(p)
for i in range(min(2,len(doc))):
    print(f"\n===== PAGE {i+1} =====")
    print(doc[i].get_text())
