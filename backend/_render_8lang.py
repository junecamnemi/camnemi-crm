#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render first ~4 pages of each image-only lang PDF to PNG for vision OCR."""
import pymupdf, os
D = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
OUT = r"C:\Users\USER\camnemi-crm\backend\_lang_ocr"
os.makedirs(OUT, exist_ok=True)
files = ["국립금오공과대학교_한국어교육원.pdf","나사렛대학교_한국어교육원.pdf","부산대_한국어교육원.pdf",
         "서울시립대_한국어교육원.pdf","서울신학대_한국어교육원.pdf","서일대학교_한국어교육원.pdf",
         "총신대_한국어교육원.pdf","한성대학교_한국어교육원.pdf"]
for fn in files:
    p=os.path.join(D,fn); d=pymupdf.open(p)
    base=fn.replace("_한국어교육원.pdf","")
    n=min(len(d),4)
    for i in range(n):
        pix=d[i].get_pixmap(dpi=140)
        op=os.path.join(OUT,f"{base}_p{i+1}.png")
        pix.save(op)
    print(f"{base}: {n}p rendered")
    d.close()
print("OUT:", OUT)
