#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Classify each IELTS5.5+DS candidate's guide as foreigner vs jaeoe-only, and show latest."""
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

# Classify guide: returns (year, track, link, note)
def classify(u_name):
    mi = master_by_school.get(u_name)
    if not mi:
        return None, None, None, ""
    st = mi.get("ba_status", "")
    note = mi.get("ba_note") or ""
    # Foreigner guide exists in adiga map?
    adiga_link = adiga_by_school.get(u_name)
    # Determine track
    has_foreigner = False
    jaeoe_only = False
    low = note.lower()
    if "재외국민과 외국인" in note or "재외국민및외국인" in note or "재외국민및 외국인" in note or "재외국민과 외국인" in note:
        has_foreigner = True  # combined guide covers foreigner
    elif "외국인" in note and "재외국민" not in note:
        has_foreigner = True
    elif "재외국민" in note and "외국인" not in note:
        jaeoe_only = True
    elif "guide is for 재외국민" in low or "재외국민 (overseas Korean) rather than pure 외국인" in low:
        jaeoe_only = True
    elif "재외국민 특별전형" in note and "외국인" not in note:
        jaeoe_only = True
    if adiga_link:
        has_foreigner = True
        jaeoe_only = False
    # If status is adiga, it's foreigner
    if st == "2027_adiga":
        has_foreigner = True
        jaeoe_only = False

    if st in ("2027_adiga", "2027_own"):
        yr = "2027"
    elif st == "2026_or_older":
        yr = "2026"
    else:
        yr = "?"

    # Best link
    link = adiga_link
    if not link:
        link = mi.get("ba_src") or ""
    if not link:
        u = mi.get("ba_url") or ""
        if u and u != "adiga_2027 (downloaded)":
            link = u
    track = "F" if has_foreigner else ("J" if jaeoe_only else "?")
    return yr, track, link, note[:160]

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
        "name": u.get("n"), "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts": u_ielts, "topik": req.get("topik"), "selftest": req.get("selftest"),
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "yr": yr, "track": track, "link": link, "note": note,
    })

# Only foreigner-track, recent year (2027 or 2026)
ok = [r for r in rows if r["track"] == "F" and r["yr"] in ("2027", "2026")]
# Also include unknown-track but with adiga/combined note (marked F already covers)
jaeoe_only = [r for r in rows if r["track"] == "J"]
unknown = [r for r in rows if r["track"] == "?"]

def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["yr"] == "2027" else 1
    return (rk, gy)

ok.sort(key=sk)

print(f"총 {len(rows)} 후보 중 외국인전형+최신가이드 = {len(ok)}개\n")
print("#### 외국인 전형 (최신 가이드 확인) ####")
for r in ok:
    t = f"₩{r['tmin']:,}~₩{r['tmax']:,}" if r["tmin"] and r["tmax"] else (f"₩{r['tmin']:,}" if r["tmin"] else "-")
    reqs = []
    if r["ielts"]: reqs.append(f"I{str(r['ielts'])}")
    if r["topik"]: reqs.append(f"T{r['topik']}")
    if r["selftest"]: reqs.append("자체")
    reqs = "/".join(reqs) if reqs else "-"
    print(f"[{r['yr']}] {r['name']}|{r['eng']}|R{r['rank'] if r['rank'] else '-'}|{r['loc']}|{reqs}|{t}")
    print(f"    {r['link']}")

print(f"\n#### 재외국민 전용 (제외) {len(jaeoe_only)}개 ####")
for r in jaeoe_only:
    print(f"- {r['name']} ({r['yr']})")

print(f"\n#### 유형 불명 (확인 필요) {len(unknown)}개 ####")
for r in unknown:
    print(f"- {r['name']} ({r['yr']}) | {r['note'][:80]}")
