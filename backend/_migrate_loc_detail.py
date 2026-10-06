#!/usr/bin/env python3
"""뷰 `universities` 에 loc_detail 을 노출시킨다(시·군 상세 표시용).

앞서 region_backfill.py 가 cat.school / universities_blob 에 loc_detail 컬럼을 추가했지만
CRM 이 읽는 것은 뷰이므로, 뷰의 SELECT 목록 끝에 COALESCE(s.loc_detail, b.loc_detail) 를 붙인다.
(기존 컬럼 이름/순서는 그대로 — 뒤에만 추가하므로 CREATE OR REPLACE 가 안전하다.)
"""
import datetime as dt
import os
import re
import sys

sys.path.insert(0, r"D:\Hermes\camnemi-crm\backend")
from region_backfill import get_conn  # noqa: E402

SQL_OUT = r"D:\Hermes\camnemi-crm\backend\_migrate_loc_detail.sql"

conn = get_conn()
cur = conn.cursor()
cur.execute("select pg_get_viewdef('public.universities'::regclass)")
d = cur.fetchone()[0].rstrip().rstrip(";")
if "loc_detail" in d:
    print("이미 loc_detail 이 있습니다 — 변경 없음")
else:
    anchor = "b.programs"
    i = d.find(anchor)
    if i < 0:
        raise SystemExit("뷰 정의에서 기준점(b.programs)을 찾지 못했습니다 — 수동 확인 필요")
    j = i + len(anchor)
    tail = d[j:j + 16]
    print("기준점 뒤 텍스트:", repr(tail))
    add = ",\n    COALESCE(s.loc_detail, b.loc_detail) AS loc_detail"
    d = d[:j] + add + d[j:]
    sql = "create or replace view public.universities as\n" + d + ";\n"
    open(SQL_OUT, "w", encoding="utf-8").write(
        "-- "\
        f"generated {dt.datetime.now().isoformat(timespec='seconds')} by _migrate_loc_detail.py\n" + sql)
    cur.execute(sql)
    conn.commit()
    print("뷰 갱신 완료 →", SQL_OUT)

cur.execute("select column_name from information_schema.columns where table_schema='public' "
            "and table_name='universities' order by ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print("loc_detail in view:", "loc_detail" in cols, "| 총 컬럼", len(cols))
cur.execute("select count(*) from universities")
print("행수:", cur.fetchone()[0])
cur.execute("select name_kr, loc, loc_detail from universities where loc_detail is not null order by name_kr limit 12")
for r in cur.fetchall():
    print("   ", r)
cur.close()
conn.close()