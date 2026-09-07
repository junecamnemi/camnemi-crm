# -*- coding: utf-8 -*-
import fitz
jobs = [
    ("cheongju_p1", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/청주대_대학원_모집요강.pdf", 0),
    ("chodang_p3", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/초당대_대학원_모집요강.pdf", 2),
    ("chodang_p4", "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/초당대_대학원_모집요강.pdf", 3),
]
for name, p, idx in jobs:
    doc = fitz.open(p)
    pg = doc[idx]
    pix = pg.get_pixmap(dpi=150)
    out = "backend/_ma_batch1_txt/" + name + ".png"
    pix.save(out)
    print(name, out, pix.width, pix.height)
