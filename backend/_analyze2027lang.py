#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze the 4 downloaded 2027 language PDFs: extract 2027 terms, tuition, D-4, dorm."""
import pymupdf, os, re, json

DIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2027_어학연수_모집요강"
files = ["가톨릭대_한국어교육원_2027.pdf","서강대_한국어교육원_2027.pdf",
         "연세대_한국어교육원_2027.pdf","이화여자대학교_한국어교육원_2027.pdf"]

for fn in files:
    p = os.path.join(DIR, fn)
    doc = pymupdf.open(p)
    txt = "".join(doc[i].get_text() for i in range(len(doc)))
    doc.close()
    print(f"\n\n########## {fn} ({os.path.getsize(p)//1024}KB, {len(txt)}자) ##########")
    # 2027 dates
    dates2027 = re.findall(r'20(?:26|27|28)\s*[./년-]\s*\d+\s*[./월-]\s*\d+', txt)[:10]
    print("날짜 감지:", dates2027[:8])
    # tuition
    fees = re.findall(r'[\d,]{6,}\s*원', txt)
    print("금액:", fees[:5])
    # D-4 / key sections
    for kw in ["D-4","수강료","등록금","학기","모집기간","접수","신청"]:
        if kw in txt: pass
    print("첫 800자:", txt[:800].replace("\n"," "))
