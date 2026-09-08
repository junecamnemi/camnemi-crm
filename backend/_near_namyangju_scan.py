#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan candidate lang PDFs (near Namyangju) for Cambodia inclusion/exclusion + fees."""
import pymupdf, os, re

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_어학연수_모집요강"
cands = ["대진대_한국어교육원.pdf","서정대학교_한국어교육원.pdf","신한대_한국어교육원.pdf",
         "삼육대_한국어교육원.pdf","성신여자대학교_한국어교육원.pdf","덕성여자대_한국어교육원.pdf",
         "국민대학교_한국어교육원.pdf","경기대_한국어교육원.pdf","대림대학교_한국어교육원.pdf"]

for fn in cands:
    p = os.path.join(DIR, fn)
    if not os.path.exists(p):
        print(f"\n### {fn}: 파일 없음"); continue
    doc = pymupdf.open(p)
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    # Cambodia presence
    has_cam = ('캄보' in txt) or ('Cambodia' in txt.lower())
    # exclusion country list context
    cam_note = "캄보디아 언급 있음" if has_cam else "캄보디아 언급 없음"
    # extract tuition
    fees = re.findall(r'[\d,]{6,}\s*원', txt)
    # find the country-list (학력인증/미수교 목록)
    m = re.search(r'(미수교국가|학력인증|국가목록|제한국가|미접수국가)', txt)
    ctx = ""
    if m:
        ctx = txt[m.start():m.start()+200].replace('\n',' ')
    print(f"\n### {fn}")
    print(f"   {cam_note} | 학비 언급: {fees[:3]}")
    if ctx: print(f"   국가안내: ...{ctx[:150]}...")
    doc.close()
