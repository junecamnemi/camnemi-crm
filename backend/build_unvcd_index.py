#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_unvcd_index.py — adiga(unvCd·홈페이지·주소) + 대학알리미(재적·외국인 통계) 통합.

최종 산출물: backend/unvcd_index.json
  key = unvCd
  value = { name, school_type(univ4/junior), homepage, ipsi_homepage, addr, tel,
            stats: {enrolled, international, year(2025)},
            excluded: {reason} or null }

필터(사용자 지시): 재적(2025말) 2000명 이하 제외, 신학대·교육대 제외.
"""
import sqlite3, json, os, re

B = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(B, "_acdmcp", "package", "data", "seed", "academyinfo_15118998.sqlite")

# 1) adiga 기본 URL + unvCd
basic = json.load(open(os.path.join(B, "_adiga_basic_urls.json"), encoding="utf-8"))
univ = json.load(open(os.path.join(B, "_adiga_univ_list.json"), encoding="utf-8"))
jr = json.load(open(os.path.join(B, "_adiga_junior_list.json"), encoding="utf-8"))

def base_name(nm):
    return re.sub(r"\[[^\]]+\]$", "", nm).strip()

# 2) 대학알리미 통계 — school_name 표준화로 매칭
con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("""
  SELECT i.school_name, i.campus_name, i.school_kind, i.school_type, i.establishment_type, i.region_name,
         max(CASE WHEN o.indicator_id='enrolled_students' THEN o.value END) AS enrolled,
         max(CASE WHEN o.indicator_id='international_students' THEN o.value END) AS itl
  FROM institutions i LEFT JOIN observations o ON o.institution_id=i.id AND o.year=2025
  GROUP BY i.id
""")
acad = {}
for r in cur.fetchall():
    name, campus, kind, stype, estab, region, enrolled, itl = r
    # 본교만 (캠퍼스는 대표 본교에 합산하지 않고, 캠퍼스별 유지)
    acad.setdefault(r[0], []).append({
        "campus": campus, "kind": kind, "stype": stype, "estab": estab, "region": region,
        "enrolled": enrolled, "international": itl
    })

# adiga 이름(한글) → acad 이름 매핑 돕기 (괄호 캠퍼스밖)
def norm(s):
    s = base_name(s)
    return re.sub(r"\([^)]*\)$", "", s).replace(" ", "")

# 3) 통합
out = {}
manual_acad = {norm(k): k for k in acad}

# verified_kb의 BA 통계(대학알리미 2025, 캠퍼스 합산) — adiga 미매칭 보완
kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
kb_ba = kb.get("schools", {})
kb_stat = {norm(n): v for n, v in kb_ba.items()}  # norm명 -> {student_count, foreign_students}

# 캠퍼스 합산: 같은 base 학교명의 모든 캠퍼스의 enrolled/international을 합침
def acad_sum(basekey):
    entries = acad.get(basekey, [])
    return (sum(int(e["enrolled"]) for e in entries if e["enrolled"]),
            sum(int(e["international"]) for e in entries if e["international"]),
            entries[0]["stype"] if entries else None)
for cd in list(univ.keys()):
    if "[본교]" not in univ[cd]:
        continue
    nm = base_name(univ[cd])
    key = norm(nm)
    # acad DB 키: base 이름이 정확히 있는지, 없으면 캠퍼스별로 base 매칭해 합산
    acad_key = manual_acad.get(key)
    if acad_key:
        enrolled, itl, stype = acad_sum(acad_key)
    else:
        # base 매칭: acad의 모든 키 중 norm이 key와 같은 것들 합산
        enrolled = itl = 0; stype = None
        for ak, entries in acad.items():
            if norm(ak) == key:
                e, i, s = acad_sum(ak)
                enrolled += e; itl += i; stype = s or stype
        if enrolled == 0: enrolled = None
    meta = basic.get(cd, {})
    # adiga 통계가 0/None이면 verified_kb(대학알리미 동일소스)로 보완
    kv = kb_stat.get(key)
    if (not enrolled) and kv and kv.get("student_count"):
        enrolled, itl = kv["student_count"], kv.get("foreign_students", 0)
    out[cd] = {
        "name": nm, "unvCd": cd, "school_type": "univ4",
        "homepage": meta.get("homepage"), "ipsi_homepage": meta.get("ipsi_homepage"),
        "addr": meta.get("addr"), "tel": meta.get("tel"),
        "stats": {"enrolled_2025": enrolled, "international_2025": itl, "year": 2025},
        "excluded": None
    }
    # 필터
    if "신학대" in nm and "성결대" not in nm:
        out[cd]["excluded"] = "신학대"
    elif stype == "교육대학":
        out[cd]["excluded"] = "교육대"
    elif enrolled is not None and enrolled < 2000:
        out[cd]["excluded"] = f"재적{enrolled}명(<2000)"

for cd in list(jr.keys()):
    if "[본교]" not in jr[cd]:
        continue
    nm = base_name(jr[cd])
    key = norm(nm)
    acad_key = manual_acad.get(key)
    if acad_key:
        enrolled, itl, stype = acad_sum(acad_key)
    else:
        enrolled = itl = 0; stype = None
        for ak, entries in acad.items():
            if norm(ak) == key:
                e, i, s = acad_sum(ak)
                enrolled += e; itl += i; stype = s or stype
        if enrolled == 0: enrolled = None
    meta = basic.get(cd, {})
    kv = kb_stat.get(key)
    if (not enrolled) and kv and kv.get("student_count"):
        enrolled, itl = kv["student_count"], kv.get("foreign_students", 0)
    out[cd] = {
        "name": nm, "unvCd": cd, "school_type": "junior",
        "homepage": meta.get("homepage"), "ipsi_homepage": meta.get("ipsi_homepage"),
        "addr": meta.get("addr"), "tel": meta.get("tel"),
        "stats": {"enrolled_2025": enrolled, "international_2025": itl, "year": 2025},
        "excluded": None
    }
    if "신학대" in nm and "성결대" not in nm:
        out[cd]["excluded"] = "신학대"
    elif enrolled is not None and enrolled < 2000:
        out[cd]["excluded"] = f"재적{enrolled}명(<2000)"

with open(os.path.join(B, "unvcd_index.json"), "w", encoding="utf-8") as f:
    json.dump({"meta": {"generated": "2026-09-19", "source": "adiga+academyinfo_mcp data.go.kr 15118998", "stat_year": 2025},
               "count": {"univ4": sum(1 for v in out.values() if v["school_type"]=="univ4"),
                         "junior": sum(1 for v in out.values() if v["school_type"]=="junior")},
               "schools": out}, f, ensure_ascii=False, indent=1)

# 요약
from collections import Counter
exc = Counter(v["excluded"] for v in out.values() if v["excluded"])
nole = Counter(v["school_type"] for v in out.values() if v["stats"]["enrolled_2025"] is None)
print(f"총 {len(out)} (4년제 {sum(1 for v in out.values() if v['school_type']=='univ4')} / 전문대 {sum(1 for v in out.values() if v['school_type']=='junior')})")
print("제외 사유:", dict(exc))
print("통계 미확보(재적):", dict(nole))
print("등록 유지:", sum(1 for v in out.values() if not v['excluded']))