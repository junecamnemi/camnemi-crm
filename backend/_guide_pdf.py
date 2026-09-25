#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render 유학생 한국생활 가이드 as a branded PDF (Camnemi navy/gold)."""
import json, os, pymupdf
B = r"C:\Users\wisew\camnemi-crm\backend"
G = json.load(open(os.path.join(B,"student_life_guide_kr.json"), encoding="utf-8"))
OUT = os.path.join(B, "유학생_한국생활_가이드.pdf")
NAVY=(0.08,0.13,0.27); GOLD=(0.85,0.65,0.13); WHITE=(1,1,1); INK=(0.15,0.15,0.2); GREY=(0.45,0.45,0.5)
FONT = r"C:\Windows\Fonts\malgun.ttf"; FONTB = r"C:\Windows\Fonts\malgunbd.ttf"
W,H = 595,842; M=46; CW=W-2*M
def page(doc):
    pg=doc.new_page(width=W,height=H)
    pg.insert_font(fontname="KR",fontfile=FONT); pg.insert_font(fontname="KRT",fontfile=FONTB)
    pg.draw_rect((0,0,W,H),color=WHITE,fill=WHITE)
    pg.draw_rect((0,0,W,26),color=NAVY,fill=NAVY)
    pg.insert_text((M,17),"CAMNEMI  ·  한국 유학생 생활 가이드",fontname="KRT",fontsize=10,color=GOLD)
    pg.draw_rect((0,H-20,W,H),color=NAVY,fill=NAVY)
    return pg
doc=pymupdf.open()
pg=page(doc)
# cover
pg.draw_rect((0,120,W,150),color=NAVY,fill=NAVY)
pg.insert_text((M,118),"외국인 유학생을 위한",fontname="KR",fontsize=18,color=INK)
pg.insert_text((M,150),"한국 생활 필수 가이드",fontname="KRT",fontsize=30,color=NAVY)
pg.draw_rect((M,175,250,4),color=GOLD,fill=GOLD)
y=210
for sec in G["sections"]:
    pg.insert_text((M,y),f"{sec['title']}",fontname="KRT",fontsize=14,color=NAVY); y+=22
    for it in sec["items"]:
        pg.insert_text((M+10,y),f"· {it}",fontname="KR",fontsize=9,color=INK); y+=16
    y+=8
    if y>H-60:
        pg=page(doc); y=70
pg.insert_text((M,y+10),"문의: 법무부 1345  ·  고용노동부 1350  ·  건강보험 1577-1000  (다국어)",fontname="KRT",fontsize=9,color=GOLD)
doc.subset_fonts()
doc.save(OUT, garbage=4, deflate=True)
print("PDF:", OUT, os.path.getsize(OUT), "bytes | 섹션", len(G["sections"]))