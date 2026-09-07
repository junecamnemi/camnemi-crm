# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

fp = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인/0000187_차의과학대학교[본교]_2026_외국인.pdf"
OUT = r"C:/Users/USER/camnemi-crm/backend/_w2_batch6_txt/cha_pages"
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(fp)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    p = os.path.join(OUT, f"cha_p{i+1:02d}.png")
    pix.save(p)
    print(p, pix.width, pix.height)
doc.close()
