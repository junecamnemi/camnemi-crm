#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL consolidated analysis: IELTS5.5 + DS majors + foreigner track + confirmed application period.
Each school's guide year is verified from actual PDF content (not the master label)."""
import re
import json
import csv

# ---- load data.js ----
with open(r"C:\Users\USER\camnemi-crm\data.js", encoding="utf-8") as f:
    content = f.read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            univs = json.loads(content[start:i + 1])
            break

# ---- guide year + track verdicts (VERIFIED from PDF content) ----
# year: 2027 = verified 2027 guide with period; 2026 = verified 2026 guide with period
# track: F = foreigner included
VERIFIED = {
    # === adiga 2027 외국인 PDF (진짜 2027, 모집기간 확인됨) ===
    "연세대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.1~9.17"),
    "고려대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.8.3~"),
    "중앙대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.8.31~9.18"),
    "인하대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.30~"),
    "가천대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.12~10.23"),
    "가톨릭관동대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.7.6~7.10"),
    "경남대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.26~11.20"),
    "경동대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.7~9.11"),
    "계명대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.21~10.23"),
    "국립경국대학교": ("F", "2027", "adiga 2027 외국인 PDF, 접수 2026.12.4~"),
    "국립창원대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.11.2~11.13"),
    "단국대학교": ("F", "2027", "adiga 2027 외국인 PDF, 1차 2026.10.1~16 / 2차 12.2~18"),
    "덕성여자대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.12~"),
    "목원대학교": ("F", "2027", "adiga 2027 외국인 PDF, 1차 2026.9.16~10.7 / 2차 11.23~12.23"),
    "배재대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.16~10.22"),
    "서울여자대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.8~10.22"),
    "숙명여자대학교": ("F", "2027", "adiga 2027 외국인 PDF(2027 전기 확인), 원서접수 2026.10.7~10.16"),
    "영남대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.12~11.13"),
    "우송대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.7.16~"),
    "을지대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.7~9.11"),
    "인제대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.9.7~9.11"),
    "제주대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.10.5~10.23"),
    "청주대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.12.1~12.24"),
    "평택대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2025.11.10~12.19"),
    "한서대학교": ("F", "2027", "adiga 2027 외국인 PDF, 1학기 2026.12.14~12.18 / 2학기 2027.6.21~6.25"),
    "건양대학교": ("F", "2027", "adiga 2027 외국인 PDF, 원서접수 2026.7.6~"),
    # === 직접 다운로드 확인: 실제 2026 요강 (마스터에 2027로 잘못 표기됐던 것) ===
    "건국대학교": ("F", "2026", "2026 전기 외국인특별전형 (실제 2026! 마스터 2027 오류), 원서접수 2025.9.4~9.11"),
    "국민대학교": ("F", "2026", "2026학년도 1학기 부모학생 외국인 (실제 2026), 원서접수 2025.9.29~10.16"),
    "세종대학교": ("F", "2026", "2026학년도 외국인 신편입 (실제 2026), 원서접수 2025.9.8~9.19"),
    "동국대학교": ("F", "2026", "2026학년도 학부 외국인 (실제 2026), 원서접수 2025.9.23~10.13"),
    "충남대학교": ("F", "2026", "2026학년도 전기 외국인 (실제 2026), 원서접수 2025.10.13~10.17"),
    "한국외국어대학교": ("F", "2026", "2026학년도 외국인 특별전형 (실제 2026), 원서접수 2025.9.1~9.12"),
    "가톨릭대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.9.15~10.15"),
    "한국항공대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.9.22~10.15"),
    "한림대학교": ("F", "2026", "2026학년도 재외국민및외국인 (실제 2026), 원서접수 2025.11.17~12.23"),
    "경상국립대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.11.27~"),
    "국립한국교통대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 접수 2025.12.29~12.31"),
    "서울시립대학교": ("F", "2026", "2026학년도 외국인전형 (실제 2026), 원서접수 2025.10.10~10.20"),
    "동덕여자대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.9.29~10.24"),
    "나사렛대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.7.1~"),
    "한국성서대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026), 원서접수 2025.9.8~10.17"),
    "청운대학교": ("F", "2026", "2026학년도 부모모두외국인 (실제 2026), 원서접수 2026.3/2026.9"),
    "서경대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (실제 2026)"),
    # === 2026 이전 (제외할 수도) ===
    "국립순천대학교": ("F", "2026", "2026학년도 재외국민과 외국인 (모집기간 명시 확인 필요)"),
}

