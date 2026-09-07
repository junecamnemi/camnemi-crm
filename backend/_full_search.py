#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Join data.js (IELTS/major) + guide master (guide status) + adiga map (foreigner PDFs)
to produce the full recommended list: IELTS 5.5 + data-science majors, with most recent guide."""
import re
import json

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

# Build adiga foreigner map: school name -> (viewlink, filename)
adiga_by_school = {}
for path, info in adiga.items():
    nm = info.get("name", "")
    if "외국인" in nm:
        # extract school name from filename like 0000063_가천대학교_2027_외국인.pdf
        m = re.match(r"^\d+_(.+?)_20\d+_외국인\.pdf$", nm)
        if m:
            adiga_by_school[m.group(1)] = info.get("viewLink")

# Build master map: school -> ba info
master_by_school = {}
for item in master:
    master_by_school[item.get("school", "")] = item

# Keyword filter for data-science related majors (tightened)
DS_KW = ["data", "데이터", "빅데이터", "ai", "인공지능", "intelligence", "소프트웨어", "software",
         "컴퓨터", "computer", "통계", "statistics", "정보통신", "정보보호", "정보", "ict",
         "sw", "사이버", "사이버보안", "산업공학", "industrial", "지능정보", "빅데"]

def has_ds_major(u):
    texts = []
    for mm in (u.get("majors_ba") or []):
        texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
    if not texts:
        texts = [str(x).lower() for x in (u.get("majors") or [])]
    combined = " ".join(texts)
    return any(kw.lower() in combined for kw in DS_KW)

# Guide status ranking: prefer 2027, then 2026, then any
def guide_status_score(u_name):
    mi = master_by_school.get(u_name)
    if not mi:
        return None, None, None, None
    st = mi.get("ba_status", "")
    if st == "2027_adiga" or st == "2027_own":
        # get best link
        link = None
        if u_name in adiga_by_school:
            link = adiga_by_school[u_name]
        elif mi.get("ba_src"):
            link = mi["ba_src"]
        elif mi.get("ba_url") and mi["ba_url"] != "adiga_2027 (downloaded)":
            link = mi["ba_url"]
        return "2027", st, link, mi
    elif st == "2026_or_older":
        link = mi.get("ba_src") or (mi.get("ba_url") if mi.get("ba_url") and mi["ba_url"] != "adiga_2027 (downloaded)" else None)
        return "2026", st, link, mi
    else:
        return "?", st, None, mi

# Filter candidates
rows = []
for u in univs:
    if u.get("type") not in ("univ", None) or u.get("type") == "junior":
        pass
    # IELTS filter: req.ielts <= 5.5 if present
    req = u.get("req") or {}
    u_ielts = req.get("ielts")
    if u_ielts is not None:
        try:
            if float(u_ielts) > 5.5:
                continue
        except ValueError:
            pass
    # major filter
    if not has_ds_major(u):
        continue
    yr, st, link, mi = guide_status_score(u.get("n"))
    rows.append({
        "name": u.get("n"),
        "eng": u.get("en"),
        "loc": u.get("loc"),
        "rank": u.get("rk"),
        "ielts": u_ielts,
        "topik": req.get("topik"),
        "selftest": req.get("selftest"),
        "tuition_min": ((u.get("tuition") or {}).get("ba") or {}).get("min"),
        "tuition_max": ((u.get("tuition") or {}).get("ba") or {}).get("max"),
        "guide_yr": yr,
        "guide_status": st,
        "guide_link": link,
        "guide_note": (mi.get("ba_note") or "")[:200] if mi else "",
    })

# Sort: rank first, then guide year (2027 first), then tuition
def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["guide_yr"] == "2027" else (1 if r["guide_yr"] == "2026" else 2)
    t = r["tuition_min"] if r["tuition_min"] else 999999999
    return (rk, gy, t)

rows.sort(key=sk)

print(f"전체 후보: {len(rows)}개 (IELTS 5.5 + 데이터사이언스 관련 학과)\n")
print("=" * 100)
for r in rows:
    t = ""
    if r["tuition_min"] and r["tuition_max"]:
        t = f"₩{r['tuition_min']:,}~₩{r['tuition_max']:,}"
    elif r["tuition_min"]:
        t = f"₩{r['tuition_min']:,}"
    req = []
    if r["ielts"]: req.append(f"IELTS {r['ielts']}")
    if r["topik"]: req.append(f"TOPIK {r['topik']}")
    if r["selftest"]: req.append("자체시험")
    reqs = ", ".join(req) if req else "-"
    print(f"[{r['guide_yr'] or '?'}] {r['name']} ({r['eng']}) | Rank {r['rank'] if r['rank'] else '-'} | {r['loc']}")
    print(f"    요건: {reqs} | 등록금: {t}")
    print(f"    가이드: {r['guide_link'] or '(가이드 링크 없음)'}")
