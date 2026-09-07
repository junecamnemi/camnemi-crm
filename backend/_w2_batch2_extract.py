# -*- coding: utf-8 -*-
import os, sys, io, warnings
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

BASE = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
files = [
    "0000073_광신대학교[본교]_2026_외국인.pdf",
    "0000078_국민대학교[본교]_2026_외국인.pdf",
    "0000080_극동대학교[본교]_2026_외국인.pdf",
    "0000084_대구대학교[본교]_2026_외국인.pdf",
    "0000088_대구가톨릭대학교[본교]_2026_외국인.pdf",
    "0000093_대신대학교[본교]_2026_외국인.pdf",
    "0000098_서울기독대학교[본교]_2026_외국인.pdf",
    "0000100_동국대학교[본교]_2026_외국인.pdf",
    "0000102_동덕여자대학교[본교]_2026_외국인.pdf",
]
OUT = r"C:/Users/USER/camnemi-crm/backend/_w2_batch2_txt"
os.makedirs(OUT, exist_ok=True)
for f in files:
    fp = os.path.join(BASE, f)
    try:
        doc = pymupdf.open(fp)
        parts = []
        total = 0
        npages = len(doc)
        for i, page in enumerate(doc):
            t = page.get_text()
            total += len(t)
            parts.append(f"\n===== PAGE {i+1} =====\n" + t)
        doc.close()
        outname = f.replace(".pdf", ".txt").replace("[본교]", "")
        with open(os.path.join(OUT, outname), "w", encoding="utf-8") as w:
            w.write("".join(parts))
        print(f"{f} -> {total} chars, {npages} pages")
    except Exception as e:
        print(f"{f} ERROR: {e}")
