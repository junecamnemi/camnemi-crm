#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Camnemi — International Student Job Manual (ENGLISH ONLY).
Data: job_manual_kr.json (HiKorea 시간제취업 + 취업경로)."""
import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FONT_PATH="C:/Windows/Fonts/malgun.ttf"; FONT_BOLD_PATH="C:/Windows/Fonts/malgunbd.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Malgun",FONT_PATH)); pdfmetrics.registerFont(TTFont("Malgun-Bold",FONT_BOLD_PATH))
    addMapping("Malgun",0,0,"Malgun"); addMapping("Malgun",1,0,"Malgun-Bold")
    FONT,FBOLD="Malgun","Malgun-Bold"
else: FONT,FBOLD="Helvetica","Helvetica-Bold"

NAVY=colors.HexColor("#0B2545"); GOLD=colors.HexColor("#C9A227")
LGRAY=colors.HexColor("#EEF1F5"); WHITE=colors.white; DARK=colors.HexColor("#1a1a1a")

B=r"C:\Users\USER\camnemi-crm\backend"
job=json.load(open(B+r"\job_manual_kr.json",encoding="utf-8"))
tp=job["time_parttime"]

def P(t,size=9.5,bold=False,color=DARK,leading=14,**kw):
    return ParagraphStyle("x",fontName=FBOLD if bold else FONT,fontSize=size,leading=leading,textColor=color,**kw)

def sec(text):
    h=ParagraphStyle("h",fontName=FBOLD,fontSize=13,leading=17,textColor=WHITE,keepWithNext=True)
    t=Table([[Paragraph(text,h)]],colWidths=[170*mm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("LEFTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

def dtable(header,rows,widths=None):
    data=[[Paragraph(c,P("",8.5,bold=True,color=WHITE)) for c in header]]
    for r in rows:
        data.append([Paragraph(str(c),P("",8,leading=10.5)) for c in r])
    w=widths or [170*mm/len(header)]*len(header)
    t=Table(data,colWidths=w,repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#B0B8C4")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LGRAY]),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    return t

s=[]
cov=Table([[Paragraph("CAMNEMI",P("logo",10,bold=True,color=GOLD))],
           [Paragraph("International Student Job Manual",P("t",17,bold=True,color=WHITE,leading=21))],
           [Paragraph("Part-time Work & Employment Guide for Students in Korea",P("s",10,color=GOLD,leading=14))],
           [Spacer(1,5)],
           [Paragraph("For D-2 (student) & D-4 (language) visa holders — allowed hours, rules, penalties, and post-graduation job paths",P("o",7.5,color=WHITE,leading=11))],
           [Spacer(1,6)],
           [Paragraph("2026.9 · Based on MOJ HiKorea manual / Camnemi offline consulting only",P("f",7,color=GOLD,leading=9))]],
          colWidths=[170*mm])
cov.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),("LEFTPADDING",(0,0),(-1,-1),16),
    ("RIGHTPADDING",(0,0),(-1,-1),16),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
s.append(cov); s.append(Spacer(1,10))

# 0. D-2 sub-status definitions (at the front, same page as compact cover)
s.append(sec("Student Visa Sub-statuses (D-2)"))
s.append(Spacer(1,4))
s.append(dtable(["Code","Name","Description"],
    [["D-2-1","Junior College","2~3-year professional-degree program"],
     ["D-2-2","Bachelor's","4-year undergraduate program"],
     ["D-2-3","Master's","Graduate master's program"],
     ["D-2-4","Doctoral","Graduate doctoral program"],
     ["D-2-5","Research","Research course/student (1 yr at a time, no stay >2 yrs)"],
     ["D-2-6","Exchange","Exchange student"],
     ["D-2-7","Work-Study","Work-study linked program"],
     ["D-2-8","Visiting","Visiting student (part-time work only after 6 months)"]],
    widths=[22*mm,34*mm,114*mm]))
s.append(Spacer(1,6))
s.append(sec("Language / Language-Learning (D-4) Sub-statuses"))
s.append(Spacer(1,4))
s.append(dtable(["Code","Name","Description"],
    [["D-4-1","Korean Language","Korean-language training at a university-affiliated language center"],
     ["D-4-2","General Training","Education/training or research at institutions, companies, or organizations other than D-2-eligible educational/research institutions"],
     ["D-4-3","Under-High-School Student","International student below high-school level (elementary/middle/high school)"],
     ["D-4-5","Cuisine Trainee","Korean-cuisine training (Sura School internship only)"],
     ["D-4-6","Private Institution","Excellent private-institution training (20+ months)"],
     ["D-4-7","Foreign Language","Foreign-language training"]],
    widths=[22*mm,40*mm,108*mm]))
s.append(Spacer(1,10))

# PageBreak: page 1 = header + D-2/D-4 definitions only; part-time section starts fresh
s.append(PageBreak())

# 1. Basic principle
s.append(sec("1. Part-Time Work — Basic Rules"))
s.append(Spacer(1,4))
s.append(Paragraph("<b>General principle:</b> limited to ordinary part-time student activity (simple labor, etc.) per Immigration Act Enforcement Decree Annex 1-2. Private tutoring is strictly restricted due to place/target characteristics.", P("",9)))
s.append(Spacer(1,3))
s.append(Paragraph("<b>Who qualifies:</b> those with a certain level of Korean ability, focused on study, with confirmation from their university's international-student office.", P("",9)))
s.append(Paragraph("• D-2-1~D-2-4, D-2-6, D-2-7 (student statuses) — see start rules below", P("",8.5)))
s.append(Paragraph("• D-4-1/D-4-7 (language) and D-2-8 (visiting) — allowed only after 6 months from change date (entry date for visa holders)", P("",8.5)))
s.append(Paragraph("• Excluded: those granted exceptional stay due to unmet graduation requirements (except master's/PhD thesis students, capped at 30h/week, no unlimited holiday rule)", P("",8.5)))
s.append(Paragraph("• Restricted: average GPA below C (2.0) in the previous semester, or language students with overall attendance below 90%; or penalized for permit violation in the last 3 months", P("",8.5)))
s.append(Spacer(1,4))

# 2. Allowed hours table
s.append(Paragraph("Allowed hours (weekday basis)", P("",9.5,bold=True)))
s.append(dtable(
    ["Level","Korean req","Weekday","Holidays/vacation","Accredited univ"],
    [[{"전문학사":"Junior college","학사 1~2학년":"Bachelor's 1-2 yr","학사 3~4학년":"Bachelor's 3-4 yr","석·박사":"Master's/PhD"}.get(r["process"],r["process"]),
      {"전문학사":"TOPIK 3 / KIIP st3 (61pt) / Sejong mid-1","학사 1~2학년":"-","학사 3~4학년":"TOPIK 4 / KIIP st4 (81pt) / Sejong mid-2","석·박사":"-"}.get(r["process"],"-"),
      r["weekday"].replace("미충족","not met").replace("충족","met").replace("시간","h").strip(),
      "Unlimited",
      r["certified"].replace("시간","h")]
     for r in tp["allowed_hours"]],
    widths=[28*mm,52*mm,32*mm,30*mm,28*mm]))
s.append(Spacer(1,4))
s.append(Paragraph("<b>English-track note:</b> TOEFL 530 (CBT197/iBT71), IELTS 5.5, CEFR B2, TEPS 601 (NEW TEPS 327) certificate holders qualify; English-native countries exempt from cert submission.", P("",8.5)))
s.append(Spacer(1,3))

# 3. Start by status, duration/place
s.append(Paragraph("<b>When work can start</b>", P("",9.5,bold=True)))
s.append(dtable(["Status","When part-time allowed"],
    [["D-2-1 (Junior College)","Immediately"],
     ["D-2-2 (Bachelor's)","Immediately"],
     ["D-2-3 (Master's)","Immediately"],
     ["D-2-4 (Doctoral)","Immediately"],
     ["D-2-6 (Exchange)","Immediately"],
     ["D-2-7 (Work-Study)","Immediately"],
     ["D-2-5 (Research)","Not part-time eligible (research status)"],
     ["D-2-8 (Visiting)","6 months after change/entry date"],
     ["D-4-1 / D-4-7 (Language)","6 months after change/entry date"]],
    widths=[70*mm,100*mm]))
s.append(Spacer(1,4))
s.append(Paragraph("<b>Duration & places:</b> D-2 = max 1 year, up to 2 workplaces simultaneously. D-4 = max 6 months, 1 workplace.", P("",8.5)))
s.append(Spacer(1,4))

# 4. Restricted fields
s.append(Paragraph("Restricted work fields", P("",9.5,bold=True)))
# ---- EN translation maps for runtime-loaded lists ----
RESTR_EN = {
 "선량한 풍속이나 그 밖의 사회질서에 반하는 행위(출입국관리법 시행규칙 제27조의2 제2항)에 해당하는 활동":"Activities contrary to public decency or social order (Immigration Act Enforcement Rule art. 27-2(2)).",
 "전문 분야(E-1~E-7) 활동범위(자격외 활동 허가 대상) - 미성년 학생 대상 외국어 교육 유관 시설에서의 회화지도(E-2) 활동 등":"Professional-field (E-1~E-7) scope incl. conversation instruction (E-2) at minor-targeted foreign-language facilities.",
 "비전문취업(E-9)의 제조업, 건설업 및 선원취업(E-10) 업종 (한국어능력 4급 이상인 경우 제조업 허용)":"E-9 manufacturing/construction and E-10 seafarer work (manufacturing allowed if TOPIK 4+).",
 "특수형태근로종사자의 활동: 택배기사, 배달대행업체 라이더, 대리기사, 보험설계사, 학습지 교사, 방문판매원 등":"Special-form laborers: couriers, delivery riders, designated drivers, insurance planners, home-visit tutors, door-to-door sales.",
 "파견, 도급, 알선 관계에 따른 취업활동 (단, 법무부장관이 별도로 정하는 지역 대학이 산학연계 방식으로 유학생의 인턴활동을 알선하는 경우는 제외)":"Employment via dispatch/contract/agency (except internship placement by universities designated by the MOJ).",
 "원거리 근무":"Remote work.",
 "과거 불법고용 등 처벌 경력으로 사증발급이 제한되는 업체 및 고용주 사업장에서의 활동":"Work at employers restricted from visa issuance due to past illegal-employment penalties.",
}
EXC_EN = {
 "제조업 분야: 한국어능력 4급 상당 이상 취득한 경우":"Manufacturing: if TOPIK 4 or equivalent.",
 "영어키즈카페, 영어캠프 등 미성년 학생 대상 외국어 교육 유관 시설에서 안전보조원, 놀이보조원 등의 활동을 하려는 사람":"Safety/play assistants at English kid-cafes/camps and minor-targeted foreign-language facilities.",
 "시간제 또는 전일제 계절근로 활동":"Part-time or full-time seasonal work.",
 "전문분야(E-1~E-7, 단, E-6-2 제외)의 보조적인 활동":"Assistance in professional fields (E-1~E-7, excluding E-6-2).",
 "일-학습연계 유학생의 전문분야(E-1~E-7) 인턴 활동":"Internship in professional fields (E-1~E-7) for work-study students.",
 "방학 기간 중 학위과정 유학생의 전문분야(E-1~E-7) 인턴 활동":"Professional-field internship (E-1~E-7) during vacations for degree students.",
 "전문분야(E-1~E-7)의 보조적 활동 또는 인턴 활동으로 시간제 취업을 하는 경우에도 국내법상 일정한 자격요건을 갖추어야 하는 직업은 그 자격요건 충족 필요":"Even when part-time work is professional-field (E-1~E-7) assistance/internship, licensed occupations still require meeting the legal qualification.",
}
DOCS_EN = {
 "신청서, 여권, 외국인등록증 (수수료 면제)":"Application, passport, alien registration card (fee waived).",
 "성적 또는 출석 증명서 (유학생정보시스템으로 확인이 될 경우 생략)":"Grade or attendance certificate (waived if verifiable via the student info system).",
 "한국어 능력(영어 능력) 증빙서류":"Korean (or English) proficiency proof.",
 "외국인 유학생 시간제 취업 확인서":"International-student part-time-work confirmation.",
 "외국인 유학생 시간제취업 요건 준수 확인서 (사업자등록증에 제조업, 건설업이 포함된 경우에 한함)":"Part-time-work requirement compliance form (only if business registration includes manufacturing/construction).",
 "사업자등록증 사본 및 고용주 신분증 사본":"Business registration copy and employer ID copy.",
 "표준근로계약서 사본 (시급 및 근무내용, 시간이 포함되어 있을 것)":"Standard employment contract copy (must state hourly wage, duties, hours).",
 "사업자등록증상의 당사자간 계약을 원칙으로 하며 인력파견업체 등 고용과 사용이 분리된 고용계약은 허용하지 않음":"Direct contract with the business principal; no split employment via staffing agencies.",
}
PEN_EN = {
 "허가를 받지 않고 취업 - 1차 적발 시: 위반 정도가 경미한 경우 통고처분 후 체류허가. 단, 건설업 분야 불법취업은 예외 없이 출국명령(입국규제 유예)":"Work without permit - 1st offense: notice & stay granted if minor; construction-sector illegal work = departure order (no exception).",
 "허가를 받지 않고 취업 - 2차 적발 시: 강제퇴거":"Work without permit - 2nd offense: forced deportation.",
 "허가를 받지 않고 취업 - 2차 적발: 강제퇴거":"Work without permit - 2nd offense: forced deportation.",
 "허가를 받았으나 허가조건 위반 - 1차 적발 시: 엄중 경고":"Permit granted but condition violated - 1st: severe warning.",
 "허가를 받았으나 허가조건 위반 - 2차 적발 시: 유학기간 중 시간제 취업 불허":"Condition violated - 2nd: no part-time work during study.",
 "허가를 받았으나 허가조건 위반 - 3차 적발 시: 유학자격 취소":"Condition violated - 3rd: student status revoked.",
}
PATH_EN = {  # visa labels
 "D-4-6 (국내 연수과정 20개월 이상)":"D-4-6 (domestic training 20+ months)",
 "D-2 유학":"D-2 Student","D-2 유학생":"D-2 Student","D-2 (유학)":"D-2 Student",
 "E-7 (특정활동)":"E-7 Specific Activity","E-7 (특정활동·전문인력)":"E-7 Specific Activity (professional)",
 "D-10 (구직)":"D-10 Job-seeking","D-10 구직":"D-10 Job-seeking",
 "F-2-7 (거주·점수제)":"F-2-7 Resident (points)","F-2 (거주)":"F-2 Resident",
 "F-5 (영주)":"F-5 Permanent","F-5 (영주권)":"F-5 Permanent",
 "E-9":"E-9 Non-professional","E-7-4 (숙련기능인력)":"E-7-4 Skilled worker","E-7-4":"E-7-4",
 "D-4 어학연수":"D-4 Language",
}

def tr(x, m):
    return m.get(str(x), str(x))

def tr_path(x):
    # handle mixed strings
    for k,v in PATH_EN.items():
        if k in str(x): x=str(x).replace(k,v)
    return x

for x in tp["restricted_fields"]:
    s.append(Paragraph("• "+tr(x,RESTR_EN), P("",8.5,leading=12)))
s.append(Spacer(1,4))

# 5. Exceptions
s.append(Paragraph("Exceptions (allowed under conditions)", P("",9.5,bold=True)))
for x in tp["exceptions"]:
    s.append(Paragraph("• "+tr(x,EXC_EN), P("",8.5,leading=12)))
s.append(Spacer(1,4))

# 6. Required docs
s.append(Paragraph("Required documents", P("",9.5,bold=True)))
for x in tp["required_docs"]:
    s.append(Paragraph("• "+tr(x,DOCS_EN), P("",8.5,leading=12)))
s.append(Spacer(1,4))

# 7. Penalty
s.append(Paragraph("⚠️ Penalties for violation", P("",9.5,bold=True)))
for x in tp["violation_penalty"]:
    s.append(Paragraph("• "+tr(x,PEN_EN), P("",8.5,leading=12)))

s.append(Spacer(1,10))
# 8. Employment paths
s.append(sec("2. Employment After Graduation"))
s.append(Spacer(1,4))
seen=set(); rows=[]
# English conditions by (from,to) signature
COND_EN = {
 ("D-4-6 (국내 연수과정 20개월 이상)","E-7 (특정활동)"):
   "Overseas jr-college or higher + domestic training (D-4-6, 20+ months) completed + national certificate + KIIP stage 4; intended job is professional/technical & related to training field",
 ("D-2 유학","E-7 (특정활동·전문인력)"):
   "Graduate + employment confirmed → change immediately",
 ("D-2 유학","D-10 (구직)"):
   "Not yet employed after graduation (max 2 yrs)",
 ("D-2 유학","F-2-7 (거주·점수제)"):
   "Meet points-based residence criteria",
 ("D-2 유학","F-5 (영주)"):
   "Long-term stay & PR criteria",
 ("E-9","E-7-4 (숙련기능인력)"):
   "5+ yrs legal work in last 10 yrs via E-9/E-10/H-2 (4+ yrs + KIIP stage 3 counts)",
 ("E-9","F-2 (거주)"):
   "Long-term stay criteria",
 ("E-9","F-5 (영주)"):
   "Long-term stay criteria",
 ("D-2 유학","E-7 (특정활동)"):
   "Graduate + employment confirmed → change immediately",
 ("D-2 유학","D-10 (구직)"):
   "Not yet employed after graduation (max 2 yrs)",
 ("D-4 어학연수","D-2 (유학)"):
   "Enter a degree program in Korea → change before term starts",
 ("E-9","E-7-4 (숙련기능인력)"):
   "5+ yrs work (4 yrs + KIIP stage 3)",
}
for x in job["employment_paths"]:
    k=(x["from"],x["to"])
    if k in seen: continue
    seen.add(k)
    rows.append([tr_path(x["from"]),tr_path(x["to"]),COND_EN.get(k,tr_path(x["condition"]))])
s.append(dtable(["From","To","Condition"],rows,widths=[42*mm,48*mm,80*mm]))
s.append(Spacer(1,6))

# 9. E-7 fields (summary in English)
s.append(Paragraph("E-7 eligible occupations (94)", P("",9.5,bold=True)))
s.append(Paragraph("Professional (E-7-1): 67 occupations — managers 15, professionals & related 52. Semi-professional (E-7-2): 10 (office 5, service 5). General skilled (E-7-3). Skilled-worker (E-7-4): 7. Negative-list system. Also: E-7-5 high-income & advanced-industry, E-7-6 best talent, E-7-7 advanced-industry & best talent. (Details per MOJ occupation table.)", P("",8.5)))
s.append(Spacer(1,5))

# 10. E-7-4
s.append(Paragraph("E-7-4 Skilled Worker", P("",9.5,bold=True)))
s.append(dtable(["Target","Requirement"],
    [["Root-industry skilled (S740), agriculture/forestry/fishery (S610), general manufacturing/construction skilled (S700)",
      "Skilled-worker points system; 2026 wage threshold KRW 26M+/yr"]],
    widths=[70*mm,100*mm]))
s.append(Spacer(1,6))

# 11. Key notes (own page so the section is balanced, not a tiny spillover)
s.append(PageBreak())
s.append(sec("3. Key Notes"))
s.append(Spacer(1,4))
NOTES=[
 "Part-time-work special rule: incidental gratuities, prize money, or payment for activities not infringing the essence of student status are exempt from the permit requirement.",
 "Paid research (D-2): study-linked research/internship within your university = exempt. Unrelated research = permit needed. Off-campus study-linked = permit needed; off-campus unrelated = status-outside-activity permit (E-3).",
 "Field-work semester: standard/mandatory field-work curricula are exempt; voluntary field work needs the permit.",
 "D-2 stay-extension caps: jr-college 3 yrs (3-yr: 4), bachelor's 6 (5-yr: 7), master's 5 (3-yr: 6), PhD 8 (2-yr: 7).",
 "Re-entry permit exemption: re-entering within 1 year of departure is exempt; between 1-2 years, apply for a multiple re-entry permit.",
 "E-7 special for excellent-private-institution trainees: D-4-6 (20+ months) + national certificate + KIIP stage 4 → E-7 in the trained field (except E-7-4).",
]
for x in NOTES:
    s.append(Paragraph("• "+x, P("",8.5,leading=12)))

OUT=B+r"\International_Student_Job_Manual_EN.pdf"
doc=SimpleDocTemplate(OUT,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=16*mm,bottomMargin=16*mm,
    title="International Student Job Manual",author="Camnemi")
doc.build(s)
print("생성:",OUT,os.path.getsize(OUT),"bytes")

# verify no hangul
import pymupdf,re
d=pymupdf.open(OUT)
full='\n'.join(p.get_text() for p in d)
h=[x for x in re.findall(r'[가-힣]{2,}',full)]
print("pages:",len(d),"| 남은 한글:",h if h else "없음 ✅")
