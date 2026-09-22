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

# 전문대(junior) 2027 상태 — 직접 수집(daily_junior_direct.py) 산출물 (adiga 미사용)
jr = load("_junior_direct_collected.json", {}) or {}
jr_done = {k: v for k, v in jr.items() if v.get("status") == "downloaded"}
jr_wait = {k: v for k, v in jr.items() if v.get("status") in ("no_pdf_link", "no_url")}

# 전문대 외국인 요강 수집 실적 — _junior_foreign_collected.json (별도 파일, 재생성돼도 유지)
jr_col = load("_junior_foreign_collected.json", {}) or {}
jr_collected = {e["name"]: e for e in jr_col.get("collected", [])}   # PDF 확보
jr_page = {e["name"]: e for e in jr_col.get("page_guide", [])}       # HTML page-guide
jr_missing = {e["name"]: e for e in jr_col.get("missing", [])}       # 무요강 확인
jr_col_2027 = {n for n, e in jr_collected.items() if str(e.get("year", "")).startswith("2027")}
# 확보 = 직접 수집으로 PDF 확보한 것 + 기존 수집 실적
jr_secured = dict(jr_done)
for n, e in jr_collected.items():
    jr_secured.setdefault(n, e)

# 요약: 2027 상태 보유 학교 수
ba2027 = sum(1 for m in master if str(m.get("ba_status", "")).startswith("2027"))
ma2027 = sum(1 for m in master if str(m.get("ma_status", "")).startswith("2027"))
lang2027 = sum(1 for m in master if str(m.get("lang_status", "")).startswith("2027"))

# 전문대 신규 감지: 전회 저장된 _guide_2027_junior_prev.json과 비교 → 오늘 새로 published된 전문대
jr_prev = load("_guide_2027_junior_prev.json", {}) or {}
new_jr_names = []
for k, v in jr_done.items():
    prev_st = str(jr_prev.get(k, {}).get("status", "")).startswith("2027_published")
    if not prev_st:
        new_jr_names.append(k)

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
E.append(Paragraph("Camnemi 외국인 모집요강 일일 수집 보고", title_s))
E.append(Paragraph(f"기준일: {today} · 생성: {datetime.datetime.now():%Y-%m-%d %H:%M}", body_s))
E.append(Spacer(1, 6*mm))

E.append(Paragraph(f"① 오늘 신규 감지 (BA {len(new_ba)} / MA {len(new_ma)} / 전문대 {len(new_jr_names)})", h_s))
if new_ba or new_ma or new_jr_names:
    def _row(level, x):
        if isinstance(x, dict):
            return [level, x.get("school",""), (x.get("url","") or "")[:70]]
        return [level, str(x), ""]
    data = [["구분","학교","요강 URL"]]
    for x in new_ba: data.append(_row("BA", x))
    for x in new_ma: data.append(_row("MA", x))
    for name in new_jr_names:
        v = jr.get(name, {})
        data.append(["전문대", name, (v.get("unvCd","") or "")])
    t = Table(data, colWidths=[15*mm, 40*mm, 125*mm])
    t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Malgun"),("FONTSIZE",(0,0),(-1,-1),8),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0d1b3e")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.4,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP")]))
    E.append(t)
else:
    E.append(Paragraph("오늘 신규 감지된 외국인 모집요강이 없습니다.", body_s))

E.append(Paragraph("② 최근 upsert된 2027 요강 (전문대 검출분 포함)", h_s))
if new_jr_names:
    E.append(Paragraph("※ 전문대 2027은 각 학교 공식 사이트에서 직접 수집(daily_junior_direct.py)한 결과입니다.", body_s))
E.append(Paragraph(f"   upsert 기록 {len(ups)}건", body_s))
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

E.append(Paragraph(f"③ 전체 2027 현황 (감시 {len(master)}교 + 전문대 {len(jr)}교)", h_s))
E.append(Paragraph(f"- 학부(BA) 2027 확보: <b>{ba2027}</b>교", body_s))
E.append(Paragraph(f"- 대학원(MA) 2027 확보: <b>{ma2027}</b>교", body_s))
E.append(Paragraph(f"- 어학(lang) 2027 확보: <b>{lang2027}</b>교", body_s))
E.append(Paragraph(f"- 전문대(junior) 요강 확보: <b>{len(jr_secured)}</b>교 (2027 {len(jr_col_2027)} / 2026 등 {len(jr_collected)-len(jr_col_2027)}) / page-guide {len(jr_page)} / 무요강 {len(jr_missing)}", body_s))
if jr_secured:
    E.append(Paragraph("  전문대 요강 확보: " + ", ".join(list(jr_secured.keys())[:30]), body_s))
if jr_page:
    E.append(Paragraph("  page-guide(HTML만, PDF 없음): " + ", ".join(list(jr_page.keys())[:20]), body_s))
E.append(Spacer(1, 8*mm))
E.append(Paragraph("※ 외국인(재외국민/외국인전형) 모집요강만 수집 · 일반 수시/정시 제외", body_s))

doc.build(E)

# 내일의 신규 감지 비교를 위해 오늘 상태를 prev로 저장
with open(os.path.join(B, "_guide_2027_junior_prev.json"), "w", encoding="utf-8") as f:
    json.dump(jr, f, ensure_ascii=False, indent=2)

print(path)