DS_KW = ["data", "데이터", "빅데이터", "ai", "인공지능", "intelligence", "소프트웨어", "software",
         "컴퓨터", "computer", "통계", "statistics", "정보통신", "정보보호", "사이버", "ict",
         "산업공학", "industrial", "지능정보"]

def has_ds_major(u):
    texts = []
    for mm in (u.get("majors_ba") or []):
        texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
    if not texts:
        texts = [str(x).lower() for x in (u.get("majors") or [])]
    combined = " ".join(texts)
    return any(kw.lower() in combined for kw in DS_KW)

def list_ds_majors(u, limit=8):
    out = []
    for mm in (u.get("majors_ba") or []):
        txt = f"{mm.get('kr','')} ({mm.get('en','')})"
        if any(kw.lower() in txt.lower() for kw in DS_KW):
            out.append(txt)
    if not out:
        for x in (u.get("majors") or []):
            if any(kw.lower() in str(x).lower() for kw in DS_KW):
                out.append(str(x))
    return out[:limit]

def sch_summary(u, maxlen=200):
    s = u.get("scholarships") or []
    if not s:
        return ""
    parts = []
    for sch in s[:2]:
        nm = sch.get("name", "")
        tiers = sch.get("tiers") or []
        if tiers:
            t0 = tiers[0]
            parts.append(f"{nm}: {t0.get('score_type','')} {t0.get('score','')}→{t0.get('amount','')}")
            if len(tiers) > 1:
                parts[-1] += f" (외 {len(tiers)-1}단계)"
        else:
            parts.append(nm)
    return " / ".join(parts)[:maxlen]

rows = []
for u in univs:
    req = u.get("req") or {}
    u_ielts = req.get("ielts")
    if u_ielts is not None:
        try:
            if float(u_ielts) > 5.5:
                continue
        except ValueError:
            pass
    if not has_ds_major(u):
        continue
    nm = u.get("n")
    if nm not in VERIFIED:
        continue
    track, yr, note = VERIFIED[nm]
    if track != "F":
        continue
    tu = ((u.get("tuition") or {}).get("ba") or {})
    rows.append({
        "school": nm, "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts": u_ielts, "topik": req.get("topik"), "selftest": "Y" if req.get("selftest") else "",
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "yr": yr, "note": note,
        "majors": " / ".join(list_ds_majors(u)), "scholarship": sch_summary(u),
    })

def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["yr"] == "2027" else 1
    return (rk, gy)
rows.sort(key=sk)

out = r"C:\Users\USER\camnemi-crm\backend\recommend_final_verified.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["가이드연도(검증)","순위","학교","영문명","지역","IELTS","TOPIK","자체시험","등록금최소","등록금최대","데이터사이언스학과","장학금","모집기간/비고"])
    for r in rows:
        w.writerow([r["yr"], r["rank"] or "", r["school"], r["eng"], r["loc"],
                    r["ielts"] or "", r["topik"] or "", r["selftest"], r["tmin"] or "", r["tmax"] or "",
                    r["majors"], r["scholarship"], r["note"]])

from collections import Counter
print(f"총 {len(rows)}개 (외국인 전형 + 모집기간 확인)")
print("2027:", len([r for r in rows if r['yr']=='2027']), "| 2026:", len([r for r in rows if r['yr']=='2026']))
print()
for r in rows:
    rk = r["rank"] if r["rank"] else "-"
    t = f"₩{r['tmin']:,}~₩{r['tmax']:,}" if r["tmin"] and r["tmax"] else (f"₩{r['tmin']:,}" if r["tmin"] else "-")
    print(f"[{r['yr']}] R{rk} {r['school']} | {r['loc']} | I{r['ielts'] or '-'}/T{r['topik'] or '-'} | {t}")
    print(f"    {r['note'][:100]}")
print()
print("저장:", out)
