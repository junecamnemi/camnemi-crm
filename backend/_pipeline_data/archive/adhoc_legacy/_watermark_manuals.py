# -*- coding: utf-8 -*-
"""Add CAMNEMI watermark (multi-band, low-alpha) + footer to all manual PDFs.
Safe: horizontal text, overlay only — never rotates existing content."""
import os, pymupdf

B = r"C:\Users\wisew\camnemi-crm\backend"
PDFS = [
    "취업_비자_매뉴얼_유학생.pdf",
    "비자별_상세규정_매뉴얼.pdf",
    "Working_Visa_Plan_Students_EN.pdf",
]
NAVY = (0.043, 0.145, 0.271)
GOLD = (0.789, 0.635, 0.153)

def stamp(fp):
    doc = pymupdf.open(fp)
    for page in doc:
        w, h = page.rect.width, page.rect.height
        fs = 64
        # staggered diagonal-feel watermark bands (offsets create a tilted look)
        for i, off in enumerate([-0.22, -0.07, 0.08, 0.23]):
            x = w * (0.5 + off)
            y = h * (0.5 + (i - 1.5) * 0.18)
            if 0 < y < h:
                page.insert_text(pymupdf.Point(x, y), "CAMNEMI",
                                 fontname="helv", fontsize=fs,
                                 color=NAVY, fill_opacity=0.05, stroke_opacity=0.05,
                                 overlay=True)
        # footer
        page.insert_text(pymupdf.Point(20, h - 12),
                         "CAMNEMI — Offline consulting 전용 / 오프라인 상담 전용",
                         fontname="helv", fontsize=6.5, color=GOLD)
    doc.save(fp, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()

for p in PDFS:
    fp = os.path.join(B, p)
    if os.path.exists(fp):
        try:
            stamp(fp)
            print(f"워터마크 적용: {p}")
        except Exception as e:
            print(f"실패: {p} — {e}")
print("완료")
