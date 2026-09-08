#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read Dong-Eui spring lang guide PDF."""
import pymupdf
p = r"C:\Users\USER\AppData\Local\Temp\deu_spring_guide.pdf"
doc = pymupdf.open(p)
for i in range(len(doc)):
    t = doc[i].get_text()
    if t.strip():
        print(f"\n===== PAGE {i+1} =====")
        print(t)
