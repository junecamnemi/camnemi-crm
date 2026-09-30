#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Effective-guide resolver: **2027 if it exists, otherwise the newest year we hold (2026)**.

The KB keeps 2026 facts for schools whose 2027 guide is not published yet, so the fallback
has to be explicit and visible — otherwise a student cannot tell whether the requirements
shown come from the 2027 guide or last year's.

For every school/level in verified_kb this fills (additive, fill-only):
  guide_effective_year  - 2027 when available, else the newest archived year
  guide_effective_pdf   - the real library file for that year
  guide_effective_note  - set when the year is not the current one (URL stays watched)

It also repairs `guide_pdf` values that hold descriptive text instead of a path
(e.g. "… 특별전형 모집요강 PDF (gachon.ac.kr/…) → PDF 저장"): the text moves to
`guide_pdf_note` and the real file path goes into `guide_pdf`.

  python guide_resolve.py            # report only
  python guide_resolve.py --apply    # write KB (backup + read-back verify)
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as pp  # noqa: E402
from guide_watchlist import school_of  # noqa: E402

KB = pp.PUBLISHED["verified_kb"]
CURRENT = "2027"
SECTIONS = [("schools", None, "ba"), ("master", "schools", "ma"),
            ("junior", "schools", "junior"), ("lang_programs", "schools", "lang")]


def library_index() -> dict[tuple[str, str], dict[str, dict]]:
    """(school, level) -> {year: best entry}"""
    manifest = pp.library_manifest()
    if not manifest.is_file():
        return {}
    entries = json.loads(manifest.read_text(encoding="utf-8")).get("entries", [])
    out: dict[tuple[str, str], dict[str, dict]] = collections.defaultdict(dict)

    def rank(e: dict) -> tuple:
        name = e.get("name", "")
        return (0 if "[본교]" in name else 1, 0 if "외국인" in name else 1, len(name))

    for e in entries:
        school = school_of(e.get("name", ""))
        if not school:
            continue
        key = (school, e.get("level", ""))
        year = e.get("year", "")
        best = out[key].get(year)
        if best is None or rank(e) < rank(best):
            out[key][year] = e
    return out


def is_path_like(value: str) -> bool:
    return bool(value) and bool(re.search(r"\.(pdf|hwp)$", value.strip(), re.I)) and (
        os.path.isfile(value) or re.match(r"^[A-Za-z]:[\\/]|^[\\/]", value.strip()))


def resolve_years(held: dict[str, dict]) -> tuple[str | None, dict | None]:
    if CURRENT in held:
        return CURRENT, held[CURRENT]
    older = sorted((y for y in held if y and y.isdigit() and y < CURRENT), reverse=True)
    if older:
        return older[0], held[older[0]]
    unknown = held.get("unknown")
    return ("unknown", unknown) if unknown else (None, None)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    lib = library_index()
    kb = json.loads(KB.read_text(encoding="utf-8"))
    stats = collections.Counter()
    per_level = collections.Counter()
    fixes: list[dict] = []

    for section, sub, level in SECTIONS:
        block = kb.get(section, {})
        if sub:
            block = block.get(sub, {}) if isinstance(block, dict) else {}
        for school, entry in block.items():
            if not isinstance(entry, dict):
                continue
            key_school = school_of(school) or school
            held = lib.get((key_school, level), {})
            year, hit = resolve_years(held)
            path = (hit or {}).get("library_path") or (hit or {}).get("path")
            stats["schools"] += 1
            if year is None:
                stats["no_guide"] += 1
                per_level[f"{level}:none"] += 1
                continue
            if year == CURRENT:
                stats["current"] += 1
                per_level[f"{level}:{CURRENT}"] += 1
            else:
                stats["fallback"] += 1
                per_level[f"{level}:{year}"] += 1
            if args.apply:
                entry["guide_effective_year"] = year
                entry["guide_effective_pdf"] = path
                if year != CURRENT:
                    entry["guide_effective_note"] = (
                        f"{CURRENT} 모집요강 미공개 — {year} 요강 기준 정보. "
                        f"공개 시 URL 감시 후 자동 수집 대상.")
                else:
                    entry.pop("guide_effective_note", None)
            # repair a guide_pdf that is descriptive text rather than a path
            gpdf = entry.get("guide_pdf")
            if isinstance(gpdf, str) and gpdf and not is_path_like(gpdf) and path:
                fixes.append({"school": school, "level": level, "old": gpdf[:70], "new": Path(path).name})
                if args.apply:
                    entry["guide_pdf"] = path
                    if not isinstance(entry.get("guide_pdf_note"), str):
                        entry["guide_pdf_note"] = gpdf[:300]

    print(json.dumps({"schools_checked": stats["schools"],
                      f"effective_{CURRENT}": stats["current"],
                      "effective_fallback_older": stats["fallback"],
                      "no_guide_any_year": stats["no_guide"],
                      "descriptive_guide_pdf_repaired": len(fixes),
                      "by_level": dict(sorted(per_level.items()))},
                     ensure_ascii=False, indent=2))
    for rec in fixes[:8]:
        print(f"  FIX {rec['school']} [{rec['level']}]: {rec['old']}… -> {rec['new']}")
    if not args.apply:
        print("\nREPORT ONLY (pass --apply to write verified_kb.json)")
        return 0
    backup = KB.with_name(f"verified_kb_bak_effective_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
    shutil.copy2(KB, backup)
    tmp = KB.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(kb, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, KB)
    back = json.loads(KB.read_text(encoding="utf-8"))
    ok = sum(1 for section, sub, _ in SECTIONS
             for e in ((back.get(section, {}).get(sub, {}) if sub else back.get(section, {})) or {}).values()
             if isinstance(e, dict) and e.get("guide_effective_year"))
    print(f"\nAPPLIED (backup {backup.name}) | schools with an explicit effective guide: {ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())