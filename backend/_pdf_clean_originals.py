# -*- coding: utf-8 -*-
"""Remove original PDFs from adiga folders (now consolidated in guides/).
Keeps HTML, manifests, scripts, and non-PDF files (foreigner HTML = the guide)."""
import os

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

# folders to clean (PDFs only)
FOLDERS = [
    "adiga_2026_외국인_모집요강",
    "adiga_2027_외국인_모집요강",
    "adiga_2026_대학원_모집요강",
    "adiga_2027_대학원_모집요강",
    "adiga_2026_전문대학_모집요강",
    "adiga_2026_어학연수_모집요강",
    "adiga_2027_어학연수_모집요강",
]

removed = 0
for folder in FOLDERS:
    base = os.path.join(UP, folder)
    if not os.path.isdir(base): continue
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower().endswith(".pdf"):
                p = os.path.join(root, f)
                try:
                    os.remove(p)
                    removed += 1
                except OSError as e:
                    print("FAIL:", p, e)

print(f"원본 PDF 삭제: {removed}개 (HTML·매니페스트·스크립트는 유지)")
