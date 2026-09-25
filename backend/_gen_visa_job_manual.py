#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Camnemi 매뉴얼 PDF: 외국인 유학생 「한국 취업 + 비자 플랜」
Navy/gold branding, 한국어 중심. Data: hikorea manual + job_manual_kr.json + visa KB."""
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD_PATH))
    addMapping("Malgun", 0, 0, "Malgun"); addMapping("Malgun", 1, 0, "Malgun-Bold")
    FONT, FBOLD = "Malgun", "Malgun-Bold"
else:
    FONT, FBOLD = "Helvetica", "Helvetica-Bold"

NAVY   = colors.HexColor("#0B2545")
GOLD   = colors.HexColor("#C9A227")
LGRAY  = colors.HexColor("#EEF1F5")
WHITE  = colors.white
DARK   = colors.HexColor("#1a1a1a")

OUT = r"C:\Users\wisew\camnemi-crm\backend\취업_비자_매뉴얼_유학생.pdf"

B = r"C:\Users\wisew\camnemi-crm\backend"
job = json.load(open(B + r"\job_manual_kr.json", encoding="utf-8"))
# hikorea D2/D4/D10/E7
hk = {}
for fn in ["체류민원_D2D4D10E7_pro.json", "사증_체류_통합분석_pro.json"]:
    try:
        d = json.load(open(B + r"\hikorea_manuals\\" + fn, encoding="utf-8"))
        hk[fn.split("_")[0]] = d
    except Exception as e:
        hk[fn.split("_")[0]] = {"err": str(e)}

tp = job["time_parttime"]

def st(t, **kw):
    kw.setdefault("fontName", FONT); kw.setdefault("fontSize", 9.5)
    kw.setdefault("leading", 14); kw.setdefault("textColor", DARK)
    return ParagraphStyle(t, **kw)

def stb(t, **kw):
    kw.setdefault("fontName", FBOLD); kw.setdefault("fontSize", 9.5)
    kw.setdefault("leading", 14); kw.setdefault("textColor", DARK)
    return ParagraphStyle(t, **kw)

title  = ParagraphStyle("title", fontName=FBOLD, fontSize=20, leading=26, textColor=WHITE)
sub    = ParagraphStyle("sub", fontName=FONT, fontSize=11, leading=16, textColor=GOLD)
h1     = ParagraphStyle("h1", fontName=FBOLD, fontSize=14, leading=18, textColor=NAVY, spaceBefore=6, spaceAfter=6, keepWithNext=True)
h2     = ParagraphStyle("h2", fontName=FBOLD, fontSize=11, leading=15, textColor=NAVY, spaceBefore=4, spaceAfter=3, keepWithNext=True)
body   = st("body")
bullet = st("bullet", leftIndent=12, bulletIndent=2, spaceAfter=2)
small  = st("small", fontSize=8, leading=11, textColor=colors.HexColor("#555"))

def sec_header(text):
    t = Table([[Paragraph(text, ParagraphStyle("sh", fontName=FBOLD, fontSize=13, leading=17, textColor=WHITE, keepWithNext=True))]],
              colWidths=[170*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY),
                           ("LEFTPADDING", (0,0), (-1,-1), 10),
                           ("TOPPADDING", (0,0), (-1,-1), 6),
                           ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return t

def data_table(header, rows, widths=None, hdr_bg=NAVY):
    data = [[Paragraph(c, ParagraphStyle("h", fontName=FBOLD, fontSize=8.5, leading=11, textColor=WHITE)) for c in header]]
    for r in rows:
        data.append([Paragraph(str(c), ParagraphStyle("c", fontName=FONT, fontSize=8, leading=10.5)) for c in r])
    w = widths or [170*mm/len(header)]*len(header)
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), hdr_bg),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#B0B8C4")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGRAY]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t

story = []

# ---------- Cover ----------
cov = Table([[Paragraph("CAMNEMI", ParagraphStyle("logo", fontName=FBOLD, fontSize=12, textColor=GOLD))],
             [Paragraph("한국 취업 · 유학생 비자 플랜", title)],
             [Paragraph("Working in Korea & Visa Plan for International Students", sub)],
             [Spacer(1, 4)],
             [Paragraph("외국인 유학생(D-2/D-4) 시간제취업 · 졸업 후 취업(D-10/E-7) · 장기체류(K-STAR/F-2/F-5)",
                        ParagraphStyle("c", fontName=FONT, fontSize=9, leading=13, textColor=WHITE))],
             [Spacer(1, 10)],
             [Paragraph("2026.9 · 법무부 출입국·외국인정책본부 자료 기준<br/>Offline consulting only — Camnemi의 기밀 자산",
                        ParagraphStyle("foot", fontName=FONT, fontSize=7.5, leading=10, textColor=GOLD))]], colWidths=[170*mm])
cov.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY),
                         ("LEFTPADDING",(0,0),(-1,-1),20),("RIGHTPADDING",(0,0),(-1,-1),20),
                         ("TOPPADDING",(0,0),(-1,-1),18),("BOTTOMPADDING",(0,0),(-1,-1),18)]))
story.append(cov)
story.append(PageBreak())

# ---------- 1. Visa path overview ----------
story.append(sec_header("1. 유학생 비자 로드맵 (Visa Roadmap)"))
story.append(Spacer(1,4))
story.append(Paragraph("외국인 유학생의 대표 경로: <b>D-4 어학연수 → D-2 학위 → 졸업 후 D-10 구직 / E-7 취업 → 장기체류(F-2·F-5·K-STAR)</b>", body))
story.append(Spacer(1,3))
story.append(data_table(
    ["단계", "비자", "내용", "핵심 조건"],
    [
        ["1", "D-4 일반연수", "어학연수(한국어 D-4-1 / 외국어 D-4-7)", "고졸 이상, 대학 부설 어학원"],
        ["2", "D-2 유학", "학위과정(전문학사1·학사2·석사3·박사4·교환6·일학습7·방문8)", "TOPIK 2+ / IELTS·재정증명"],
        ["3", "D-10 구직", "졸업 후 구직 (최대 2년)", "학위 취득, 구직활동"],
        ["4", "E-7 특정활동", "전문 취업 (전공 분야)", "졸업+취업확정 또는 D-10→E-7"],
        ["5", "F-2 거주", "점수제 거주", "소득·한국어·연령 점수"],
        ["6", "F-5 영주권", "영구거주", "장기체류 요건"],
        ["★", "K-STAR F-2-7S", "이공계 대학원 → 3년 후 영주권, 취업 무관", "지정 32개 대학 석·박사"],
    ],
    widths=[12*mm, 28*mm, 80*mm, 50*mm]))
story.append(Spacer(1,6))
story.append(Paragraph("D-4→D-2 변경: 해외 재외공관에서 사증 발급 → 국내 체류자격 변경허가. 이전 어학연수 성적·출석증명서 요구.", small))

# ---------- 2. Part-time work ----------
story.append(Spacer(1,6))
story.append(sec_header("2. 시간제취업 (Part-time Work, D-2/D-4)"))
story.append(Spacer(1,3))
story.append(Paragraph("<b>기본원칙</b>", h2))
story.append(Paragraph("통상 학생이 하는 단순노무 등 시간제 활동에 한정. 개인과외는 엄격 제한. 한국어능력 갖추고 대학 담당자 확인 필요.", body))
story.append(Spacer(1,3))
story.append(Paragraph("<b>허용시간 (평일)</b>", h2))
story.append(data_table(
    ["과정", "한국어 요건", "평일(한국어 충족)", "휴일·방학", "인증대학"],
    [[r["process"], (r["korean_req"] or "-")[:28],
      "25h" if "석·박" not in r["process"] else "30h",
      "무제한", r["certified"]]
     for r in tp["allowed_hours"]],
    widths=[30*mm, 48*mm, 34*mm, 26*mm, 22*mm]))
story.append(Spacer(1,4))
story.append(Paragraph("<b>언제부터 허용?</b>", h2))
story.append(Paragraph("D-2-1~D-2-4, D-2-6, D-2-7: 바로 가능 (D-2-8 방문학생은 6개월 경과 후)", body, bulletText="•"))
story.append(Paragraph("D-4-1/D-4-7: 변경일(사증소지자 입국일)로부터 6개월 경과 후", body, bulletText="•"))
story.append(Paragraph("<b>기간·장소:</b> D-2 = 최장 1년·동시 2곳 / D-4 = 최장 6개월·1곳", body, bulletText="•"))
story.append(Spacer(1,4))
story.append(Paragraph("<b>제한직종</b>", h2))
for x in tp["restricted_fields"][:5]:
    story.append(Paragraph("• " + x[:120], bullet))
story.append(Spacer(1,3))
story.append(Paragraph("<b>필요서류</b>", h2))
story.append(Paragraph("신청서·여권·외국인등록증, 성적/출석증명, 한국어(영어)능력 증빙, 시간제취업 확인서, 사업자등록증·근로계약서 사본, 표준근로계약서(시급·근무내용 명시)", body))
story.append(Spacer(1,3))
story.append(Paragraph("<b>⚠️ 위반 페널티</b>", h2))
story.append(Paragraph("허가 없이 취업: 1차 = 통고처분·체류허가(건설업 불법취업은 예외 없이 출국), 2차 = 강제퇴거. 허가조건 위반: 1차 경고 / 2차 유학 중 시간제 취업 불허 / 3차 유학자격 취소.", body))

# ---------- 3. Employment paths ----------
story.append(Spacer(1,10))
story.append(sec_header("3. 졸업 후 취업경로 (Employment Paths)"))
story.append(Spacer(1,4))
paths = job["employment_paths"]
seen=set(); rows=[]
for x in paths:
    k=(x["from"],x["to"])
    if k in seen: continue
    seen.add(k)
    rows.append([x["from"], x["to"], x["condition"][:80]])
story.append(data_table(["출발 비자", "도착 비자", "조건"], rows,
                        widths=[38*mm, 42*mm, 90*mm]))
story.append(Spacer(1,6))
story.append(Paragraph("<b>E-7 허용직종</b> (94개)", h2))
story.append(Paragraph(job["e7_fields"], body))
story.append(Spacer(1,4))
story.append(Paragraph("<b>E-7-4 숙련기능인력</b>", h2))
story.append(data_table(["대상", "요건"],
    [[job["e7_4_skilled"]["target"], job["e7_4_skilled"]["requirement"]]],
    widths=[70*mm, 100*mm]))

# ---------- 4. Long-term stays ----------
story.append(Spacer(1,10))
story.append(sec_header("4. 장기체류 · 영주권 (Long-term Stay / PR)"))
story.append(Spacer(1,4))
story.append(Paragraph("<b>K-STAR (F-2-7S)</b> — 이공계 유학생 영주권 최단경로", h2))
story.append(data_table(["항목", "내용"],
    [["대상", "이공계 석·박사 (지정 32개 대학, 2026 확대)"],
     ["혜택", "무취업 5년 체류, 3년 후 F-5 영주권, 특별귀화"],
     ["방식", "지도교수 추천 → 총장 명의 추천서 → 체류자격 변경"],
     ["비교", "일반 F-2(점수제)보다 빠름, 취업 고정 없음"]], widths=[40*mm, 130*mm]))
story.append(Spacer(1,5))
story.append(Paragraph("<b>F-2 거주(점수제) / F-5 영주권</b>", h2))
story.append(Paragraph("F-2-7: 소득·한국어·연령·학력 점수 충족 (한국어 TOPIK·KIIP 가점)", body, bulletText="•"))
story.append(Paragraph("F-5: 장기체류(보통 5년+)·소득·한국어 요건", body, bulletText="•"))
story.append(Spacer(1,4))
story.append(Paragraph("<b>KIIP (사회통합프로그램)</b> — TOPIK 대체 + 가점", h2))
story.append(Paragraph("3단계(61점)≈TOPIK 3, 4단계(81점)≈TOPIK 4, 5단계≈TOPIK 5", body, bulletText="•"))
story.append(Paragraph("영주권·귀화 신청 시 한국어 요건 충족 + 가점", body, bulletText="•"))

# ---------- 5. Key notes ----------
story.append(Spacer(1,10))
story.append(sec_header("5. 핵심 유의사항 (Key Notes)"))
story.append(Spacer(1,4))
for x in job["key_notes"]:
    story.append(Paragraph("• " + x, bullet))
story.append(Spacer(1,6))
story.append(sec_header("6. 재정증명 (Financial Proof, 2026)"))
story.append(Spacer(1,4))
story.append(data_table(["구분", "수도권", "지방"],
    [["D-2 학위", "2,000만원 (~$14,300)", "1,600만원 (~$11,500)"],
     ["D-4 어학", "1,000만원 (~$7,200)", "800만원 (~$5,800)"],
     ["유의", "학교별·지역별 상이, 28일 이상 예치 요구 가능", ""]],
    widths=[40*mm, 65*mm, 65*mm]))
story.append(Spacer(1,6))
story.append(Paragraph("⚠️ 2026 비자정밀심사 대상 대학(20교)은 추천 제외. 캄보디아는 '기타국가'로 일부 D-4 4학기 요구·마감 불리할 수 있음.", small))
story.append(Spacer(1,4))
story.append(Paragraph("본 매뉴얼은 Camnemi 오프라인 상담 전용입니다. (출처: 법무부 하이코리아 매뉴얼 2026.9, 검증된 KB)", small))

doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm, topMargin=16*mm, bottomMargin=16*mm,
    title="Camnemi 취업·비자 매뉴얼", author="Camnemi")
doc.build(story)
print("생성:", OUT, os.path.getsize(OUT), "bytes")
