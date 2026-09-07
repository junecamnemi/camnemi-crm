#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final detailed analysis: IELTS5.5 + DS majors + foreigner track + HAS application period."""
import re
import json
import csv

# ---- load period scan ----
with open(r"C:\Users\USER\camnemi-crm\backend\_period_scan.json", encoding="utf-8") as f:
    period_scan = json.load(f)

# False-positive date patterns: page numbers, "3 - 1", "13 - 1", "1 - 1", "42-28" (phone), "0-28"
BAD_DATE = re.compile(r"^(\d{1,2})\s*[-–]\s*(\d{1,2})$")  # page ranges like 3-1
PHONE = re.compile(r"^\d{2,3}-\d{2,3}-\d{2,4}$")

def valid_dates(dates):
    """Filter out page numbers / phone fragments from date list."""
    out = []
    for d in dates:
        d = d.strip()
        if not d:
            continue
        if BAD_DATE.match(d):
            continue
        if PHONE.match(d):
            continue
        # must contain at least one 20xx year OR be a recognizable date fragment
        if re.search(r"20\d{2}", d):
            out.append(d)
        elif re.match(r"^\d{1,2}\s*[.\-월]\s*\d{1,2}", d) and len(d) >= 5:
            out.append(d)
    return out

# Reclassify each school from period_scan
period_ok = {}
period_detail = {}
for school, v in period_scan.items():
    if v.get("error"):
        period_ok[school] = False
        period_detail[school] = "PDF 오류"
        continue
    if v.get("chars", 0) == 0:
        period_ok[school] = False
        period_detail[school] = "빈 PDF"
        continue
    best_dates = []
    best_ctx = ""
    for f in v.get("found", []):
        dates = valid_dates(f.get("dates", []))
        if dates:
            best_dates = dates
            best_ctx = f.get("ctx", "")[:200]
            break
    period_ok[school] = bool(best_dates)
    period_detail[school] = (", ".join(best_dates[:3]) + " | " + best_ctx) if best_dates else "모집기간 미발견"

# ---- load data.js for IELTS + majors ----
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

# ---- manual verdicts from previous step (track, year) ----
exec(open(r"C:\Users\USER\camnemi-crm\backend\_final_reviewed.py", encoding="utf-8").read().split("# ---- Classification")[0])

# Rebuild MANUAL from the earlier file - simpler: re-import by re-running logic
# Instead, reload the verdicts from the CSV we already produced
with open(r"C:\Users\USER\camnemi-crm\backend\recommend_final.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    verdicts = {}
    for row in reader:
        verdicts[row["학교"]] = (row["전형"], row["가이드연도"], row["비고"])

# ---- assemble final ----
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
    if nm not in verdicts:
        continue
    track, yr, note = verdicts[nm]
    if track != "외국인":
        continue
    tu = ((u.get("tuition") or {}).get("ba") or {})
    rows.append({
        "school": nm, "eng": u.get("en"), "loc": u.get("loc"), "rank": u.get("rk"),
        "ielts": u_ielts, "topik": req.get("topik"), "selftest": "Y" if req.get("selftest") else "",
        "tmin": tu.get("min"), "tmax": tu.get("max"),
        "yr": yr, "note": note,
        "majors": " / ".join(list_ds_majors(u)), "scholarship": sch_summary(u),
        "has_period": period_ok.get(nm, False),
        "period": period_detail.get(nm, ""),
    })

# Final filter: must have application period
final = [r for r in rows if r["has_period"]]
excluded_no_period = [r for r in rows if not r["has_period"]]

def sk(r):
    rk = r["rank"] if r["rank"] else 9999
    gy = 0 if r["yr"] == "2027" else 1
    return (rk, gy)
final.sort(key=sk)

# ---- output CSV ----
out = r"C:\Users\USER\camnemi-crm\backend\recommend_detail.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["가이드연도","순위","학교","영문명","지역","IELTS","TOPIK","자체시험","등록금최소","등록금최대","데이터사이언스학과","장학금","모집기간(요강에서 확인)","비고"])
    for r in final:
        w.writerow([r["yr"], r["rank"] or "", r["school"], r["eng"], r["loc"],
                    r["ielts"] or "", r["topik"] or "", r["selftest"], r["tmin"] or "", r["tmax"] or "",
                    r["majors"], r["scholarship"], r["period"], r["note"]])

from collections import Counter
print(f"외국인 전형 + 모집기간 확인: {len(final)}개")
print(f"외국인 전형이지만 모집기간 없음(제외): {len(excluded_no_period)}개")
print()
print("== 최종 대상 (모집기간 확인됨) ==")
for r in final:
    rk = r["rank"] if r["rank"] else "-"
    t = f"₩{r['tmin']:,}~₩{r['tmax']:,}" if r["tmin"] and r["tmax"] else (f"₩{r['tmin']:,}" if r["tmin"] else "-")
    print(f"[{r['yr']}] R{rk} {r['school']} | {r['loc']} | I{r['ielts'] or '-'}/T{r['topik'] or '-'} | {t}")
    print(f"    기간: {r['period'][:110]}")
print()
print("== 제외 (모집기간 없음) ==")
for r in excluded_no_period:
    print(f"  {r['school']} | {r['period'][:80]}")
print()
print("저장:", out)
