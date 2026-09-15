#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the complete 일자리 매뉴얼 PDF (Camnemi navy/gold)."""
import json, os, pymupdf
B = r"C:\Users\USER\camnemi-crm\backend"
job = json.load(open(os.path.join(B,"job_manual_kr.json"), encoding="utf-8"))
tp = job.get("time_parttime", {})

NAVY=(0.10,0.18,0.38); GOLD=(0.78,0.60,0.20)
KR=r"C:\Windows\Fonts\malgun.ttf"; KRB=r"C:\Windows\Fonts\malgunbd.ttf"
d=pymupdf.open(); cur={"pg":None,"y":0}
def newpage(cover=False):
    pg=d.new_page(width=595,height=842); pg.insert_font(fontname="KR",fontfile=KR); pg.insert_font(fontname="KRB",fontfile=KRB); # builtin korea font, no embedding needed
    cur["pg"]=pg
    if cover:
        pg.draw_rect(pymupdf.Rect(0,0,595,220),fill=NAVY)
        cur["y"]=260
    else:
        pg.draw_rect(pymupdf.Rect(0,0,595,60),fill=NAVY)
        cur["y"]=88
    return pg
def T(x,s,sz=9,bold=False,color=(0,0,0),y=None):
    pg=cur["pg"]; yy=cur["y"] if y is None else y
    pg.insert_text((x,yy), str(s), fontname=("KRB" if bold else "KR"), fontsize=sz, color=color)
    if y is None: cur["y"]=yy+sz+4
def H(s): 
    if cur["y"]>760: newpage()
    cur["y"]+=6; T(40,s,13,True,NAVY); T(40,"",1); cur["y"]+=2
def SUB(s): 
    if cur["y"]>770: newpage()
    T(44,s,10,True,GOLD)
def LI(s,n=100):
    if cur["y"]>770: newpage()
    for line in str(s).split(" / "):
        T(50,"· "+line.strip()[:n],8)

# cover
newpage(True)
T(40,"외국인 유학생",24,True,(1,1,1),y=90); T(40,"일자리 매뉴얼",30,True,GOLD,y=130)
T(40,"아르바이트(시간제취업) · 졸업 후 취업 경로 · 직종·소득요건",11,False,(0.85,0.85,0.9),y=165)
T(40,"법무부 출입국·외국인정책본부 자료(2026.9) 기준 · Camnemi",9,False,(0.8,0.8,0.85),y=190)
T(40,"시간제취업(아르바이트)",15,True,NAVY,y=270); cur["y"]=292

H("1. 시간제취업 활동 허가")
SUB("기본원칙"); LI(tp.get("basic_principle",""))
SUB("대상"); LI(tp.get("target",""))
SUB("허용 시간 (한국어능력·과정별, '23.7 시행)")
pg=cur["pg"]; y=cur["y"]
for cx,h in [(50,"과정"),(160,"한국어기준"),(300,"주중"),(345,"주말·방학"),(415,"인증대학"),(490,"영어트랙")]:
    pg.insert_text((cx,y),h,fontname="KRB",fontsize=8,color=NAVY)
pg.draw_line((50,y+4),(544,y+4),color=GOLD,width=1); y+=15
for r in tp.get("allowed_hours",[]):
    pg.insert_text((50,y),str(r.get("process",""))[:15],fontname="KR",fontsize=8)
    pg.insert_text((160,y),str(r.get("korean_req",""))[:18],fontname="KR",fontsize=7)
    pg.insert_text((300,y),str(r.get("weekday",""))[:9],fontname="KR",fontsize=7.5)
    pg.insert_text((345,y),str(r.get("weekend_vacation",""))[:11],fontname="KR",fontsize=7.5)
    pg.insert_text((415,y),str(r.get("certified",""))[:11],fontname="KR",fontsize=7.5)
    pg.insert_text((490,y),str(r.get("english_track",""))[:10],fontname="KR",fontsize=7)
    y+=13
cur["y"]=y+8
SUB("D-2 vs D-4 (시작·기간·장소)"); 
for k in ("D-2","D-4"):
    if tp.get("start_by_status",{}).get(k): LI(f"{k} 시작: {tp['start_by_status'][k]}")
for k,lab in [("D-2","D-2 유학"),("D-4","D-4 어학연수")]:
    if tp.get("period_place",{}).get(k): LI(f"{lab}: {tp['period_place'][k]}")
SUB("제한 분야"); 
for s in tp.get("restricted_fields",[]): LI(s)
SUB("예외적 허용");
for s in tp.get("exceptions",[]): LI(s)
SUB("신청 서류");
for s in tp.get("required_docs",[]): LI(s)

H("2. 졸업 후 취업 경로 (체류자격 변경)")
pg=cur["pg"]; y=cur["y"]
for cx,h in [(50,"현재"),(150,"변경"),(250,"조건"),(420,"소득요건")]:
    pg.insert_text((cx,y),h,fontname="KRB",fontsize=8,color=NAVY)
pg.draw_line((50,y+4),(544,y+4),color=GOLD,width=1); y+=15
for p in job.get("employment_paths",[]):
    pg.insert_text((50,y),str(p.get("from",""))[:16],fontname="KR",fontsize=7.5)
    pg.insert_text((150,y),str(p.get("to",""))[:18],fontname="KR",fontsize=7.5)
    pg.insert_text((250,y),str(p.get("condition",""))[:42],fontname="KR",fontsize=7.5)
    pg.insert_text((420,y),str(p.get("income",""))[:22],fontname="KR",fontsize=7.5)
    y+=12
    if y>780: newpage(); y=cur["y"]
cur["y"]=y+6

H("3. E-7 특정활동 (전문 취업)")
LI(job.get("e7_fields","") or "허용직종 94개 (매뉴얼 별표)")

H("4. E-7-4 숙련기능인력")
sk=job.get("e7_4_skilled",{})
LI("대상: "+str(sk.get("target",""))); LI("요건: "+str(sk.get("requirement",""))); LI("쿼터: "+str(sk.get("quota","")))

H("5. 시간제취업 위반 제재")
for s in tp.get("violation_penalty",[]): LI(s)

H("6. 핵심 유의사항")
for s in job.get("key_notes",[]): LI(s)

T(40,"본 매뉴얼은 법무부 자료 요약이며, 최종 판단은 출입국·외국인청(1345) 확인 필요. · Camnemi",7,False,(0.5,0.5,0.5),y=800)
out=os.path.join(B,"일자리_매뉴얼.pdf"); import sys
try:
    d.subset_fonts()
except Exception as e:
    print('subset skip', e)
d.save(out, garbage=4, deflate=True)
print("페이지:", len(d), "| 저장:", out)
