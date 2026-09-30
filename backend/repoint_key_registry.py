#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""repoint_key_registry.py — unvcd_index.json 의 모집요강 경로를 단일 라이브러리로 재지정.

unvcd_index.json = 사용자 정의 KEY 레지스트리:
  key = adiga unvCd (본교만) → name / school_type / homepage / ipsi_homepage / addr / tel
      + stats(enrolled_2025, international_2025, 대학알리미) + foreign_guides_*

수집 당시 경로는 은퇴한 스토어(`C:\\Users\\wisew\\내 드라이브\\...`)를 가리켜 전부 죽은 링크다.
여기서 단일 라이브러리 파일로 재지정하고, 외국인 전형만 남기며(재외국민 제거),
현재연도(2027) 보유 여부를 `guide_2027`/`guide_status` 로 명시한다.

기본은 report-only. `--apply` 로 저장(백업 생성).
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as pp  # noqa: E402

BACKEND = Path(pp.BACKEND)
REGISTRY = BACKEND / "unvcd_index.json"
CURRENT = "2027"
LEVELS_4YR = ("ba", "ma")
LEVELS_JR = ("junior",)
KEEP_FOREIGN_ONLY = True


def norm(s: str) -> str:
    return re.sub(r"[\s\[\]()._\-·]", "", (s or "")).lower()


def base_name(nm: str) -> str:
    return re.sub(r"\[[^\]]+\]$", "", (nm or "").strip())


def build_library_index():
    """(by_code, by_name) -> {code/name: {level: {'2027': path, ...}}} from the manifest."""
    by_code: dict[str, dict] = collections.defaultdict(dict)
    by_name: dict[str, dict] = collections.defaultdict(dict)
    man = pp.library_manifest()
    entries = json.loads(man.read_text(encoding="utf-8")).get("entries", []) if man.is_file() else []
    for e in entries:
        if e.get("archived"):
            continue
        name = e.get("name", "")
        path = e.get("library_path") or e.get("path") or ""
        year = str(e.get("year") or "")
        level = e.get("level") or ""
        m = re.match(r"^(\d{6,7})_", name)
        if m:
            by_code[m.group(1)].setdefault(level, {}).setdefault(year, path)
        stem = re.sub(r"^(\d{6,7})_", "", re.sub(r"\.pdf$", "", name, flags=re.I))
        for probe in {norm(base_name(stem)), norm(stem.split("_")[0])}:
            if probe:
                by_name[probe].setdefault(level, {}).setdefault(year, path)
    return by_code, by_name


def resolve(entry, by_code, by_name):
    """(path, level, year, how) for the school's current foreign guide, or (None, ...)."""
    code = str(entry.get("unvCd") or "")
    levels = LEVELS_JR if entry.get("school_type") == "junior" else LEVELS_4YR
    for level in levels:
        hit = (by_code.get(code) or {}).get(level, {}).get(CURRENT)
        if hit:
            return hit, level, CURRENT, "code"
    for probe in {norm(base_name(entry.get("name", "")))}:
        for level in levels:
            hit = (by_name.get(probe) or {}).get(level, {}).get(CURRENT)
            if hit:
                return hit, level, CURRENT, "name"
    # any year held -> the school is on the watch list rather than covered
    for src, table in (("code", by_code.get(code) or {}),):
        for level in levels:
            years = table.get(level) or {}
            if years:
                y = sorted(years)[-1]
                return years[y], level, y, "code-older"
    for level in levels:
        years = (by_name.get(norm(base_name(entry.get("name", "")))) or {}).get(level) or {}
        if years:
            y = sorted(years)[-1]
            return years[y], level, y, "name-older"
    return None, "", "", "none"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    schools = reg["schools"]
    by_code, by_name = build_library_index()

    how = collections.Counter()
    status = collections.Counter()
    dropped_jaewoe = 0
    for code, e in schools.items():
        path, level, year, method = resolve(e, by_code, by_name)
        how[method] += 1
        if path and year == CURRENT:
            e["guide_2027"] = path
            e["guide_2027_level"] = level
            e["guide_status"] = "current"
            status["current"] += 1
        elif path:
            e["guide_2027"] = None
            e["guide_last_pdf"] = path
            e["guide_last_year"] = year
            e["guide_status"] = "watch"
            status["watch"] += 1
        else:
            e["guide_2027"] = None
            e["guide_status"] = "needs_url"
            status["needs_url"] += 1

        # 외국인 전형만 남긴다 (재외국민 제거) + 죽은 경로는 라이브러리 파일로 교체
        fg = e.get("foreign_guides_4yr")
        if isinstance(fg, dict):
            kept = {}
            for k, v in fg.items():
                if KEEP_FOREIGN_ONLY and "재외국민" in k:
                    dropped_jaewoe += 1
                    continue
                if isinstance(v, str) and not Path(v).is_file():
                    kept[k] = e.get("guide_2027") if "외국인" in k else None
                    if kept[k] is None:
                        kept.pop(k)
                else:
                    kept[k] = v
            e["foreign_guides_4yr"] = kept

    reg["meta"]["registry_updated"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    reg["meta"]["guide_resolution"] = {"current_year": CURRENT, "by_code": how.get("code", 0),
                                       "by_name": how.get("name", 0),
                                       "older_year_held": how.get("code-older", 0) + how.get("name-older", 0),
                                       "no_guide": how.get("none", 0)}

    if not args.quiet:
        print(f"registry keys: {len(schools)} | guide status: {dict(status)}")
        print(f"resolution: {reg['meta']['guide_resolution']}")
        print(f"재외국민 links dropped: {dropped_jaewoe}")
        miss = [f"{c}:{e['name']}" for c, e in schools.items() if e.get("guide_status") == "needs_url"]
        print(f"needs_url ({len(miss)}): {', '.join(miss[:8])}")

    if args.apply:
        backup = REGISTRY.with_name(f"unvcd_index_bak_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
        backup.write_text(REGISTRY.read_text(encoding="utf-8"), encoding="utf-8")
        tmp = REGISTRY.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, REGISTRY)
        print(f"APPLIED (backup {backup.name})")
    else:
        print("report-only (use --apply to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())