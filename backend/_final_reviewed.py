#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final reviewed classification: track (foreigner vs jaeoe) + guide year, manual overrides."""
import re
import json
import csv

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"
MASTER = r"C:\Users\USER\camnemi-crm\backend\_guide_2027_master.json"
ADIGA = r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json"

def load_datajs():
    with open(DATA_FILE, encoding="utf-8") as f:
        content = f.read()
    start = content.find("[")
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                return json.loads(content[start:i + 1])
    return []

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

univs = load_datajs()
master = load_json(MASTER)
adiga = load_json(ADIGA)

adiga_by_school = {}
for path, info in adiga.items():
    nm = info.get("name", "")
    if "외국인" in nm:
        m = re.match(r"^\d+_(.+?)(?:\[.*?\])?_20\d+_외국인\.pdf$", nm)
        if not m:
            m = re.match(r"^(.+?)_20\d+_외국인\.pdf$", nm)
        if m:
            adiga_by_school.setdefault(m.group(1), info.get("viewLink"))

master_by_school = {}
for item in master:
    master_by_school[item.get("school", "")] = item

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

def list_ds_majors(u, limit=6):
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

def sch_summary(u, maxlen=180):
    s = u.get("scholarships") or []
    if not s:
        return ""
    parts = []
    for sch in s[:2]:
        nm = sch.get("name", "")
        tiers = sch.get("tiers") or []
        if tiers:
            t0 = tiers[0]
            parts.append(f"{nm}: {t0.get('score_type','')} {t0.get('score','')} → {t0.get('amount','')}")
            if len(tiers) > 1:
                parts[-1] += f" (외 {len(tiers)-1}단계)"
        else:
            parts.append(nm)
    return " / ".join(parts)[:maxlen]

# ---- Classification ----------------------------------------------------------
# track: F = foreigner included, J = jaeoe-only, ? = unclear
# year : 2027 / 2026 / ?

# Manual verdicts after full review (school -> (track, year, note))
# Based on master ba_note + adiga foreigner map + web checks.
MANUAL = {
    # ---- 2027 foreigner confirmed (adiga 외국인 PDF) ----
    "연세대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "고려대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "중앙대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "인하대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "가천대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "가톨릭관동대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "강서대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "경남대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "경동대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "계명대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "국립경국대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "국립창원대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "단국대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "덕성여자대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "목원대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "배재대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "서울여자대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "선문대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "영남대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "우송대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "을지대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "인제대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "제주대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "청주대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "평택대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "한서대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    "건양대학교": ("F", "2027", "adiga 외국인 2027 PDF"),
    # ---- 2027 combined 재외국민+외국인 (foreigner included) ----
    "건국대학교": ("F", "2027", "재외국민과외국인전형 2027"),
    "동국대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "국민대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "세종대학교": ("F", "2027", "재외국민과 외국인전형 2027"),
    "가톨릭대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "경상국립대학교": ("F", "2027", "재외국민과 외국인 2027"),
    "국립순천대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "국립한국교통대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "나사렛대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "동덕여자대학교": ("F", "2027", "재외국민과 외국인 2027"),
    "서경대학교": ("F", "2027", "재외국민과 외국인 2027"),
    "신한대학교": ("F", "2027", "재외국민/외국인 2027 (2027 Admission for Int'l Student)"),
    "한국항공대학교": ("F", "2027", "재외국민과 외국인 특별전형 2027"),
    "한림대학교": ("F", "2027", "재외국민및외국인 2027"),
    "한국성서대학교": ("F", "2027", "재외국민과 외국인 2027"),
    # ---- 2027 pure foreigner (부모 모두 외국인/외국인특별전형) ----
    "한국외국어대학교": ("F", "2027", "2027 Spring 부모 모두 외국인 외국인특별전형"),
    "충남대학교": ("F", "2027", "2027 CNU-ASIA 외국인특별전형"),
    "청운대학교": ("F", "2027", "2027 부모 모두 외국인 전형"),
    "서울시립대학교": ("F", "2027", "2027 외국인전형 요강 확인"),
    "전북대학교": ("F", "2027", "2026/2027 학부 외국인 특별전형 계획 (외국인 별도 존재)"),
    # ---- 2026 foreigner (2027 미발간) ----
    "숙명여자대학교": ("F", "2026", "2026 Fall Admission 외국인 (2027 아님)"),
    "강원대학교": ("F", "2026", "2026 외국인 학부 전형"),
    "경일대학교": ("F", "2026", "2026 후기 재외국민과 외국인"),
    "광주대학교": ("F", "2026", "2026 외국인 신·편입 특별전형"),
    "국립군산대학교": ("F", "2026", "2026 후기 외국인 학부"),
    "국립목포대학교": ("F", "2026", "2026 순수외국인"),
    "대구가톨릭대학교": ("F", "2026", "2026 후기 외국인특별전형"),
    "대구대학교": ("F", "2026", "2026-2 외국인 (재외국민 2027 별도)"),
    "대구한의대학교": ("F", "2026", "2026 후기 외국인"),
    "동명대학교": ("F", "2026", "2026-2 외국인유학생 특별전형"),
    "동서대학교": ("F", "2026", "2026 후기 외국인전형"),
    "부산가톨릭대학교": ("F", "2026", "2026 전기 외국인 특별전형"),
    "상지대학교": ("F", "2026", "2026 외국인모집요강"),
    "성결대학교": ("F", "2026", "2026-1 외국인 입학"),
    "세명대학교": ("F", "2026", "2026 외국인"),
    "순천향대학교": ("F", "2026", "2026-2 외국인 특별전형"),
    "신경주대학교": ("F", "2026", "2026-2 외국인 특별전형"),
    "조선대학교": ("F", "2026", "2026-2 외국인특별전형"),
    "한남대학교": ("F", "2026", "2026 외국인 신입학"),
    "한성대학교": ("F", "2026", "2026 순수외국인"),
    "협성대학교": ("F", "2026", "2026-2 순수외국인전형"),
    "김천대학교": ("F", "2026", "2026 외국인 특별전형"),
    "극동대학교": ("F", "2026", "2026 재외국민과 외국인"),
    # ---- 재외국민 전용만 (제외) ----
    "부산대학교": ("J", "2027", "2027 재외국민 특별전형만 확인 (외국인 전형은 국제처 별도, 2027 요강 미확인)"),
    "국립부경대학교": ("J", "2027", "2027 재외국민 특별전형"),
    "명지대학교": ("J", "2027", "2027 재외국민 특별전형"),
    "부산외국어대학교": ("J", "2027", "2027 수시 재외국민전형"),
    "수원대학교": ("J", "2027", "2027 재외국민"),
    "숭실대학교": ("J", "2027", "2027 재외국민 특별전형"),
    "전주대학교": ("J", "2027", "2027 재외국민 모집요강"),
    "삼육대학교": ("J", "2027", "2027 재외국민모집"),
    "상명대학교": ("J", "2027", "2027 재외국민 특별전형"),
    "용인대학교": ("J", "2027", "2027 재외국민 특별전형 (외국인은 2026-9월)"),
    "국립금오공과대학교": ("J", "2027", "2027 재외국민 특별전형"),
    "인천대학교": ("J", "2027", "2027 재외국민 특별전형 (재외국민 및 외국인 50명 포함 계획)"),
}

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
    verdict = MANUAL.get(nm)
    if not verdict:
        # fallback: adiga foreigner -> F 2027
        if nm in adiga_by_school:
            verdict = ("F", "2027", "adiga 외국인 2027 PDF (fallback)")
        else:
            continue
    track, yr, note = verdict
    tu = ((u.get("tuition") or {}).get("ba") or {})
    # link
    link = adiga_by_school.get(nm)
    if not link:
        mi = master_by_school.get(nm) or {}
        link = mi.get("ba_src") or ""
        if not link:
            b = mi.get("ba_url") or ""
            if b and b != "adiga_2027 (downloaded)":
                link = b
    rows.append({
        "school": nm, "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts": u_ielts, "topik": req.get("topik"), "selftest": "Y" if req.get("selftest") else "",
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "track": track, "yr": yr, "note": note, "link": link,
        "majors": " / ".join(list_ds_majors(u)), "scholarship": sch_summary(u),
    })

