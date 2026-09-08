#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract full text from Seoul Women's Univ lang PDF, esp. the country list part."""
import fitz
p = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강\서울여자대_한국어교육원.pdf"
doc = fitz.open(p)
print("pages:", len(doc))
full = ""
for i in range(len(doc)):
    full += f"\n--- PAGE {i+1} ---\n" + doc[i].get_text()
# find country-related keywords
import re
for kw in ["캄보", "Cambodia", "학력인증", "신원", "베트남", "국가", "몽골", "네팔", "미얀마", "스리랑카"]:
    for m in re.finditer(kw, full):
        s=max(0,m.start()-80); e=min(len(full), m.end()+150)
        print(f"\n[{kw}] ...{full[s:e]}...")
