#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from batch-8 PDFs (2026 foreigner guides) with pymupdf, suppressing MuPDF stderr."""
import os, sys, io, contextlib
import pymupdf

BASE = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인"
OUT = r"C:/Users/USER/camnemi-crm/backend/_curation_tmp/_w2_batch8"

files = [
    "0002660_인천대학교[본교]_2026_외국인.pdf",
    "0002800_신한대학교[제2캠퍼스]_2026_외국인.pdf",
    "0002959_상명대학교[제2캠퍼스]_2026_외국인.pdf",
    "0003193_영산대학교[본교]_2026_외국인.pdf",
    "0003194_영산대학교[제2캠퍼스]_2026_외국인.pdf",
    "경운대학교[본교]_2026_외국인.pdf",
    "광주여자대학교[본교]_2026_외국인.pdf",
    "국립금오공과대학교[본교]_2026_외국인.pdf",
    "송원대학교[본교]_2026_외국인.pdf",
]

os.makedirs(OUT, exist_ok=True)
for f in files:
    path = os.path.join(BASE, f)
    tag = f.split("[")[0]
    if tag in ("영산대학교",):
        tag = f.replace(".pdf", "").replace("[", "_").replace("]", "")
    out_txt = os.path.join(OUT, tag + ".txt")
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            doc = pymupdf.open(path)
            n = doc.page_count
            parts = []
            for i, page in enumerate(doc):
                parts.append(f"\n===== PAGE {i+1} =====\n")
                parts.append(page.get_text())
            text = "".join(parts)
            doc.close()
        with open(out_txt, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"OK {tag}: {n} pages, {len(text)} chars -> {out_txt}")
    except Exception as e:
        print(f"FAIL {tag}: {e}")
