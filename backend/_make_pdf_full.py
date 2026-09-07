#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the COMPLETE English-track university PDF (2026/2027) with Korean font.
Includes all verified English-track schools incl. 전북대 국제이공학부."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD_PATH))
addMapping("Malgun", 0, 0, "Malgun")
addMapping("Malgun", 1, 0, "Malgun-Bold")
FONT = "Malgun"
FONT_BOLD = "Malgun-Bold"

OUT = r"C:\Users\USER\camnemi-crm\backend\영어트랙_대학정리_2026_2027_전체.pdf"

# school, loc, rank, majors(eng track), lang, period, tuition, scholarship, year
DATA = [
    # ============ 2027 ============
    {"school": "중앙대학교 (Chung-Ang Univ)", "loc": "서울", "rank": "#8",
     "majors": "게임융합학과 (100% 영어수업) / 융합공학부", "lang": "IELTS 5.5 / TOEFL iBT 60",
     "period": "2026.8.31 ~ 9.18", "tuition": "₩5,320,000~₩8,468,000",
     "scholarship": "외국인장학: IELTS6.5/TOPIK6→100%", "year": "2027"},
    {"school": "인하대학교 (Inha Univ)", "loc": "인천", "rank": "#12",
     "majors": "IBT학과(국제비즈니스무역) / ISE학과(통합시스템공학) / 글로벌자유전공학부", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2026.9.30 ~ 11.5", "tuition": "확인 필요",
     "scholarship": "글로벌1장학: IELTS9→전액4년+생활보조", "year": "2027"},
    {"school": "숙명여자대학교 (Sookmyung WU)", "loc": "서울", "rank": "#20",
     "majors": "글로벌서비스학부(글로벌협력·앙트러프러너십) / 영어영문학부", "lang": "IELTS 5.5(영어트랙)",
     "period": "1차 10.7~16 / 2차 11.6~20 / 3차 12.3~18", "tuition": "확인 필요",
     "scholarship": "세계지역핵심인재: IELTS8→70%", "year": "2027"},
    {"school": "가천대학교 (Gachon Univ)", "loc": "경기", "rank": "#25",
     "majors": "경영학과(ENG) / 컴퓨터공학과(ENG) / 반도체공학과(ENG) / 시스템반도체학과(ENG)", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2026.10.12 ~ 10.23", "tuition": "₩4,173,800~₩5,665,800",
     "scholarship": "외국인장학: TOPIK4~5→100% / TOPIK3→40%", "year": "2027"},
    {"school": "광운대학교 (Kwangwoon Univ)", "loc": "서울", "rank": "-",
     "majors": "반도체시스템공학부(영어트랙만) / 정보융합학부 데이터사이언스전공 / 로봇학부 AI로봇 / 소프트웨어학부 / 국제통상학부 / 경영학부 빅데이터경영", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2027학년도 1학기", "tuition": "확인 필요",
     "scholarship": "영어트랙: IELTS 5.5 인정", "year": "2027"},
    {"school": "한양대학교 ERICA", "loc": "경기(안산)", "rank": "-",
     "majors": "컴퓨터학부(영어트랙) / ICT융합학부(데이터인텔리전스·디자인컨버전스) / 인공지능학과 / 수리데이터사이언스학과 / 경제학부·경영학부(영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2027학년도 1학기", "tuition": "확인 필요",
     "scholarship": "영어트랙: IELTS 5.5 성적표 필수", "year": "2027"},
    {"school": "한경국립대학교 (Hankyong Nat'l)", "loc": "경기(안성)", "rank": "-",
     "majors": "글로벌경영전공 / English Language·Literature and Language Technology", "lang": "IELTS 5.5 / TOEFL iBT",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "TOPIK3/IELTS5.5 → 장학", "year": "2027"},
    {"school": "단국대학교 (Dankook Univ)", "loc": "경기", "rank": "-",
     "majors": "국제경영학과 / 모바일시스템공학과 / 바이오소재융합공학과 / 한국학과", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "1차 10.1~16 / 2차 12.2~18", "tuition": "₩4,230,000~₩6,799,000",
     "scholarship": "영어트랙: TOEFL iBT71→수업료 50%", "year": "2027"},
    {"school": "계명대학교 (Keimyung Univ)", "loc": "대구", "rank": "-",
     "majors": "Keimyung Adams College / 디지펜게임공학과", "lang": "IELTS 5.5(일부 5.0) / TOEFL iBT 80",
     "period": "2026.9.21 ~ 10.23", "tuition": "₩3,250,000~₩4,856,000",
     "scholarship": "외국인장학: TOPIK5→100%", "year": "2027"},
    {"school": "목원대학교 (Mokwon Univ)", "loc": "대전", "rank": "-",
     "majors": "글로벌융합학부: 글로벌IT공학전공 / 글로벌경제·개발협력전공", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "1차 9.16~10.7 / 2차 11.23~12.23", "tuition": "확인 필요",
     "scholarship": "입학장학: TOPIK3→20%", "year": "2027"},
    {"school": "배재대학교 (Pai Chai Univ)", "loc": "대전", "rank": "-",
     "majors": "글로벌융합학부: 글로벌경영학과 / 글로벌IT학과", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2026.10.16 ~ 10.22", "tuition": "확인 필요",
     "scholarship": "GKS 별도 / 영어트랙 10명 선발", "year": "2027"},
    {"school": "우송대학교 (Woosong Univ)", "loc": "대전", "rank": "-",
     "majors": "솔브릿지경영학부 / AI·빅데이터학과 / 글로벌철도학과 / 글로벌미디어AI영상학과 / 글로벌호텔관광 / 글로벌외식조리 / 글로벌제과제빵 (100% 영어수업)", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2026.7.16 ~", "tuition": "확인 필요",
     "scholarship": "TOEFL iBT85→4년 전액", "year": "2027"},
    {"school": "을지대학교 (Eulji Univ)", "loc": "대전", "rank": "-",
     "majors": "글로벌빅데이터AI학과 (외국인 전담 영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2026.9.7 ~ 9.11", "tuition": "확인 필요",
     "scholarship": "순수외국인 입학장학: 4년 수업료", "year": "2027"},
    {"school": "인제대학교 (Inje Univ)", "loc": "경남", "rank": "-",
     "majors": "외국인 유학생 전담학과(영어트랙): AI컴퓨터학과 / 글로벌경영학과 등", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2026.9.7 ~ 9.11", "tuition": "확인 필요",
     "scholarship": "입학장학 D형: IELTS6.5→50%", "year": "2027"},
    {"school": "선문대학교 (Sun Moon Univ)", "loc": "충남", "rank": "-",
     "majors": "컴퓨터공학부(영어트랙) / 글로벌자유전공학부", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2027학년도", "tuition": "₩3,634,000~₩4,471,000",
     "scholarship": "영어능력 우수 장학", "year": "2027"},
    {"school": "한동대학교 (Handong Univ)", "loc": "경북(포항)", "rank": "-",
     "majors": "영어강의 학과 (전 과정)", "lang": "IELTS 5.5 / TOEFL iBT 85",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "IELTS5.5→등록금 50%", "year": "2027"},
    {"school": "고신대학교 (Kosin Univ)", "loc": "부산", "rank": "-",
     "majors": "영어트랙 전학과 (TOEFL iBT59/IELTS5.5)", "lang": "IELTS 5.5",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "영어과정 장학", "year": "2027"},
    {"school": "동신대학교 (Dongshin Univ)", "loc": "전남(나주)", "rank": "-",
     "majors": "국제학부(글로벌경영전공·호텔투어리즘·IT전공) / 식품영양·스포츠의학·반려동물 등 (영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},
    {"school": "중원대학교 (Jungwon Univ)", "loc": "충북", "rank": "-",
     "majors": "국제대학(한국어학과 등) / 경영·항공서비스·기계·전기전자·뷰티메디컬·생명공학 등 (영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},
    {"school": "창신대학교 (Changshin Univ)", "loc": "경남(창원)", "rank": "-",
     "majors": "글로벌학부(스마트경영·IT제조전공) [외국인 전담 영어트랙]", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},
    {"school": "제주국제대학교 (Jeju Int'l)", "loc": "제주", "rank": "-",
     "majors": "영어트랙 운영 전공 (항공경영·호텔관광·소방방재 등)", "lang": "IELTS 5.5 / TOEFL iBT 3.5",
     "period": "2026-2 순수외국인", "tuition": "₩2,844,000~₩3,096,000",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},
    {"school": "한일장신대학교 (Hanjil Univ)", "loc": "전북", "rank": "-",
     "majors": "AI융합혁신경영학과 (영어트랙)", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2027학년도", "tuition": "확인 필요",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},
    {"school": "평택대학교 (Pyeongtaek Univ)", "loc": "경기", "rank": "-",
     "majors": "AI융합학과 / 데이터정보학과 / 융합소프트웨어학과 / 경영학과(이중언어) / 국제무역·국제물류", "lang": "IELTS 5.5 / TOEFL iBT 71",
     "period": "2025.11.10~12.19(2026 표기)", "tuition": "₩3,532,000~₩4,593,000",
     "scholarship": "영어트랙 IELTS 5.5", "year": "2027"},

    # ============ 전북대 (특별 추가) ============
    {"school": "전북대학교 (Jeonbuk Nat'l Univ) ★", "loc": "전북(전주)", "rank": "-",
     "majors": "국제이공학부(엔지니어링사이언스) — 전기·전자·컴퓨터 계열, 4년 영어강의 / 국제학부(국제협력) [영어트랙]", "lang": "IELTS 5.5 / TEPS 600",
     "period": "2026 전기: 1차 9.22~10.3 / 2차 11.5~19 (2026)", "tuition": "확인 필요",
     "scholarship": "국제이공학부 외국인 장학 (학업성적 80%+영어 20%)", "year": "2027"},

    # ============ 2026 ============
    {"school": "한국외국어대학교 (HUFS)", "loc": "서울", "rank": "#17",
     "majors": "AI데이터융합학부 / Finance&AI / 컴퓨터공학부 / 국제학부", "lang": "IELTS 5.5 / TOEFL iBT 59",
     "period": "2025.9.1~9.12 (2026)", "tuition": "₩4,201,000~₩5,273,000",
     "scholarship": "총장장학: 100% / 학장 50%", "year": "2026"},
    {"school": "세종대학교 (Sejong Univ)", "loc": "서울", "rank": "#19",
     "majors": "인공지능데이터사이언스학과 / 컴퓨터공학 / 소프트웨어학과 등", "lang": "IELTS 5.5 / TOPIK 3",
     "period": "2025.9.8~9.19 (2026)", "tuition": "₩4,556,000~₩6,237,000",
     "scholarship": "TOPIK3→30% / 6→100%", "year": "2026"},
    {"school": "건국대학교 (Konkuk Univ)", "loc": "서울", "rank": "#8",
     "majors": "컴퓨터소프트웨어학과 / 컴퓨터공학부 / 응용통계학과", "lang": "IELTS 5.5 / TOPIK 3",
     "period": "2025.9.4~9.11 (2026)", "tuition": "₩4,636,000~₩7,133,000",
     "scholarship": "TOPIK3→30% / 6→100%", "year": "2026"},
    {"school": "한림대학교 (Hallym Univ)", "loc": "강원", "rank": "-",
     "majors": "데이터사이언스학부 / 소프트웨어학부 / 인공지능융합학부", "lang": "IELTS 5.5 / TOPIK 2",
     "period": "2025.11.17~12.23 (2026)", "tuition": "₩3,575,800~₩4,644,800",
     "scholarship": "TOPIK6→80%", "year": "2026"},
]

# ---------- Build PDF ----------
doc = SimpleDocTemplate(
    OUT, pagesize=A4, leftMargin=10*mm, rightMargin=10*mm, topMargin=13*mm, bottomMargin=13*mm,
    title="2026/2027 영어트랙 지원 가능 대학 정리 (전체)",
    author="Camnemi University Advisor",
)

st_title = ParagraphStyle("t", fontName=FONT_BOLD, fontSize=15, leading=20, alignment=1, spaceAfter=3)
st_sub = ParagraphStyle("s", fontName=FONT, fontSize=9, leading=13, alignment=1, textColor=colors.HexColor("#555555"), spaceAfter=8)
st_h = ParagraphStyle("h", fontName=FONT_BOLD, fontSize=12, leading=17, spaceBefore=10, spaceAfter=5, textColor=colors.HexColor("#1a3a6b"))
st_c = ParagraphStyle("c", fontName=FONT, fontSize=6.8, leading=9.6)
st_cb = ParagraphStyle("cb", fontName=FONT_BOLD, fontSize=6.8, leading=9.6)
st_note = ParagraphStyle("n", fontName=FONT, fontSize=7.5, leading=11, textColor=colors.HexColor("#777777"), spaceBefore=6)

story = []
story.append(Paragraph("🎓 2026/2027 영어트랙 지원 가능 대학 정리 (전체)", st_title))
story.append(Paragraph("IELTS 5.5 기준 · 외국인 전형 · Camnemi University Advisor", st_sub))

for year, label in [("2027", "✅ 2027년 모집요강 확정 (최신)"), ("2026", "📅 2026년 가이드 (2027 요강 미발간)")]:
    rows = [r for r in DATA if r["year"] == year]
    if not rows:
        continue
    story.append(Paragraph(label, st_h))
    header = ["학교", "위치", "순위", "전공 (영어트랙)", "언어조건", "모집일자", "등록금/학기", "장학금"]
    tr = [header]
    for r in rows:
        tr.append([
            Paragraph(r["school"], st_cb), Paragraph(r["loc"], st_c),
            Paragraph(r["rank"], st_c), Paragraph(r["majors"], st_c),
            Paragraph(r["lang"], st_c), Paragraph(r["period"], st_c),
            Paragraph(r["tuition"], st_c), Paragraph(r["scholarship"], st_c),
        ])
    tbl = Table(tr, colWidths=[30*mm, 13*mm, 9*mm, 46*mm, 23*mm, 25*mm, 24*mm, 28*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a3a6b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef3fa")]),
        ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 4))

story.append(Paragraph("※ 영어트랙 = 영어로 진행되는 학과(부). 전북대 국제이공학부는 4년 전공을 영어로 강의, IELTS 5.5 인정. ※ 언어조건은 각 대학 2026/2027 모집요강 기준이며, 지원 전 최신 요강 반드시 확인. ※ 등록금 '확인 필요' = 요강에서 미확인, 대학별 학과 등록금표 참조.", st_note))

doc.build(story)
print("PDF 생성 완료:", OUT)
print("크기:", os.path.getsize(OUT), "bytes")
