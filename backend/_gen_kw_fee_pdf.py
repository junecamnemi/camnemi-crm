#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a clean PDF of 경운대학교 official tuition + scholarship table (from 국제처 page)."""
import pymupdf

# Official data — source: 경운대 국제처 > 외국인입학 > 학부입학 > 등록금 및 장학금
# https://www.ikw.ac.kr/worldle/page/link.tc?mn=3874&pageSeq=2748
TUITION = [
    ("항공공과대학", "항공기계공학과", "공학계열", "4,120,000", "3,980,000"),
    ("", "항공전자공학과 / 항공정보통신공학과", "공학계열", "4,120,000", "3,980,000"),
    ("", "에너지소재공학과 / 소프트웨어학 / 무인기공학과", "공학계열", "4,120,000", "3,980,000"),
    ("항공서비스대학", "항공운항학과", "자연2계열", "5,005,000", "4,865,000"),
    ("", "항공관광서비스학과", "인문계열", "3,170,000", "3,030,000"),
    ("", "항공교통물류학과", "공학2계열", "4,045,000", "3,905,000"),
    ("", "안전방재공학과", "공학계열", "4,120,000", "3,980,000"),
    ("간호보건대학", "간호학과", "자연계열", "4,045,000", "3,905,000"),
    ("", "물리치료학과 / 작업치료학과 / 치위생학과 / 임상병리학과", "자연계열", "4,045,000", "3,905,000"),
    ("", "의료서비스경영학과 / 상담복지학", "인문계열", "3,170,000", "3,030,000"),
    ("사회안전대학", "군사학과 / 경찰행정학과", "인문계열", "3,170,000", "3,030,000"),
    ("", "항공보안경호학부 / 스포츠건강재활학과", "체육계열", "4,070,000", "3,930,000"),
    ("", "멀티미디어학과", "예능계열", "4,320,000", "4,180,000"),
]
SCHOLAR = [
    ("TOPIK 5급 이상 / 한국어연수 4급 이상 수료 / 본교 한국어능력시험 합격자", "첫학기 수업료 100%"),
    ("TOPIK 4급 이상", "첫학기 수업료 70%"),
    ("TOPIK 3급 이상 / 한국어연수 4급 이상 수료 / IELTS 6.5 이상", "첫학기 수업료 50%"),
    ("IELTS 5.5 이상 / 기타(외부 추천 등)", "첫학기 수업료 20%"),
]
SCHOLAR2 = [
    ("TOPIK 5급 + 직전학기 평점 3.5 이상", "수업료 100%"),
    ("TOPIK 4급 + 직전학기 평점 3.5 이상", "수업료 70%"),
    ("TOPIK 3급 + 직전학기 평점 3.0 이상", "수업료 50%"),
    ("직전학기 평점 3.0 이상", "수업료 30%"),
]

doc = pymupdf.open()
page = doc.new_page(width=595, height=842)  # A4

# register a Korean-capable font (Windows 맑은 고딕)
KFONT = r"C:\Windows\Fonts\malgun.ttf"
page.insert_font(fontname="KR", fontfile=KFONT)

def txt(page, x, y, s, size=9, bold=False, font="KR"):
    page.insert_text((x, y), s, fontsize=size, fontname=font, color=(0, 0, 0))

y = 50
txt(page, 40, y, "경운대학교 등록금 및 장학금 (외국인 학부)", size=15, font="KR"); y += 22
txt(page, 40, y, "출처: 경운대 국제처 > 외국인입학 > 학부입학 > 등록금 및 장학금 (2023학년도 기준)", size=8); y += 20
txt(page, 40, y, "1) 등록금 (단위: 원, 1학년 입학학기 / 2~4학년)", size=11); y += 16
txt(page, 45, y, "대학                학부(과)                                      계열        1학년        2~4학년", size=8); y += 12
for r in TUITION:
    txt(page, 45, y, f"{r[0][:8]:<8} {r[1][:44]:<44} {r[2]:<9} {r[3]:>10} {r[4]:>10}", size=8); y += 12
y += 10
txt(page, 40, y, "2) 입학장학금 (첫 학기)", size=11); y += 16
for cond, amt in SCHOLAR:
    txt(page, 45, y, f"   {cond[:70]}  →  {amt}", size=8); y += 12
y += 10
txt(page, 40, y, "3) 성적우수장학금 (재학 중, 매 학기)", size=11); y += 16
for cond, amt in SCHOLAR2:
    txt(page, 45, y, f"   {cond[:60]}  →  {amt}", size=8); y += 12
y += 14
txt(page, 40, y, "※ 등록금은 2023학년도 기준 — 최신 금액은 학교/국제처 확인 필요", size=8)
y += 12
txt(page, 40, y, "※ 모집요강 PDF에는 등록금·장학금 표가 없으며, 위 자료는 공식 국제처 웹페이지 기준임", size=8)

OUT = r"C:\Users\USER\camnemi-crm\backend\경운대_등록금_장학금_정리.pdf"
doc.save(OUT)
doc.close()
print("저장:", OUT)
import os
print(f"{os.path.getsize(OUT)/1024:.0f} KB")
