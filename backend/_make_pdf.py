#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the English-track university recommendation PDF with Korean font support."""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# Register Korean fonts (Windows)
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD_PATH))
    addMapping("Malgun", 0, 0, "Malgun")
    addMapping("Malgun", 1, 0, "Malgun-Bold")
    FONT = "Malgun"
    FONT_BOLD = "Malgun-Bold"
else:
    FONT = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

OUT = r"C:\Users\USER\camnemi-crm\backend\영어트랙_대학정리_2026_2027.pdf"

# ---------- Data: English-track schools (2026/2027) ----------
# fields: school, loc, rank, majors, lang, period, tuition, scholarship
DATA = [
    # 2027 확정 - 상위권
    {
        "school": "중앙대학교 (Chung-Ang Univ)", "loc": "서울", "rank": "#8",
        "majors": "게임융합학과 (100% 영어수업)",
        "lang": "IELTS 5.5 / TOEFL iBT 60",
        "period": "2026.8.31 ~ 9.18",
        "tuition": "₩5,320,000 ~ ₩8,468,000/학기",
        "scholarship": "외국인 장학금: TOPIK6·IELTS6.5→수업료 100%",
        "year": "2027",
    },
    {
        "school": "인하대학교 (Inha Univ)", "loc": "인천", "rank": "#12",
        "majors": "IBT학과(국제비즈니스무역) / ISE학과(통합시스템공학) / 글로벌자유전공학부",
        "lang": "IELTS 5.5 / TOEFL iBT 71",
        "period": "2026.9.30 ~ 11.5",
        "tuition": "확인 필요",
        "scholarship": "글로벌1장학: IELTS9→전액4년+생활보조 / TOPIK4→30%",
        "year": "2027",
    },
    {
        "school": "숙명여자대학교 (Sookmyung WU)", "loc": "서울", "rank": "#20",
        "majors": "글로벌서비스학부(글로벌협력·앙트러프러너십) / 영어영문학부(TESL)",
        "lang": "IELTS 5.5 (영어트랙 일부전공)",
        "period": "1차 10.7~16 / 2차 11.6~20 / 3차 12.3~18",
        "tuition": "확인 필요",
        "scholarship": "세계지역핵심인재: IELTS8→70% / TOPIK6→90%",
        "year": "2027",
    },
    {
        "school": "가천대학교 (Gachon Univ)", "loc": "경기", "rank": "#25",
        "majors": "경영학과(ENG) / 컴퓨터공학과(ENG) / 반도체공학과(ENG) / 시스템반도체학과(ENG)",
        "lang": "IELTS 5.5 / TOEFL iBT 59",
        "period": "2026.10.12 ~ 10.23",
        "tuition": "₩4,173,800 ~ ₩5,665,800/학기",
        "scholarship": "외국인장학: TOPIK4~5→첫학기 등록금 100% / TOPIK3→40%",
        "year": "2027",
    },
    # 2027 - 수도권/지방
    {
        "school": "단국대학교 (Dankook Univ)", "loc": "경기", "rank": "-",
        "majors": "국제경영학과 / 모바일시스템공학과 / 바이오소재융합공학과 / 한국학과",
        "lang": "IELTS 5.5 / TOEFL iBT 71",
        "period": "1차 10.1~16 / 2차 12.2~18",
        "tuition": "₩4,230,000 ~ ₩6,799,000/학기",
        "scholarship": "영어트랙: TOEFL iBT71→수업료 50% 면제(1학기)",
        "year": "2027",
    },
    {
        "school": "계명대학교 (Keimyung Univ)", "loc": "대구", "rank": "-",
        "majors": "Keimyung Adams College / 디지펜게임공학과",
        "lang": "IELTS 5.5 (일부 5.0) / TOEFL iBT 80",
        "period": "2026.9.21 ~ 10.23",
        "tuition": "₩3,250,000 ~ ₩4,856,000/학기",
        "scholarship": "외국인장학: TOPIK5→수업료 100% / TOPIK3→30%",
        "year": "2027",
    },
    {
        "school": "목원대학교 (Mokwon Univ)", "loc": "대전", "rank": "-",
        "majors": "글로벌융합학부: 글로벌IT공학전공 / 글로벌경제·개발협력전공",
        "lang": "IELTS 5.5 / TOEFL iBT 71",
        "period": "1차 9.16~10.7 / 2차 11.23~12.23",
        "tuition": "확인 필요",
        "scholarship": "입학장학금: TOPIK3→등록금 20% 감면",
        "year": "2027",
    },
    {
        "school": "배재대학교 (Pai Chai Univ)", "loc": "대전", "rank": "-",
        "majors": "글로벌융합학부: 글로벌경영학과 / 글로벌IT학과",
        "lang": "IELTS 5.5 / TOEFL iBT 71",
        "period": "2026.10.16 ~ 10.22",
        "tuition": "확인 필요",
        "scholarship": "GKS(정부초청) 별도 / 영어트랙 입학생 10명 선발",
        "year": "2027",
    },
    {
        "school": "우송대학교 (Woosong Univ)", "loc": "대전", "rank": "-",
        "majors": "솔브릿지경영학부 / AI·빅데이터학과 / 글로벌철도학과 / 글로벌미디어AI영상학과 / 글로벌호텔관광 / 글로벌외식조리 / 글로벌제과제빵 (100% 영어수업 ◉)",
        "lang": "IELTS 5.5 / TOEFL iBT 59",
        "period": "2026.7.16 ~",
        "tuition": "확인 필요",
        "scholarship": "외국어성적우수: TOEFL iBT85→4년 전액 감면",
        "year": "2027",
    },
    {
        "school": "을지대학교 (Eulji Univ)", "loc": "대전", "rank": "-",
        "majors": "글로벌빅데이터AI학과 (외국인 전담 영어트랙)",
        "lang": "IELTS 5.5 / TOEFL iBT 59",
        "period": "2026.9.7 ~ 9.11",
        "tuition": "확인 필요",
        "scholarship": "순수외국인 입학장학: 4년 수업료 지원(성적별)",
        "year": "2027",
    },
    {
        "school": "인제대학교 (Inje Univ)", "loc": "경남", "rank": "-",
        "majors": "외국인 유학생 전담학과 (영어트랙): AI컴퓨터학과 등",
        "lang": "IELTS 5.5 / TOEFL iBT 71",
        "period": "2026.9.7 ~ 9.11",
        "tuition": "확인 필요",
        "scholarship": "입학장학 D형(영어트랙): IELTS6.5→등록금 50%",
        "year": "2027",
    },
    # 2026 실측
    {
        "school": "한국외국어대학교 (HUFS)", "loc": "서울", "rank": "#17",
        "majors": "AI데이터융합학부 / Finance&AI융합학부 / 컴퓨터공학부 / 국제학부 등",
        "lang": "IELTS 5.5 / TOEFL iBT 59",
        "period": "2025.9.1 ~ 9.12 (2026)",
        "tuition": "₩4,201,000 ~ ₩5,273,000/학기",
        "scholarship": "총장장학: 등록금100% / 학장장학 50%",
        "year": "2026",
    },
    {
        "school": "세종대학교 (Sejong Univ)", "loc": "서울", "rank": "#19",
        "majors": "인공지능데이터사이언스학과 / 컴퓨터공학과 / 소프트웨어학과 등",
        "lang": "IELTS 5.5 / TOPIK 3",
        "period": "2025.9.8 ~ 9.19 (2026)",
        "tuition": "₩4,556,000 ~ ₩6,237,000/학기",
        "scholarship": "외국인장학: TOPIK3→30% / 6→100%",
        "year": "2026",
    },
    {
        "school": "건국대학교 (Konkuk Univ)", "loc": "서울", "rank": "#8",
        "majors": "컴퓨터소프트웨어학과 / 컴퓨터공학부 / 응용통계학과 등",
        "lang": "IELTS 5.5 / TOPIK 3",
        "period": "2025.9.4 ~ 9.11 (2026)",
        "tuition": "₩4,636,000 ~ ₩7,133,000/학기",
        "scholarship": "우수외국인장학: TOPIK3→30% / 6→100%",
        "year": "2026",
    },
    {
        "school": "한림대학교 (Hallym Univ)", "loc": "강원", "rank": "-",
        "majors": "데이터사이언스학부 / 소프트웨어학부 / 인공지능융합학부",
        "lang": "IELTS 5.5 / TOPIK 2",
        "period": "2025.11.17 ~ 12.23 (2026)",
        "tuition": "₩3,575,800 ~ ₩4,644,800/학기",
        "scholarship": "순수외국인장학: TOPIK6→80% 감면",
        "year": "2026",
    },
]

