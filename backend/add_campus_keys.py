#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""add_campus_keys.py — 이름이 다른 캠퍼스(분교)를 KEY 레지스트리에 편입.

June's rule (2026-09-29): 본교만 대상이지만 **이름이 다른** 캠퍼스는 별개 학교다
(한양대학교(ERICA), 건국대학교(글로컬), 고려대학교(세종), 동국대학교(WISE), 연세대학교(미래)).
`[제2/3/4캠퍼스]` 처럼 이름이 같은 캠퍼스는 편입하지 않는다.

기존 레지스트리 항목은 건드리지 않고 새 항목만 추가한다(가이드 경로는
repoint_key_registry.py 가 이어서 해석).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sqlite3
import sys

B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import pipeline_paths as pp  # noqa: E402

REGISTRY = os.path.join(B, "unvcd_index.json")
DB = os.path.join(B, "_acdmcp", "package", "data", "seed", "academyinfo_15118998.sqlite")
GENERIC = re.compile(r"^\[?제\s*\d\s*캠퍼스\]?$")


def campus_tag(name: str) -> str:
    m = re.search(r"[\[(]([^\])]+)[\])]", name or "")
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    univ = json.loads(open(os.path.join(B, "_adiga_univ_list.json"), encoding="utf-8").read())
    jun = json.loads(open(os.path.join(B, "_adiga_junior_list.json"), encoding="utf-8").read())
    basic = json.loads(open(os.path.join(B, "_adiga_basic_urls.json"), encoding="utf-8").read())
    reg = json.loads(open(REGISTRY, encoding="utf-8").read())
    schools = reg["schools"]

    con = sqlite3.connect(DB)
    cur = con.cursor()

    def stats_for(full_name: str):
        """academyinfo stats by exact school_name (named campuses are separate rows)."""
        base = re.sub(r"[\[(][^\])]+[\])]", "", full_name).strip()
        tag = campus_tag(full_name)
        probe = f"{base}({tag})" if tag and not GENERIC.match("[" + tag + "]") else base
        cur.execute("""SELECT i.school_name, max(CASE WHEN o.indicator_id='enrolled_students' THEN o.value END),
                              max(CASE WHEN o.indicator_id='international_students' THEN o.value END)
                       FROM institutions i LEFT JOIN observations o ON o.institution_id=i.id AND o.year=2025
                       WHERE i.school_name = ? GROUP BY i.id""", (probe,))
        row = cur.fetchone()
        if row and (row[1] is not None or row[2] is not None):
            return {"enrolled_2025": row[1], "international_2025": row[2], "year": 2025}, probe
        return None, probe

    added = []
    for code, name in {**univ, **jun}.items():
        if "[본교]" in name or code in schools:
            continue
        tag = campus_tag(name)
        if not tag or GENERIC.match("[" + tag + "]"):
            continue  # same-name campus -> not a separate key
        st, probe = stats_for(name)
        b = basic.get(code, {})
        schools[code] = {
            "name": re.sub(r"\[[^\]]+\]$", "", name).strip(),
            "unvCd": code,
            "school_type": "junior" if code in jun else "univ4",
            "homepage": b.get("homepage"),
            "ipsi_homepage": b.get("ipsi_homepage"),
            "addr": b.get("addr"),
            "tel": b.get("tel"),
            "stats": st or {},
            "excluded": None,
            "campus_of": probe if st else None,
            "note": "named campus included as its own key (June's rule: 이름이 다른 캠퍼스)",
        }
        added.append((code, schools[code]["name"], st is not None))

    print(f"named-campus keys added: {len(added)}")
    for c, n, has in added:
        print(f"   {c} {n:34s} stats={'yes' if has else 'NONE'}")
    if args.apply:
        backup = os.path.join(B, f"unvcd_index_bak_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
        open(backup, "w", encoding="utf-8").write(open(REGISTRY, encoding="utf-8").read())
        reg["meta"]["campus_keys_added"] = [c for c, _, _ in added]
        reg["count"] = {"univ4": sum(1 for v in schools.values() if v.get("school_type") == "univ4"),
                        "junior": sum(1 for v in schools.values() if v.get("school_type") == "junior")}
        tmp = REGISTRY + ".tmp"
        open(tmp, "w", encoding="utf-8").write(json.dumps(reg, ensure_ascii=False, indent=1))
        os.replace(tmp, REGISTRY)
        print(f"APPLIED (backup {os.path.basename(backup)}) | keys now {len(schools)}")
    else:
        print("report-only (use --apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())