#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""일일 외국인 모집요강 수집 PDF 생성 → 크론이 이 파일을 텔레그램으로 전송."""
import json, os, datetime, glob

B = r"C:\Users\USER\camnemi-crm\backend"
OUTDIR = r"C:\Users\USER\camnemi-crm\backend\daily_guide_pdf"
os.makedirs(OUTDIR, exist_ok=True)

def load(p, default=None):
    try: return json.load(open(os.path.join(B,p), encoding="utf-8"))
    except: return default if default is not None else {}

today = datetime.date.today().isoformat()
newd = load("_homepage_2027_new.json", {})
new_ba = newd.get("new_ba", []) or []
new_ma = newd.get("new_ma", []) or []
ups = load("upserted_2027.json", {}).get("upserts", []) or []
master = load("_guide_2027_master.json", []) or []

# 요약: 2027 상태 보유 학교 수
ba2027 = sum(1 for m in master if str(m.get("ba_status","")).startswith("2027"))
ma2027 = sum(1 for m in master if str(m.get("ma_status","")).startswith("2027"))
lang2027 = sum(1 for m in master if str(m.get("lang_status","")).startswith("2027"))

# PDF 생성
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

FONT = r"C:\Windows\Fonts\malgun.ttf"
pdfmetrics.registerFont(TTFont("Malgun", FONT))
styles = getSampleStyleSheet()
title_s = ParagraphStyle("t", parent=styles["Title"], fontName="Malgun", fontSize=18, leading=24)
h_s = ParagraphStyle("h", parent=styles["Heading2"], fontName="Malgun", fontSize=13, leading=18, spaceBefore=10)
body_s = ParagraphStyle("b", parent=styles["Normal"], fontName="Malgun", fontSize=9.5, leading=14)

fname = f"외국인모집요강_일일수집_{today}.pdf"
path = os.path.join(OUTDIR, fname)
doc = SimpleDocTemplate(path, pagesize=A4, topMargin=18*mm, bottomMargin=18*mm)
E = []
E.append(Paragraph(f"Camnemi 외국인 모집요강 일일 수집 보고", title_s))
E.append(Paragraph(f"기준일: {today} · 생성: {datetime.datetime.now():%Y-%m-%d %H:%M}", body_s))
E.append(Spacer(1, 6*mm))

E.append(Paragraph(f"① 오늘 신규 감지 (BA {len(new_ba)} / MA {len(new_ma)})", h_s))
if new_ba or new_ma:
    data = [["구분","학교","요강 URL"]]
    for x in new_ba: data.append(["BA", x.get("school",""), (x.get("url","") or "")[:70]])
    for x in new_ma: data.append(["MA", x.get("school",""), (x.get("url","") or "")[:70]])
    t = Table(data, colWidths=[15*mm, 40*mm, 125*mm])
    t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Malgun"),("FONTSIZE",(0,0),(-1,-1),8),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0d1b3e")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP")]))
    E.append(t)
else:
    E.append(Paragraph("오늘 신규 감지된 외국인 모집요강이 없습니다.", body_s))

E.append(Paragraph(f"② 최근 upsert된 2027 요강 ({len(ups)}건)", h_s))
if ups:
    data = [["레벨","학교","요강"]]
    for u in ups:
        data.append([str(u[1]).upper(), u[0], (u[2] or "")[:75]])
    t = Table(data, colWidths=[15*mm, 40*mm, 125*mm])
    t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Malgun"),("FONTSIZE",(0,0),(-1,-1),7.5),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0d1b3e")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP")]))
    E.append(t)
else:
    E.append(Paragraph("upsert 기록 없음.", body_s))

E.append(Paragraph(f"③ 전체 2027 현황 (감시 {len(master)}교)", h_s))
E.append(Paragraph(f"- 학부(BA) 2027 확보: <b>{ba2027}</b>교", body_s))
E.append(Paragraph(f"- 대학원(MA) 2027 확보: <b>{ma2027}</b>교", body_s))
E.append(Paragraph(f"- 어학(lang) 2027 확보: <b>{lang2027}</b>교", body_s))
E.append(Spacer(1, 8*mm))
E.append(Paragraph("※ 외국인(재외국민/외국인전형) 모집요강만 수집 · 일반 수시/정시 제외", body_s))

doc.build(E)
print(path)