#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the 13 downloaded 2027 guide PDFs: year + foreigner-track + school match."""
import pymupdf, os, re
BA = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_외국인_모집요강\own_site"
MA = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_대학원_모집요강"
files = [(BA,f) for f in os.listdir(BA) if f.endswith('.pdf')] + [(MA,f) for f in os.listdir(MA) if f.endswith('.pdf')]
for d,fn in sorted(files):
    p = os.path.join(d,fn)
    try:
        doc = pymupdf.open(p)
        txt = "".join(doc[i].get_text() for i in range(min(len(doc),25)))
        doc.close()
    except Exception as e:
        print(f"{fn}: OPEN FAIL {e}"); continue
    has27 = '2027' in txt
    has26only = ('2027' not in txt)
    foreign = ('외국인' in txt)
    grad = ('대학원' in txt)
    ba = ('학부' in txt) or ('신입학' in txt)
    print(f"{fn:38s} | 2027:{'Y' if has27 else 'N'} 외국인:{'Y' if foreign else 'N'} 대학원:{'Y' if grad else 'N'} 학부:{'Y' if ba else 'N'} | {len(txt)}자")
