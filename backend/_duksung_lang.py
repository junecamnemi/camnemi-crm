#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dukseung Women's Univ lang PDF - full text extraction."""
import pymupdf, os
p = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\덕성여자대_한국어교육원.pdf"
doc = pymupdf.open(p)
print(f"pages: {len(doc)}")
for i in range(len(doc)):
    print(f"\n===== PAGE {i+1} =====")
    print(doc[i].get_text())
