# -*- coding: utf-8 -*-
"""Build Konyang Univ D-4 (Dec/4Q 2026) consulting PDF — navy/gold Camnemi brand."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

NAVY = colors.HexColor("#0B2545")
GOLD = colors.HexColor("#C9A227")
LIGHT = colors.HexColor("#F4F1EA")

pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont("Malgun-Bold", r"C:\Windows\Fonts\malgunbd.ttf"))
pdfmetrics.registerFontFamily("Malgun", normal="Malgun", bold="Malgun-Bold", italic="Malgun", boldItalic="Malgun-Bold")

OUT = r"C:\Users\USER\camnemi-crm\backend\건양대_D4_12월입학_컨설팅_2026.pdf"

def st(name, **kw):
    base = dict(fontName="Malgun", fontSize=10, leading=15, textColor=colors.HexColor("#1a1a1a"), spaceAfter=4)
    base.update(kw); return ParagraphStyle(name, **base)

S_title = st("t", fontName="Malgun-Bold", fontSize=19, leading=24, textColor=colors.white, alignment=TA_CENTER)
S_sub   = st("s", fontName="Malgun", fontSize=10.5, leading=14, textColor=GOLD, alignment=TA_CENTER)
S_h1    = st("h1", fontName="Malgun-Bold", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=5)
S_h2    = st("h2", fontName="Malgun-Bold", fontSize=11, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=3)
S_body  = st("b", fontSize=10)
S_bul   = st("bul", fontSize=9.8, leading=14.5, leftIndent=10, bulletIndent=2)
S_note  = st("note", fontSize=9, leading=13, textColor=colors.HexColor("#666666"))
S_warn  = st("warn", fontName="Malgun-Bold", fontSize=9.5, leading=13, textColor=colors.HexColor("#B00020"))

def header_footer(canvas, doc):
    canvas.saveState()
    w,h = A4
    # header band
    canvas.setFillColor(NAVY); canvas.rect(0, h-30*mm, w, 30*mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Malgun-Bold", 13)
    canvas.drawString(15*mm, h-15*mm, "Camnemi 유학컨설팅")
    canvas.setFillColor(GOLD); canvas.setFont("Malgun", 9)
    canvas.drawString(15*mm, h-22*mm, "캄보디아 학생 · 한국 유학 전문")
    # footer
    canvas.setFillColor(NAVY); canvas.rect(0, 0, w, 12*mm, stroke=0, fill=1)
    canvas.setFillColor(colors.white); canvas.setFont("Malgun", 8)
    canvas.drawCentredString(w/2, 5*mm, "Camnemi · 본 자료는 2026.09.08 기준 모집요강 기반 — 최신 정보는 국제교육원 확인")
    canvas.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm, topMargin=34*mm, bottomMargin=16*mm)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=header_footer)])

story = []
story.append(Paragraph("건양대학교 한국어연수(D-4)", S_title))
story.append(Spacer(1,2))
story.append(Paragraph("2026학년도 4쿼터(12월 입학) 입학안내 — 국제교육원", S_sub))
story.append(Spacer(1,6))

# ===== 개요 =====
story.append(Paragraph("1. 학교 개요", S_h1))
story.append(Paragraph("건양대학교(Konyang University) — 충남 논산시 대학로 121 (국제교육원 건양회관 5층)", S_body))
story.append(Paragraph("캠퍼스: 논산(본교) · 대전(제2캠퍼스, 의료·보건 특화)  |  과정: 한국어연수 정규과정 (D-4)", S_body))
story.append(Paragraph("문의: 041-730-5132 / 5136  ·  kyuintl@konyang.ac.kr  ·  interedu.konyang.ac.kr", S_body))

# ===== 일정 =====
story.append(Paragraph("2. 2026 4쿼터(겨울) 전형 일정 ★ 현재 접수 진행 중", S_h1))
story.append(Paragraph("지원자가 많으면 조기 마감될 수 있어 조기 준비 필요", S_warn))
schedule = [
    ["구분", "일정", "비고"],
    ["원서접수", "2026.09.01(화) ~ 10.10(토)", "유웨이 kyuklc.uway.com 온라인"],
    ["서류(원본) 제출", "2026.10.21(수)", "우편/방문 — 이후 도착 시 다음 쿼터"],
    ["서류합격자 발표", "매주 개별 발표", "이메일 통보"],
    ["면접", "매주 진행", "현지 면접(온라인 가능)"],
    ["인보이스 발급", "면접 후 확인", "유웨이 로그인"],
    ["등록금 납부", "2026.10.21(수)까지", "FLYWIRE 또는 가상계좌"],
    ["표준입학허가서", "2026.10.30(금)까지", "등록·원본 확인 후 발급"],
    ["지정입국일", "1차 11.27(금) / 2차 12.11(금)", "공항 인솔 지원(지정일만)"],
    ["학기 시작", "2026.11.30(월)", "동기유발 12.13~14 필수"],
]
t = Table(schedule, colWidths=[34*mm, 52*mm, 88*mm])
t.setStyle(TableStyle([
    ("FONTNAME",(0,0),(-1,-1),"Malgun"),
    ("FONTNAME",(0,0),(-1,0),"Malgun-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),8.6),
    ("BACKGROUND",(0,0),(-1,0),NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
    ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#bbbbbb")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEADING",(0,0),(-1,-1),11),
]))
story.append(t)

# ===== 지원자격 =====
story.append(Paragraph("3. 지원자격", S_h1))
story.append(Paragraph("• 부모가 모두 외국인인 외국인 (순수외국인)", S_bul, bulletText="•"))
story.append(Paragraph("• 모국에서 정규교육 12년(고교) 이수", S_bul, bulletText="•"))
story.append(Paragraph("• 학력 조건 (아래 중 하나):", S_bul, bulletText="•"))
story.append(Paragraph("   - 고등학교 졸업 후 2년 이내 (성적 100점 만점 70점 이상)", S_bul))
story.append(Paragraph("   - 대학 졸업 후 2년 이내 (GPA 4.5만점 3.0 이상)", S_bul))
story.append(Paragraph("• 재정: 본인 또는 보증인이 학비·체류비 지불 능력", S_bul, bulletText="•"))
story.append(Paragraph("• 비자: D-4 발급에 결격사유 없을 것 (결석 5회 이하 기록 유지)", S_bul, bulletText="•"))

# ===== 비용 =====
story.append(Paragraph("4. 등록금 및 비용", S_h1))
cost = [
    ["항목", "금액(KRW)", "비고"],
    ["수업료", "₩4,400,000", "1년 (4쿼터)"],
    ["입학금", "₩100,000", "최초 입학 시"],
    ["전형료", "₩100,000", ""],
    ["기숙사비", "₩910,000", "15주/학위 1학기"],
    ["보험료", "₩150,000", "6개월 (차액 환불)"],
    ["합계", "약 ₩5,660,000", "교재비·문화체험비 별도"],
]
t2 = Table(cost, colWidths=[34*mm, 52*mm, 88*mm])
t2.setStyle(TableStyle([
    ("FONTNAME",(0,0),(-1,-1),"Malgun"),
    ("FONTNAME",(0,0),(-1,0),"Malgun-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),8.8),
    ("BACKGROUND",(0,0),(-1,0),NAVY),
    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,LIGHT]),
    ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#bbbbbb")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("BACKGROUND",(0,5),(-1,5),colors.HexColor("#E8E0C8")),
    ("FONTNAME",(0,5),(-1,5),"Malgun-Bold"),
]))
story.append(t2)

# ===== 장학 =====
story.append(Paragraph("5. 장학금", S_h1))
story.append(Paragraph("• 정착지원금: 500,000원 / 1년", S_bul, bulletText="•"))
story.append(Paragraph("• TOPIK 2급 보유자: 2개 쿼터 등록금 30% 할인 (660,000원)", S_bul, bulletText="•"))
story.append(Paragraph("   → 캄보디아 학생이 TOPIK 2급 소지 시 유리", S_bul))

# ===== 서류 =====
story.append(Paragraph("6. 제출서류", S_h1))
story.append(Paragraph("• 입학신청서(자기소개서·학습계획서 포함, 본교 양식)", S_bul, bulletText="•"))
story.append(Paragraph("• 여권 사본 + 부모·본인 신분증", S_bul, bulletText="•"))
story.append(Paragraph("• 가족관계증명 (캄보디아: 관련 입증서류)", S_bul, bulletText="•"))
story.append(Paragraph("• 최종학력 졸업증명 + 성적증명 (아포스티유 또는 영사확인)", S_bul, bulletText="•"))
story.append(Paragraph("• 학력인증서 (아포스티유 체결국)", S_bul, bulletText="•"))
story.append(Paragraph("• 부모 재직·수입증명", S_bul, bulletText="•"))
story.append(Paragraph("• 은행잔고증명 USD 5,000 이상 (6개월 동결, 비자신청 30일 내)", S_bul, bulletText="•"))
story.append(Paragraph("• 사진 5매 (4x3cm, 흰배경)  +  엑셀 신청정보", S_bul, bulletText="•"))

# ===== 주의 =====
story.append(Paragraph("7. 핵심 주의사항", S_h1))
story.append(Paragraph("1) D-4 비자로 입국, 6개월마다 체류 연장 (최장 2년) — D-4 외 비자 변경 시 환불 불가", S_bul, bulletText="①"))
story.append(Paragraph("2) 입국일(11.27/12.11) 오전 인천공항 도착 항공권 예매 필수 (지정일만 공항 인솔)", S_bul, bulletText="②"))
story.append(Paragraph("3) 입국 시 결핵확인서·홍역접종확인서 지참 필수", S_bul, bulletText="③"))
story.append(Paragraph("4) 캐리어 1~2개 제한", S_bul, bulletText="④"))
story.append(Paragraph("5) 비자발급이 2026.12.10 이후면 이번 쿼터 입학 불가 → 다음 쿼터로 이월", S_bul, bulletText="⑤"))
story.append(Paragraph("6) 서류 마감(10.21) 이후 도착 원본은 다음 쿼터 지원에 사용", S_bul, bulletText="⑥"))
story.append(Spacer(1,4))
story.append(Paragraph("※ 어학연수 후 학위 진학 시 3+1, 2+2 제도 활용 가능 — 캄보디아 학생 로드맵 상담 권장", S_note))

doc.build(story)
print(f"PDF 생성: {OUT}")
print(f"크기: {os.path.getsize(OUT)} bytes")
