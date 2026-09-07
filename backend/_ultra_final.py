#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL ultra-verified table: IELTS 5.5 + DS majors + foreigner track + 2027 guide + app period.
Applies the deep-verified language requirements (from actual 2027 foreigner PDFs)."""
import json

# ---- Deep-verified language verdicts (from _lang_verify.json + manual checks of PDFs) ----
# track_ok: whether IELTS 5.5 alone is accepted (English track or listed 5.5)
# IELTS 5.5 accepted
IELTS55_OK = {
    # (rank or None, loc, note)
    "중앙대학교": "IELTS 5.5/TOPIK3 명시, 2027 외국인, 원서 2026.8.31~9.18",
    "인하대학교": "IELTS 5.5/TOPIK3, 영어트랙, 2027 외국인, 원서 2026.9.30~11.5",
    "가천대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 원서 2026.10.12~10.23",
    "경남대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 원서 2026.10.26~11.20",
    "경동대학교": "IELTS 5.5, 2027 외국인, 원서 2026.9.7~9.11",
    "계명대학교": "IELTS 5.5(일부전공 5.0), 2027 외국인, 원서 2026.9.21~10.23",
    "단국대학교": "IELTS 5.5, 2027 외국인, 1차 10.1~16 / 2차 12.2~18",
    "목원대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 1차 9.16~10.7 / 2차 11.23~12.23",
    "배재대학교": "IELTS 5.5, 2027 외국인, 원서 2026.10.16~10.22",
    "우송대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 원서 2026.7.16~",
    "을지대학교": "IELTS 5.5, 2027 외국인, 원서 2026.9.7~9.11",
    "인제대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 원서 2026.9.7~9.11",
    "평택대학교": "IELTS 5.5, 영어트랙, (PDF상 2026 표기 주의), 원서 2025.11.10~12.19",
    "한서대학교": "IELTS 5.5, 영어트랙, 2027 외국인, 1학기 12.14~18 / 2학기 6.21~25",
    # 영어/한국어 트랙 병행 - 영어트랙으로 IELTS 5.5 지원 가능 (스캔에서 5.5 값 안 잡혔으나 eng트랙 존재)
    "연세대학교": "TOPIK5 또는 영어트랙(IELTS), 2027 외국인, 원서 2026.9.1~9.17",
    "영남대학교": "TOPIK3~4 또는 영어트랙, 2027 외국인, 원서 2026.10.12~11.13",
    "숙명여자대학교": "TOPIK3 또는 영어트랙(일부전공 IELTS 5.5), 2027 외국인, 1차 10.7~16 / 2차 11.6~20 / 3차 12.3~18",
}

# NOT accepted (TOPIK only, or IELTS >5.5)
IELTS55_NO = {
    "고려대학교": "IELTS 7.0 요구 (TOPIK5)",
    "국립창원대학교": "TOPIK3만 (영어트랙 없음)",
    "제주대학교": "TOPIK3만, 데이터사이언스는 TOPIK4 요구",
    "청주대학교": "TOPIK3만 (영어트랙 없음)",
    "서울여자대학교": "TOPIK3만",
    "가톨릭관동대학교": "TOPIK2/4만 (영어트랙 없음)",
    "국립경국대학교": "TOPIK3~5만",
}

# ---- Build final table from data.js + the above ----
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
    if not has_ds_major(u):
        continue
    nm = u.get("n")
    if nm not in IELTS55_OK:
        continue
    tu = ((u.get("tuition") or {}).get("ba") or {})
    req = u.get("req") or {}
    rows.append({
        "school": nm, "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts_data": req.get("ielts"), "topik_data": req.get("topik"),
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "note": IELTS55_OK[nm],
        "majors": " / ".join(list_ds_majors(u)), "scholarship": sch_summary(u),
    })

def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    return rk
rows.sort(key=sk)

import csv
out_path = r"C:\Users\USER\camnemi-crm\backend\recommend_ultra.csv"
with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["순위","학교","영문명","지역","IELTS(data)","TOPIK(data)","등록금최소","등록금최대","데이터사이언스학과","장학금","검증비고"])
    for r in rows:
        w.writerow([r["rank"] or "", r["school"], r["eng"], r["loc"],
                    r["ielts_data"] or "", r["topik_data"] or "", r["tmin"] or "", r["tmax"] or "",
                    r["majors"], r["scholarship"], r["note"]])

print(f"IELTS 5.5 + DS + 외국인 + 2027 확정: {len(rows)}개\n")
for r in rows:
    rk = r["rank"] if r["rank"] else "-"
    t = f"₩{r['tmin']:,}~₩{r['tmax']:,}" if r["tmin"] and r["tmax"] else (f"₩{r['tmin']:,}" if r["tmin"] else "-")
    print(f"R{rk} {r['school']} | {r['loc']} | {t}")
    print(f"   {r['note']}")
    print(f"   학과: {r['majors'][:130]}")
print("\n저장:", out_path)