# ---------- Build PDF ----------
doc = SimpleDocTemplate(
    OUT, pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=14*mm, bottomMargin=14*mm,
    title="2026/2027 영어트랙 지원 가능 대학 정리",
    author="Camnemi University Advisor",
)

style_title = ParagraphStyle("t", fontName=FONT_BOLD, fontSize=16, leading=22, alignment=1, spaceAfter=4)
style_sub = ParagraphStyle("s", fontName=FONT, fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#555555"), spaceAfter=10)
style_h = ParagraphStyle("h", fontName=FONT_BOLD, fontSize=13, leading=18, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1a3a6b"))
style_cell = ParagraphStyle("c", fontName=FONT, fontSize=7.5, leading=10.5)
style_cell_b = ParagraphStyle("cb", fontName=FONT_BOLD, fontSize=7.5, leading=10.5)

story = []
story.append(Paragraph("🎓 2026/2027 영어트랙 지원 가능 대학 정리", style_title))
story.append(Paragraph("IELTS 5.5 기준 · 외국인 전형 · Camnemi University Advisor", style_sub))

# Split by year
for year, label in [("2027", "✅ 2027년 모집요강 확정 (최신)"), ("2026", "📅 2026년 가이드 (2027 요강 미발간)")]:
    rows = [r for r in DATA if r["year"] == year]
    if not rows:
        continue
    story.append(Paragraph(label, style_h))
    header = ["학교", "위치", "순위", "전공 (영어트랙)", "언어조건", "모집일자", "등록금/학기", "장학금"]
    table_rows = [header]
    for r in rows:
        table_rows.append([
            Paragraph(r["school"], style_cell_b),
            Paragraph(r["loc"], style_cell),
            Paragraph(r["rank"], style_cell),
            Paragraph(r["majors"], style_cell),
            Paragraph(r["lang"], style_cell),
            Paragraph(r["period"], style_cell),
            Paragraph(r["tuition"], style_cell),
            Paragraph(r["scholarship"], style_cell),
        ])
    tbl = Table(table_rows, colWidths=[32*mm, 12*mm, 10*mm, 45*mm, 24*mm, 26*mm, 26*mm, 34*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a3a6b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef3fa")]),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 4))

story.append(Spacer(1, 8))
story.append(Paragraph("※ 영어트랙 = 영어로 진행되는 학과(부). 일부 학교는 전 학과 영어트랙, 일부는 특정 학과만 해당. 지원 전 최신 모집요강 확인 필요.", style_sub))

doc.build(story)
print("PDF 생성 완료:", OUT)
print("파일 크기:", os.path.getsize(OUT), "bytes")
