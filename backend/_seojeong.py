#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seojeong full text + Daejin admission section."""
import pymupdf, os
DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
doc = pymupdf.open(os.path.join(DIR,"서정대학교_한국어교육원.pdf"))
print("======== 서정대 full ========")
print("".join(doc[i].get_text() for i in range(len(doc)))[:3500])