def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["yr"] == "2027" else 1
    return (rk, gy)

rows.sort(key=sk)

fk = [r for r in rows if r["track"] == "F"]
jk = [r for r in rows if r["track"] == "J"]

out = r"C:\Users\USER\camnemi-crm\backend\recommend_final.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["전형","가이드연도","순위","학교","영문명","지역","IELTS","TOPIK","자체시험","등록금최소","등록금최대","데이터사이언스관련학과","장학금","비고","가이드링크"])
    for r in rows:
        track_kr = "외국인" if r["track"] == "F" else "재외국민"
        w.writerow([track_kr, r["yr"], r["rank"] or "", r["school"], r["eng"], r["loc"],
                    r["ielts"] or "", r["topik"] or "", r["selftest"], r["tmin"] or "", r["tmax"] or "",
                    r["majors"], r["scholarship"], r["note"], r["link"]])

from collections import Counter
print("외국인 전형:", len(fk), "| 재외국민 전용:", len(jk))
print("외국인 - 연도별:", dict(Counter(r['yr'] for r in fk)))
print("외국인 - 지역별:", dict(Counter(r['loc'] for r in fk)))
print()
print("== 외국인 전형 (랭크순) ==")
for r in fk:
    if r["rank"]:
        print(f"[{r['yr']}] R{r['rank']} {r['school']} ({r['loc']})")
print()
print("== 외국인 전형 (랭크 없음, 2027) ==")
for r in fk:
    if not r["rank"] and r["yr"] == "2027":
        print(f"[{r['yr']}] {r['school']} ({r['loc']})")
print()
print("== 외국인 전형 (2026) ==")
for r in fk:
    if r["yr"] == "2026":
        print(f"[2026] {r['school']} ({r['loc']})")
print()
print("== 재외국민 전용 (제외) ==")
for r in jk:
    print(f"- {r['school']} ({r['loc']}) | {r['note']}")
print()
print("저장:", out)
