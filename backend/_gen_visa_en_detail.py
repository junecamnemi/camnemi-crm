#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Camnemi: (A) 비자별 상세 규정 매뉴얼 (KO) + (B) Working & Visa Plan (EN).
Data: hikorea 체류민원 D2/D4/D10/E7 pro 분석."""
import os, json
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
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", FONT_BOLD_PATH))
    addMapping("Malgun",0,0,"Malgun"); addMapping("Malgun",1,0,"Malgun-Bold")
    FONT, FBOLD = "Malgun", "Malgun-Bold"
else:
    FONT, FBOLD = "Helvetica", "Helvetica-Bold"

NAVY=colors.HexColor("#0B2545"); GOLD=colors.HexColor("#C9A227")
LGRAY=colors.HexColor("#EEF1F5"); WHITE=colors.white; DARK=colors.HexColor("#1a1a1a")

B=r"C:\Users\USER\camnemi-crm\backend"
hk=json.load(open(B+r"\hikorea_manuals\체류민원_D2D4D10E7_pro.json",encoding="utf-8"))
job=json.load(open(B+r"\job_manual_kr.json",encoding="utf-8"))
by={s["status"]:s for s in hk["by_status"]}

def P(t, size=9.5, bold=False, color=DARK, leading=14, **kw):
    return ParagraphStyle("x", fontName=FBOLD if bold else FONT, fontSize=size, leading=leading,
                          textColor=color, **kw)

def sec_header(text, lang="ko"):
    t=Table([[Paragraph(text, ParagraphStyle("h",fontName=FBOLD,fontSize=13,leading=17,textColor=WHITE))]],
             colWidths=[170*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("LEFTPADDING",(0,0),(-1,-1),10),
                           ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

def dtable(header, rows, widths=None):
    data=[[Paragraph(c, P("",8.5,bold=True,color=WHITE)) for c in header]]
    for r in rows:
        data.append([Paragraph(str(c), P("",8,leading=10.5)) for c in r])
    w=widths or [170*mm/len(header)]*len(header)
    t=Table(data,colWidths=w,repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#B0B8C4")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LGRAY]),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t

def cover(story, ko_title, en_sub, out_note, footer):
    cov=Table([[Paragraph("CAMNEMI", P("logo",12,bold=True,color=GOLD))],
               [Paragraph(ko_title, P("t",20,bold=True,color=WHITE,leading=26))],
               [Paragraph(en_sub, P("s",11,color=GOLD,leading=16))],
               [Spacer(1,8)],
               [Paragraph(out_note, P("o",8,color=WHITE,leading=12))],
               [Spacer(1,12)],
               [Paragraph(footer, P("f",7.5,color=GOLD,leading=10))]], colWidths=[170*mm])
    cov.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("LEFTPADDING",(0,0),(-1,-1),20),
                             ("RIGHTPADDING",(0,0),(-1,-1),20),("TOPPADDING",(0,0),(-1,-1),18),
                             ("BOTTOMPADDING",(0,0),(-1,-1),18)]))
    story.append(cov); story.append(PageBreak())

def build(path, story):
    d=SimpleDocTemplate(path,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,
        topMargin=16*mm,bottomMargin=16*mm,title="Camnemi Manual",author="Camnemi")
    d.build(story)
    return os.path.getsize(path)

# ============================================================
# A) 비자별 상세 규정 매뉴얼 (KO)
# ============================================================
s=[]; cover(s,"비자별 상세 규정 매뉴얼","Visa-Specific Regulations for International Students",
            "D-2 유학 · D-4 어학연수 · D-10 구직 · E-7 취업 — 체류기간·활동범위·필요서류·변경특례",
            "2026.9 · 법무부 하이코리아 매뉴얼 기준 / Camnemi offline consulting 전용")
for st in hk["by_status"]:
    stt=st["status"]
    s.append(sec_header(stt)); s.append(Spacer(1,4))
    def kv(label, key):
        if st.get(key): s.append(Paragraph(f"<b>{label}</b>: {st[key]}", P("",9)))
    kv("신청대상","apply_target")
    kv("활동범위","activity_scope")
    kv("체류기간","period")
    s.append(Spacer(1,3))
    docs=st.get("required_docs",[])
    if docs:
        s.append(Paragraph("<b>공통 필요서류</b>", P("",9,bold=True)))
        for x in docs: s.append(Paragraph("• "+str(x), P("",8.5,leading=12)))
    extra=st.get("additional_docs_by_case",[])
    if extra:
        s.append(Spacer(1,2)); s.append(Paragraph("<b>경우별 추가서류</b>", P("",9,bold=True)))
        for x in extra: s.append(Paragraph("• "+str(x), P("",8.5,leading=12)))
    if st.get("work_rights"):
        s.append(Spacer(1,2)); s.append(Paragraph("<b>취업·근로 권리</b>", P("",9,bold=True)))
        s.append(Paragraph(st["work_rights"], P("",8.5,leading=12)))
    if st.get("notes"):
        s.append(Spacer(1,2)); s.append(Paragraph("<b>참고</b>", P("",9,bold=True)))
        s.append(Paragraph(st["notes"], P("",8,leading=11)))
    s.append(Spacer(1,8))

# append part-time hours summary
s.append(sec_header("부록: 시간제취업 허용시간 (2023.7 시행 기준)"))
s.append(Spacer(1,4))
s.append(dtable(["과정","한국어 요건","평일(충족)","휴일·방학","인증대학"],
    [[r["process"],(r["korean_req"] or "-")[:30],"25h" if "석·박" not in r["process"] else "30h","무제한",r["certified"]]
     for r in job["time_parttime"]["allowed_hours"]],
    widths=[30*mm,50*mm,32*mm,26*mm,24*mm]))
sizeA=build(B+r"\비자별_상세규정_매뉴얼.pdf",s)
print("A(비자별상세KO):", sizeA, "bytes")

# ============================================================
# B) Working & Visa Plan (EN)
# ============================================================
s=[]; cover(s,"Working in Korea & Visa Plan","For International Students (English)",
            "Part-time work (D-2/D-4) · Post-graduation employment (D-10/E-7) · Long-term stay (K-STAR/F-2/F-5)",
            "2026.9 · Based on MOJ HiKorea manual / Camnemi offline consulting only")
s.append(sec_header("1. Visa Roadmap"))
s.append(Paragraph("Typical path: <b>D-4 Language → D-2 Degree → D-10 Job-seeking / E-7 Work → F-2·F-5·K-STAR (PR)</b>",
                   P("",9.5,bold=False)))
s.append(Spacer(1,4))
s.append(dtable(["Step","Visa","Purpose","Key condition"],
    [["1","D-4 General Training","Korean/foreign language (D-4-1 / D-4-7)","HS grad+, university-affiliated language center"],
     ["2","D-2 Student","Degree (jr-college/BA/MA/PhD/research/exchange/work-study/visiting)","TOPIK 2+ / IELTS · financial proof"],
     ["3","D-10 Job-seeking","After graduation (max 2 yrs)","Degree, active job search"],
     ["4","E-7 Specific Activity","Professional employment","Graduation + job offer, or D-10→E-7"],
     ["5","F-2 Resident","Points-based","Income·Korean·age points"],
     ["6","F-5 PR","Permanent residence","Long-stay requirements"],
     ["★","K-STAR F-2-7S","STEM grad → PR in 3 yrs, job-free","32 designated univs, master's/PhD"]],
    widths=[12*mm,34*mm,84*mm,40*mm]))
s.append(Spacer(1,6))
s.append(Paragraph("D-4→D-2: apply in Korea for status change after entering; prior language-study attendance/grade cert required.",
                   P("",8,color=colors.HexColor("#555"))))

s.append(Spacer(1,6)); s.append(sec_header("2. Part-Time Work (D-2/D-4)"))
s.append(Paragraph("Limited to ordinary student part-time activity (simple labor). Private tutoring strictly restricted. Need Korean ability + university advisor confirmation.", P("",9)))
s.append(Spacer(1,3))
s.append(Paragraph("Allowed hours (weekday)", P("",9,bold=True)))
s.append(dtable(["Level","Korean req","Weekday (met)","Holidays/vacation","Accredited univ"],
    [[{"전문학사":"Junior college","학사 1~2학년":"Bachelor's 1-2 yr","학사 3~4학년":"Bachelor's 3-4 yr","석·박사":"Master's/PhD"}.get(r["process"],r["process"]),
      {"전문학사":"TOPIK 3 / KIIP stage 3 (61pts) / Sejong mid-1","학사 1~2학년":"-","학사 3~4학년":"TOPIK 4 / KIIP stage 4 (81pts) / Sejong mid-2","석·박사":"-"}.get(r["process"],"-"),
      "25h" if "석·박" not in r["process"] else "30h","Unlimited",
      r["certified"].replace("시간","h") if r.get("certified") else ""]
     for r in job["time_parttime"]["allowed_hours"]],
    widths=[30*mm,52*mm,30*mm,24*mm,24*mm]))
s.append(Spacer(1,4))
s.append(Paragraph("<b>When allowed?</b> D-2-1~4/6/7: immediately (D-2-8 visiting: after 6 months). D-4-1/7: after 6 months.", P("",8.5)))
s.append(Paragraph("<b>Duration/places:</b> D-2 = max 1 yr, 2 places / D-4 = max 6 months, 1 place.", P("",8.5)))
s.append(Spacer(1,3))
s.append(Paragraph("<b>⚠️ Penalty for unpermitted work:</b> 1st = warning & stay granted (construction-sector illegal work = departure, no exception), 2nd = forced deportation. Condition violation: 1st warning / 2nd no part-time during study / 3rd student status revoked.", P("",8.5)))

s.append(Spacer(1,10)); s.append(sec_header("3. Employment After Graduation"))
s.append(dtable(["From","To","Condition"],
    [["D-2","E-7 (professional)","Graduate + job offer confirmed → change immediately"],
     ["D-2","D-10 (job-seeking)","Not yet employed after grad (max 2 yrs)"],
     ["D-2","F-2-7 (points)","Meet points criteria"],
     ["D-2","F-5 (PR)","Long-stay criteria"],
     ["D-4-6 (20mo training)","E-7","Overseas jr-college+, domestic training completed, national cert + KIIP stage 4"],
     ["E-9","E-7-4 (skilled)","5 yrs legal work (4 yrs + KIIP stage 3 counts)"],
     ["E-9","F-2 / F-5","Long-stay criteria"]],
    widths=[40*mm,48*mm,82*mm]))
s.append(Spacer(1,6))
s.append(Paragraph("<b>E-7 eligible occupations:</b> 94 total — professional (E-7-1) 67, semi-professional (E-7-2) 10, general skilled (E-7-3).", P("",8.5)))
s.append(Paragraph("<b>E-7-4 skilled worker:</b> root/manufacturing/construction skilled (S700/S740), agriculture (S610). 2026 wage threshold: KRW 26M+/yr.", P("",8.5)))

s.append(Spacer(1,10)); s.append(sec_header("4. Long-Term Stay & PR"))
s.append(dtable(["Visa","What","Benefit"],
    [["K-STAR (F-2-7S)","STEM master's/PhD from 32 designated univs","Stay 5 yrs job-free; F-5 PR in 3 yrs; special naturalization"],
     ["F-2 Resident","Points system","Income·Korean·age points"],
     ["F-5 PR","Long-term stay","5+ yrs, income & Korean"],
     ["KIIP","Social Integration Program","Replaces TOPIK + points for PR/naturalization"]],
    widths=[40*mm,70*mm,60*mm]))
s.append(Spacer(1,6))
s.append(sec_header("5. Key Notes"))
EN_NOTES = [
    "Part-time-work special rule: incidental gratuities, prize money, or payment for activities that do not infringe the essence of student status are exempt from the permit requirement.",
    "Paid research (D-2): research/internship tied to study within your own university = exempt from part-time-work permit. Research unrelated to study = permit needed. Off-campus study-linked research/internship = permit needed; off-campus unrelated research = status-outside-activity permit (E-3).",
    "Field-work semester: standard field-work semester programs and mandatory practicum curricula are exempt from the part-time-work permit; voluntary field work needs the permit.",
    "D-2 stay-extension special caps: jr-college max 3 yrs (3-yr program: 4), bachelor's max 6 yrs (5-yr: 7), master's max 5 yrs (3-yr: 6), PhD max 8 yrs (2-yr: 7) from enrollment.",
    "Re-entry permit exemption: a registered international student re-entering within 1 year of departure is exempt; re-entry between 1-2 years may apply for a multiple re-entry permit.",
    "E-7 special for excellent-private-institution trainees: completing D-4-6 (20+ months), obtaining a national certificate, and completing KIIP stage 4+ allows E-7 status change in the trained field (except E-7-4).",
]
for x in EN_NOTES:
    s.append(Paragraph("• "+x, P("",8.5,leading=12)))
s.append(Spacer(1,6))
s.append(sec_header("6. Financial Proof (2026)"))
s.append(dtable(["Type","Capital region","Non-capital"],
    [["D-2 (degree)","KRW 20M (~$14,300)","KRW 16M (~$11,500)"],
     ["D-4 (language)","KRW 10M (~$7,200)","KRW 8M (~$5,800)"],
     ["Note","School/region vary; some require ≥28-day deposit",""]],
    widths=[40*mm,65*mm,65*mm]))
s.append(Spacer(1,6))
s.append(Paragraph("⚠️ 2026 visa-intensive-screening universities (20) are excluded from recommendations. Cambodia = 'other country' → some D-4 require 4 semesters; deadlines may be less favorable.", P("",8,color=colors.HexColor("#555"))))
sizeB=build(B+r"\Working_Visa_Plan_Students_EN.pdf",s)
print("B(영문매뉴얼):", sizeB, "bytes")
