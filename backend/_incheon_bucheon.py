#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract winter(겨울/12월) term + application from Incheon/Bucheon lang PDFs."""
import pymupdf, os, re
D = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
cands = {
 "인천대학교_한국어교육원.pdf":"인천대",
 "인하대_한국어교육원.pdf":"인하대",
 "가톨릭대_한국어교육원.pdf":"가톨릭대(부천)",
 "부천대학교_한국어교육원.pdf":"부천대",
}
for fn,name in cands.items():
    p=os.path.join(D,fn)
    if not os.path.exists(p): print(f"\n### {name}: 파일없음"); continue
    doc=pymupdf.open(p); txt="".join(doc[i].get_text() for i in range(len(doc))); doc.close()
    print(f"\n\n########## {name} ({fn}) ##########")
    # winter/겨울 context
    for m in re.finditer(r'겨울|12월|11\.\d+|12\.\d+|겨울학기', txt):
        s=max(0,m.start()-100); e=min(len(txt),m.end()+150)
        seg=txt[s:e].replace("\n"," ")
        print(f"  • ...{seg}...")
        # cap output per file
        if m.start()>8000: break
