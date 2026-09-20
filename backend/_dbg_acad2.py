#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""academyinfo_stats_ingest.py — 대학알리미(academyinfo-mcp 스냅샷: data.go.kr 15118998)에서
재적(재학생)·외국인 학생 수 추출. adiga 기본 URL과 unvCd로 연결.

출력: backend/_school_stats.json  {normalized_name: {enrolled, international, year, school_kind}}
"""
import sqlite3, json, os, re

B = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(B, "_acdmcp", "package", "data", "seed", "academyinfo_15118998.sqlite")

con = sqlite3.connect(DB)
cur = con.cursor()

# 지표 id
cur.execute("SELECT indicator_id FROM indicators")
inds = [r[0] for r in cur.fetchall()]
print("지표:", len(inds))

# 기관 전체 (4년제+전문대) — school_kind/type 확인
cur.execute("SELECT id, school_name, campus_name, school_kind, school_type, establishment_type, region_name FROM institutions")
rows = cur.fetchall()
print("기관 수:", len(rows))
kinds = {}
for r in rows:
    kinds[r[3]] = kinds.get(r[3], 0) + 1
print("school_kind 분포:", kinds)
types = {}
for r in rows:
    types[r[4]] = types.get(r[4], 0) + 1
print("school_type 분포:", types)

# 샘플
for r in rows[:5]:
    print("  기관샘플:", r)

# 재적/외국인 년도별
cur.execute("""
  SELECT i.school_name, i.campus_name, o.indicator_id, o.year, o.value
  FROM observations o JOIN institutions i ON o.institution_id=i.id
  WHERE o.indicator_id IN ('enrolled_students','international_students')
  ORDER BY i.school_name, o.indicator_id, o.year
  LIMIT 30
""")
print("\n샘플 obs (재적/외국인):")
for r in cur.fetchall():
    print("  ", r)