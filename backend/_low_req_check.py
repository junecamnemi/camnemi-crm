#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymupdf, re, os
DIR = r"C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인"
KEYS = ['우송','동신','제주국제','한일장신','중원','창신','한동','고신','선문']
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith('.pdf'): continue
    m0 = re.match(r'\d+_(.+?)(?:\[.*\])?_', fn)
    school = m0.group(1) if m0 else fn
    if not any(k in school for k in KEYS): continue
    doc = pymupdf.open(os.path.join(DIR, fn))
    full = '\n'.join(p.get_text() for p in doc)
    doc.close()
    print(f'=== {school} ===')
    m = re.search(r'IELTS\s*\d+\.?\d*', full)
    if m:
        ctx = full[max(0, m.start()-100):m.start()+100].replace('\n', ' ')
        ctx = re.sub(r'\s+', ' ', ctx)
        print(f'  IELTS: {m.group(0)} | 문맥: {ctx[:160]}')
    else:
        print('  IELTS 언급 없음')
    topik_pat = re.compile(r'TOPIK\s*\d')
    print(f'  TOPIK 언급: {bool(topik_pat.search(full))}')
    print()
