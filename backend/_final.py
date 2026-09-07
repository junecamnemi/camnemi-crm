#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final: IELTS5.5 + DS majors, foreigner-track only, latest guide, with scholarships. -> CSV/XLSX"""
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
        m = re.match(r"^\d+_(.+?)_20\d+_외국인\.pdf$", nm)
        if m:
            adiga_by_school[m.group(1)] = info.get("viewLink")

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

def classify(u_name):
    mi = master_by_school.get(u_name)
    if not mi:
        return None, None, None, ""
    st = mi.get("ba_status", "")
    note = mi.get("ba_note") or ""
    adiga_link = adiga_by_school.get(u_name)
    has_foreigner = False
    jaeoe_only = False
    if adiga_link:
        has_foreigner = True
    if st == "2027_adiga":
        has_foreigner = True
    if "재외국민과외국인" in note or "재외국민과 외국인" in note or "재외국민및외국인" in note or "재외국민및 외국인" in note:
        has_foreigner = True
    if ("외국인" in note) and ("재외국민" not in note):
        has_foreigner = True
    if "for International St" in note or "2027 SPRING ADMISSION" in note:
        has_foreigner = True
    # jaeoe-only signals
    if ("재외국민 특별전형" in note or "재외국민 (overseas Korean) rather than pure 외국인" in note or "for 재외국민" in note) and "외국인" not in note:
        jaeoe_only = True
    if "재외국민" in note and "외국인" not in note and "adiga" not in st and not adiga_link:
        jaeoe_only = True

    if st in ("2027_adiga", "2027_own"):
        yr = "2027"
    elif st == "2026_or_older":
        yr = "2026"
    else:
        yr = "?"
    link = adiga_link or mi.get("ba_src") or ""
    if not link:
        u = mi.get("ba_url") or ""
        if u and u != "adiga_2027 (downloaded)":
            link = u
    track = "F" if has_foreigner else ("J" if jaeoe_only else "?")
    return yr, track, link, note[:200]

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
    yr, track, link, note = classify(u.get("n"))
    tu = ((u.get("tuition") or {}).get("ba") or {})
    rows.append({
        "school": u.get("n"), "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts": u_ielts, "topik": req.get("topik"), "selftest": "Y" if req.get("selftest") else "",
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "yr": yr, "track": track, "link": link, "note": note,
        "majors": " / ".join(list_ds_majors(u)), "scholarship": sch_summary(u),
    })

ok = [r for r in rows if r["track"] == "F" and r["yr"] in ("2027", "2026")]
def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["yr"] == "2027" else 1
    return (rk, gy)
ok.sort(key=sk)

# write CSV
out = r"C:\Users\USER\camnemi-crm\backend\recommend_full.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["가이드연도","순위","학교","영문명","지역","IELTS","TOPIK","자체시험","등록금최소","등록금최대","데이터사이언스관련학과","장학금","가이드링크"])
    for r in ok:
        w.writerow([r["yr"], r["rank"] or "", r["school"], r["eng"], r["loc"], r["ielts"] or "", r["topik"] or "", r["selftest"], r["tmin"] or "", r["tmax"] or "", r["majors"], r["scholarship"], r["link"]])
print("외국인 전형 + 최신가이드:", len(ok), "개 ->", out)
# stats by region
from collections import Counter
c = Counter(r["loc"] for r in ok)
print("지역별:", dict(c))
c2 = Counter(r["yr"] for r in ok)
print("연도별:", dict(c2))
# ranked only
ranked = [r for r in ok if r["rank"]]
print("순위 있는 학교:", len(ranked))
for r in ok:
    print(f"{r['yr']}|R{r['rank'] or '-'}|{r['school']}|{r['loc']}|I{r['ielts'] or '-'}/T{r['topik'] or '-'}|{r['tmin']}")
