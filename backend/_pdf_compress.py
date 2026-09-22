# -*- coding: utf-8 -*-
"""Compress all PDFs in guides/ using pymupdf (recompress streams, deflate)."""
import os, pymupdf

GUIDES = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\guides"

total_before = 0
total_after = 0
n = 0
for root, dirs, files in os.walk(GUIDES):
    for f in files:
        if not f.lower().endswith(".pdf"): continue
        p = os.path.join(root, f)
        before = os.path.getsize(p)
        total_before += before
        try:
            doc = pymupdf.open(p)
            # recompress: save with garbage=4, deflate, and recompress images
            doc.save(p + ".tmp", garbage=4, deflate=True, clean=True)
            doc.close()
            after = os.path.getsize(p + ".tmp")
            if after < before:
                os.replace(p + ".tmp", p)
                total_after += after
            else:
                os.remove(p + ".tmp")
                total_after += before
            n += 1
        except Exception as e:
            print("FAIL:", f, e)
            total_after += before

print(f"압축 완료: {n}개")
print(f"용량: {total_before/1e6:.1f}MB -> {total_after/1e6:.1f}MB ({(1-total_after/total_before)*100:.1f}% 감소)")
