#!/usr/bin/env python3
"""region_backfill.py — 지역 표기를 정식명으로 통일한다(요강DB 정본 + 파생 저장소).

대상
  1) Supabase  cat.school.region, cat.school.loc     ← 요강DB **정본**
  2) Supabase  universities_blob.loc                 ← 뷰 `universities` 의 폴백
  3) data.js                                         ← CRM UI + 봇 검색(univ_search) 데이터
  4) backend/verified_kb.json, backend/consulting_db.json

정책
  - 저장은 한글 정식명(`경기도`/`서울특별시`/`강원특별자치도` …)으로만.
  - 시·군 상세(`경기(안산)`)는 **버리지 않고** `loc_detail` / `locDetail` 로 분리 보존.
  - 값이 NULL 이면 **건드리지 않는다**(지어내지 않음). null 목록만 보고한다.
  - 기본은 dry-run. 쓰기는 `--apply`. 쓰기 전 원본을 백업한다.

사용법
    python region_backfill.py            # dry-run (변경 예정 + null 보고)
    python region_backfill.py --apply    # 실제 반영(백업 + 로그)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from region_norm import CANONICAL, is_canonical, normalize  # noqa: E402

BASE = r"D:\Hermes\camnemi-crm"
BACKUP_ROOT = r"D:\Hermes\_sjcu"
LOG_DIR = r"D:\Hermes\_sjcu"
KEY_RE = re.compile(r"^(region|loc)$", re.I)
DATA_JS = os.path.join(BASE, "data.js")
JSONS = [os.path.join(BASE, "backend", "verified_kb.json"),
         os.path.join(BASE, "backend", "consulting_db.json")]
DB_COLS = [("cat.school", "region"), ("cat.school", "loc"), ("universities_blob", "loc")]


# ------------------------------------------------------------------ helpers
def split_new(value):
    """원문 → (정식명, 상세). 상세 없으면 ('', )."""
    kr, det = normalize(value)
    return kr, det


def walk_patch(obj, key_re, log, path=""):
    """dict/list 를 제자리 수정. (region|loc) 문자열 키를 정식명으로."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if key_re.match(str(k)) and isinstance(v, str) and v.strip():
                if not is_canonical(v):
                    kr, det = split_new(v)
                    obj[k] = kr
                    log.append({"path": f"{path}.{k}", "old": v, "new": kr, "detail": det})
                    if det:
                        dk = "loc_detail" if str(k).lower() == "loc" else "region_detail"
                        obj.setdefault(dk, det)
            elif isinstance(v, (dict, list)):
                walk_patch(v, key_re, log, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, it in enumerate(obj):
            walk_patch(it, key_re, log, f"{path}[{i}]")


def patch_datajs(text, log):
    """data.js 의 "loc": "…" 를 정식명으로. 상세가 있으면 "locDetail" 을 옆에 추가."""
    def repl(m):
        old = m.group(2)
        if not old.strip() or is_canonical(old):
            return m.group(0)
        kr, det = split_new(old)
        log.append({"path": "data.js", "old": old, "new": kr, "detail": det})
        out = f'{m.group(1)}{kr}{m.group(3)}'   # 먼저 값을 닫고
        if det:
            out += f', "locDetail": "{det}"'    # 그 다음 상세 키를 붙인다
        return out

    new = re.sub(r'("loc"\s*:\s*")([^"]*)(")', repl, text)
    # 가드: 패치 후 모든 loc 값이 정식명이어야 한다(아니면 쓰지 않는다).
    bad = [v for v in re.findall(r'"loc"\s*:\s*"([^"]*)"', new) if v.strip() and not is_canonical(v)]
    if bad:
        raise SystemExit(f"data.js 패치 검증 실패 — 정규화 안 된 값 {len(bad)}개: {bad[:5]}")
    n0 = len(re.findall(r'"loc"\s*:', text))
    n1 = len(re.findall(r'"loc"\s*:', new))
    if n0 != n1:
        raise SystemExit(f"data.js 패치 검증 실패 — loc 키 개수 {n0} → {n1}")
    return new


# ------------------------------------------------------------------ DB
def db_plan(cur):
    plan = []
    for table, col in DB_COLS:
        cur.execute(f"select distinct {col} from {table} where {col} is not null")
        for (val,) in cur.fetchall():
            if is_canonical(val):
                continue
            kr, det = split_new(val)
            plan.append({"table": table, "col": col, "old": val, "new": kr, "detail": det})
    return plan


def db_null_report(cur):
    out = []
    for table, col in DB_COLS:
        cur.execute(f"select count(*) from {table} where {col} is null")
        n = cur.fetchone()[0]
        if n:
            out.append(f"{table}.{col}: null {n}건")
    cur.execute("select name_kr from cat.school where (loc is null or loc='') order by name_kr limit 40")
    out += [f"   cat.school loc 없음: {r[0]}" for r in cur.fetchall()]
    return out


def db_apply(cur, plan):
    done = 0
    for t in ("cat.school", "universities_blob"):
        cur.execute(f"alter table {t} add column if not exists loc_detail text")
    for p in plan:
        cur.execute(
            f"update {p['table']} set {p['col']}=%(new)s, "
            f"loc_detail=coalesce(%(det)s, loc_detail) where {p['col']}=%(old)s",
            {"new": p["new"], "det": p["detail"] or None, "old": p["old"]})
        done += cur.rowcount
    return done


def get_conn():
    """pg_conn(psycopg3) 우선, 없으면 psycopg2 로 같은 후보에 접속."""
    import pg_conn  # noqa: E402
    try:
        return pg_conn.connect()
    except ModuleNotFoundError:
        import psycopg2
        last = None
        for kw in pg_conn.candidates():
            try:
                c = psycopg2.connect(connect_timeout=8, sslmode="require", **kw)
                c.autocommit = False
                return c
            except Exception as exc:  # noqa: BLE001
                last = f"{kw['host']}:{kw['port']} -> {type(exc).__name__}: {str(exc)[:120]}"
        raise SystemExit(f"no reachable Postgres endpoint (psycopg2). last: {last}")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log = {"ts": ts, "apply": a.apply, "db": [], "datajs": [], "json": {}, "files": {}}

    conn = get_conn()
    cur = conn.cursor()
    try:
        plan = db_plan(cur)
        log["db"] = plan
        print(f"[DB] Supabase 변경 대상 {len(plan)}종(값)")
        for p in plan[:60]:
            print(f"   {p['table']}.{p['col']:7s} {p['old']!r:26s} → {p['new']!r}"
                  + (f"  detail={p['detail']!r}" if p["detail"] else ""))
        nulls = db_null_report(cur)
        if nulls:
            print("\n[DB null — 손대지 않음]")
            for line in nulls[:12]:
                print("   " + line)
        if a.apply:
            done = db_apply(cur, plan)
            conn.commit()
            print(f"\n[DB] 업데이트 완료 — 영향 행 {done}건 (커밋)")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    # 파일들
    files = [DATA_JS] + JSONS
    if a.apply:
        bdir = os.path.join(BACKUP_ROOT, f"region_backup_{ts}")
        os.makedirs(bdir, exist_ok=True)
        for f in files:
            if os.path.exists(f):
                shutil.copy2(f, os.path.join(bdir, os.path.basename(f)))
        print(f"\n[백업] {bdir}")

    for f in files:
        if not os.path.exists(f):
            continue
        txt = open(f, encoding="utf-8").read()
        if f.endswith("data.js"):
            flog = []
            new = patch_datajs(txt, flog)
            log["datajs"] = flog
            print(f"\n[data.js] loc 변경 {len(flog)}건")
            for c in flog[:10]:
                print(f"   {c['old']!r:22s} → {c['new']!r}" + (f"  detail={c['detail']!r}" if c["detail"] else ""))
            if a.apply and new != txt:
                open(f, "w", encoding="utf-8", newline="").write(new)
                log["files"][os.path.basename(f)] = "written"
        else:
            d = json.loads(txt)
            flog = []
            walk_patch(d, KEY_RE, flog)
            log["json"][os.path.basename(f)] = flog
            print(f"\n[{os.path.basename(f)}] 지역 변경 {len(flog)}건")
            for c in flog[:8]:
                print(f"   {c['old']!r:22s} → {c['new']!r}" + (f"  detail={c['detail']!r}" if c["detail"] else ""))
            if a.apply and flog:
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump(d, fh, ensure_ascii=False, indent=1)
                log["files"][os.path.basename(f)] = "written"

    if a.apply:
        os.makedirs(LOG_DIR, exist_ok=True)
        lp = os.path.join(LOG_DIR, f"region_backfill_{ts}.json")
        json.dump(log, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n[로그] {lp}")
    else:
        print("\n[dry-run] 쓰기 없음. 반영하려면 --apply")


if __name__ == "__main__":
    main()