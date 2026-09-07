# -*- coding: utf-8 -*-
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

BASE = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
files = [
    "0000040_서울시립대학교[본교]_2026_외국인.pdf",
    "0000051_강남대학교[본교]_2026_외국인.pdf",
    "0000053_건국대학교(글로컬)[분교]_2026_외국인.pdf",
    "0000054_건양대학교[본교]_2026_외국인.pdf",
    "0000056_경기대학교[본교]_2026_외국인.pdf",
    "0000061_대구한의대학교[본교]_2026_외국인.pdf",
    "0000064_경일대학교[본교]_2026_외국인.pdf",
    "0000065_신경주대학교[본교]_2026_외국인.pdf",
    "0000070_고려대학교(세종)[분교]_2026_외국인.pdf",
]
OUT = r"C:/Users/USER/camnemi-crm/backend/_w2_batch1_txt"
os.makedirs(OUT, exist_ok=True)
for f in files:
    fp = os.path.join(BASE, f)
    doc = pymupdf.open(fp)
    parts = []
    total = 0
    for i, page in enumerate(doc):
        t = page.get_text()
        total += len(t)
        parts.append(f"\n===== PAGE {i+1} =====\n" + t)
    doc.close()
    outname = f.replace(".pdf", ".txt").replace("[본교]", "").replace("[분교]", "")
    with open(os.path.join(OUT, outname), "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print(f"{f}: pages={len(parts)} chars={total}")
