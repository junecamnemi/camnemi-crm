#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Branded K-트렌드 카드뉴스 (PIL, navy/gold) — K-pop 순위 + 드라마 런칭."""
from PIL import Image, ImageDraw, ImageFont
import os
W,H = 1080, 2400
NAVY=(16,32,66); GOLD=(220,168,40); WHITE=(255,255,255); SOFT=(230,235,245); MUTED=(160,170,190)
FB=r"C:\Windows\Fonts\malgunbd.ttf"; FR=r"C:\Windows\Fonts\malgun.ttf"
img=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(img)
def f(sz, bold=True): return ImageFont.truetype(FB if bold else FR, sz)
# header
d.rectangle((0,0,W,150), fill=(10,20,45))
d.text((60,40),"CAMNEMI",font=f(46),fill=GOLD)
d.text((60,100),"오늘의 K-트렌드 · 2026.09.16",font=f(28,False),fill=SOFT)
d.rectangle((60,160,280,166),fill=GOLD)
y=210
# K-POP TOP10
d.text((60,y),"🎵 K-POP 아이돌 차트 TOP10",font=f(38),fill=WHITE); y+=70
chart=[
 ("1","Saddle Up","aespa"),("2","Guitarist","도경수 D.O."),("3","LOVE ATTACK","RESCENE"),
 ("4","Skibidi","소녀시대-HRS"),("5","퇴사할게여","소연 SOYEON"),("6","BAD","ATEEZ"),
 ("7","갑자기","아이오아이 I.O.I"),("8","Deja Vu","RESCENE"),("9","REDRED","CORTIS"),
 ("10","만찬가","태연 TAEYEON")]
for rk,song,art in chart:
    d.rectangle((60,y,W-60,y+72), fill=(30,50,95), outline=(60,80,120))
    d.text((85,y+14),rk,font=f(34),fill=GOLD)
    d.text((160,y+10),song,font=f(30),fill=WHITE)
    d.text((160,y+46),art,font=f(22,False),fill=MUTED)
    y+=86
y+=30
d.rectangle((60,y,W-60,y+6),fill=GOLD); y+=40
# 드라마 런칭
d.text((60,y),"🎬 드라마 · 런칭",font=f(38),fill=WHITE); y+=70
dramas=[
 ("메이드 인 코리아 2","현빈·정우성·우도환 · Disney+ 9/9"),
 ("스캔들","손예진·지창욱·나나 · Netflix 9/18"),
 ("로또 1등도 출근합니다","tvN 9/14 첫방")]
for t,sub in dramas:
    d.ellipse((62,y+14,82,y+34),fill=GOLD)
    d.text((100,y+8),t,font=f(30),fill=WHITE)
    d.text((100,y+44),sub,font=f(22,False),fill=MUTED)
    y+=92
y+=30
d.text((60,y),"🎤 이달의 컴백",font=f(36),fill=WHITE); y+=66
d.text((60,y),"○ 컴백: 르세라핌 'Made My Night'(9/11) · 도경수 'DOPAMINE'(9/8)",font=f(24,False),fill=SOFT); y+=40
d.text((60,y),"○ 투어: BIGBANG 'XX:COSMOS' · ENHYPEN 'WALK THE LINE'",font=f(24,False),fill=SOFT); y+=40
d.text((60,y),"○ 라인업: 르세라핌 · BTS · BLACKPINK · IVE",font=f(24,False),fill=SOFT); y+=40
# footer
d.rectangle((0,H-150,W,H),fill=(10,20,45))
d.text((60,H-105),"CAMNEMI · 유학생을 위한 한국 소식",font=f(26),fill=GOLD)
d.text((60,H-60),"출처: 벅스 K-POP 차트 · 하이코리아 · OTT",font=f(20,False),fill=MUTED)
OUT=r"C:\Users\wisew\camnemi-crm\backend\K트렌드_카드뉴스_0916.png"
img.save(OUT)
print("저장:", OUT, os.path.getsize(OUT), "bytes |", W,"x",H)