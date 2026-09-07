# -*- coding: utf-8 -*-
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

fp = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인/0000056_경기대학교[본교]_2026_외국인.pdf"
OUT = r"C:/Users/USER/camnemi-crm/backend/_w2_batch1_img"
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(fp)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=140)
    out = os.path.join(OUT, f"kyunggi_p{i+1:02d}.png")
    pix.save(out)
    print(out, pix.width, pix.height)
doc.close()
