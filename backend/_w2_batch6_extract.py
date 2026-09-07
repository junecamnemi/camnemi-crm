# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

BASE = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
files = [
    "0000173_중부대학교[본교]_2026_외국인.pdf",
    "0000187_차의과학대학교[본교]_2026_외국인.pdf",
    "0000194_한국항공대학교[본교]_2026_외국인.pdf",
    "0000195_한남대학교[본교]_2026_외국인.pdf",
    "0000200_한성대학교[본교]_2026_외국인.pdf",
    "0000205_서울한영대학교[본교]_2026_외국인.pdf",
    "0000207_협성대학교[본교]_2026_외국인.pdf",
    "0000208_호남대학교[본교]_2026_외국인.pdf",
    "0000215_가톨릭꽃동네대학교[본교]_2026_외국인.pdf",
]
OUT = r"C:/Users/USER/camnemi-crm/backend/_w2_batch6_txt"
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
    outname = f.replace(".pdf", ".txt").replace("[본교]", "")
    with open(os.path.join(OUT, outname), "w", encoding="utf-8") as fh:
        fh.write("".join(parts))
    print(f"{f}: pages={len(parts)} chars={total}")
