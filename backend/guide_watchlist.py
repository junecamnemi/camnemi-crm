#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Current-year policy: only the CURRENT guide year is the working set.

For every school we track (KB universe) plus every school the library holds:
- `current`   — current-year guide in the library (the working set)
- `watch`     — older guide only, URL is monitored; the daily detector records the
                school the moment its page shows the current year and the download
                stage then fetches the real PDF
- `needs_url` — older guide but no usable URL (URL-discovery target)
- `no_guide`  — no guide at all in the library

Writes `_pipeline_data/reports/_<year>_watchlist.json` (ONE data home) and prints a
compact summary. Read-only: never downloads, never edits the KB.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline_paths as pp  # noqa: E402
import school_keys as sk  # noqa: E402

BACKEND = pp.BACKEND
KB = BACKEND / "verified_kb.json"
PAGE_JSONS = ["_guide_pages.json", "_junior_guide_pages.json", "_lang_guide_pages.json"]
JUNK_URL = re.compile(r"accounts\.google|youtube\.com|signin|javascript:|^about:", re.I)
JUNK_SCHOOL = re.compile(r"^(gks|_|[0-9]+$)", re.I)


def _norm(v: str) -> str:
    return re.sub(r"[\s\[\]()._\-]", "", (v or "")).lower()


_EXTRA_INDEX: dict[str, str] | None = None


def extra_index() -> dict[str, str]:
    """Junior colleges are absent from school_keys; index them from the adiga junior
    list plus the KB junior/master/lang sections so their files still map to a school."""
    global _EXTRA_INDEX
    if _EXTRA_INDEX is not None:
        return _EXTRA_INDEX
    idx: dict[str, str] = {}
    jl = BACKEND / "_adiga_junior_list.json"
    if jl.is_file():
        try:
            for name in json.loads(jl.read_text(encoding="utf-8")).values():
                idx.setdefault(_norm(name), name)
        except Exception:
            pass
    try:
        kb = json.loads(KB.read_text(encoding="utf-8"))
    except Exception:
        kb = {}
    for sec, sub in [("junior", "schools"), ("lang_programs", "schools"), ("master", "schools")]:
        for name in (kb.get(sec, {}) or {}).get(sub, {}):
            idx.setdefault(_norm(name), name)
    _EXTRA_INDEX = idx
    return idx


def match_extra(probe: str) -> str | None:
    idx = extra_index()
    hit = idx.get(_norm(probe))
    if hit:
        return hit
    key = _norm(probe)
    if len(key) < 4:
        return None
    for k, name in idx.items():
        if k.startswith(key) or key.startswith(k):
            return name
    return None


def school_of(name: str) -> str | None:
    """Filename -> canonical adiga school key (None when it is not a school guide)."""
    stem = re.sub(r"\.[a-z]{2,4}$", "", (name or "").strip(), flags=re.I)
    stem = re.sub(r"^\d{6,8}_", "", stem)
    parts = [p for p in re.split(r"[_\[\]()]+", stem) if p]
    for take in range(1, min(4, len(parts)) + 1):
        for probe in (" ".join(parts[:take]), parts[0]):
            if JUNK_SCHOOL.search(probe) or len(probe) < 3:
                continue
            for fn in (sk.resolve, sk.resolve_short):
                try:
                    hit = fn(probe)
                except Exception:
                    hit = None
                if hit:
                    return hit
            hit = match_extra(probe)
            if hit:
                return hit
    return None


def unreadable_names() -> set[str]:
    """Filenames flagged by `guide_library.py --validate` (0-page / corrupt PDFs).

    A broken file must not count as the school's current-year guide, otherwise the school
    looks covered while its guide cannot be parsed (2026-09-29).
    """
    rep = pp.REPORT_DIR / "_invalid_pdfs.json"
    if not rep.is_file():
        return set()
    try:
        data = json.loads(rep.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {b.get("name", "") for b in data.get("unreadable", [])}


def library_state() -> tuple[set[str], set[str], int]:
    """(schools with a guide, schools by year, unmatched file count)."""
    manifest = pp.library_manifest()
    entries = []
    if manifest.is_file():
        try:
            entries = json.loads(manifest.read_text(encoding="utf-8")).get("entries", [])
        except Exception:
            entries = []
    broken = unreadable_names()
    by_year: dict[str, set[str]] = collections.defaultdict(set)
    unmatched = 0
    skipped_broken = 0
    for e in entries:
        if e.get("name", "") in broken:
            skipped_broken += 1
            continue
        school = school_of(e.get("name", ""))
        if not school:
            unmatched += 1
            continue
        by_year[e.get("year", "")].add(school)
    if skipped_broken:
        print(f"note: {skipped_broken} unreadable PDF(s) excluded from current coverage (see _invalid_pdfs.json)")
    return by_year, unmatched


def unmapped_entries(year: str) -> list[str]:
    """Library files whose name carries no resolvable school (naming hygiene list)."""
    manifest = pp.library_manifest()
    if not manifest.is_file():
        return []
    try:
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("entries", [])
    except Exception:
        return []
    return sorted(e.get("name", "") for e in entries
                  if e.get("year") == year and not school_of(e.get("name", "")))


def load_page_urls() -> dict[str, dict]:
    urls: dict[str, dict] = {}
    for name in PAGE_JSONS:
        path = BACKEND / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        level = "junior" if "junior" in name else ("lang" if "lang" in name else "ba")
        for school, entry in data.items():
            url = None
            if isinstance(entry, dict):
                url = entry.get("guide_page_url") or entry.get("url") or entry.get("page_url")
            if isinstance(url, str) and url.startswith("http"):
                key = sk.resolve(school) or sk.resolve_short(school) or school
                urls.setdefault(key, {"level": level, "page_url": url, "source": name})
    try:
        kb = json.loads(KB.read_text(encoding="utf-8"))
    except Exception:
        kb = {}
    for sec, sub, level in [("schools", None, "ba"), ("master", "schools", "ma"),
                            ("junior", "schools", "junior"), ("lang_programs", "schools", "lang")]:
        try:
            block = kb[sec][sub] if sub else kb[sec]
        except Exception:
            continue
        for school, entry in block.items():
            url = entry.get("guide_page_url") if isinstance(entry, dict) else None
            if isinstance(url, str) and url.startswith("http"):
                key = sk.resolve(school) or sk.resolve_short(school) or school
                urls.setdefault(key, {"level": level, "page_url": url, "source": "verified_kb"})
    return urls


def kb_schools() -> dict[str, str]:
    """canonical school -> level, from verified_kb (the recommendation universe)."""
    out: dict[str, str] = {}
    try:
        kb = json.loads(KB.read_text(encoding="utf-8"))
    except Exception:
        return out
    for sec, sub, level in [("schools", None, "ba"), ("master", "schools", "ma"),
                            ("junior", "schools", "junior"), ("lang_programs", "schools", "lang")]:
        try:
            block = kb[sec][sub] if sub else kb[sec]
        except Exception:
            continue
        for school in block:
            key = sk.resolve(school) or sk.resolve_short(school) or school
            out.setdefault(key, level)
    return out


def build(year: str) -> dict:
    by_year, unmatched = library_state()
    current, older = by_year.get(year, set()), set()
    for y, schools in by_year.items():
        if y and y < year:
            older |= schools
    urls = load_page_urls()
    kbmap = kb_schools()
    universe = sorted(set(kbmap) | current | older)
    rows = []
    for school in universe:
        info = urls.get(school, {})
        url = info.get("page_url", "")
        if school in current:
            status = "current"
        elif school in older:
            status = "watch" if url and not JUNK_URL.search(url) else "needs_url"
        elif url:
            status = "watch"
        else:
            status = "no_guide"
        rows.append({"school": school, "level": kbmap.get(school) or info.get("level", ""),
                     "status": status, "page_url": url, "url_source": info.get("source", ""),
                     "has_current": school in current, "has_older": school in older})
    counts = collections.Counter(r["status"] for r in rows)
    payload = {
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "current_year": year,
        "policy": "current-year guide = working set; older years archive-only and their URLs stay watched",
        "counts": dict(counts),
        "total_schools": len(rows),
        "library_years": {y: len(v) for y, v in sorted(by_year.items())},
        "library_files_unmatched_to_school": unmatched,
        "unmapped_current_files": unmapped_entries(year),
        "needs_url": [r["school"] for r in rows if r["status"] == "needs_url"],
        "watch": [r["school"] for r in rows if r["status"] == "watch"],
        "rows": rows,
    }
    pp.scaffold()
    out = pp.REPORT_DIR / f"_{year}_watchlist.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, out)
    kb_rows = [r for r in rows if r["school"] in kbmap]
    kb_counts = collections.Counter(r["status"] for r in kb_rows)
    print(f"[all] current({year})={counts.get('current',0)} | watch={counts.get('watch',0)} | "
          f"needs_url={counts.get('needs_url',0)} | no_guide={counts.get('no_guide',0)} | total={len(rows)}")
    print(f"[KB universe] current={kb_counts.get('current',0)} | watch={kb_counts.get('watch',0)} | "
          f"needs_url={kb_counts.get('needs_url',0)} | no_guide={kb_counts.get('no_guide',0)} | total={len(kb_rows)}")
    print(f"library year sets: {payload['library_years']} | files not mapped to a school: {unmatched}")
    print(f"current-year files with no resolvable school name: {len(payload['unmapped_current_files'])} "
          f"(naming hygiene, e.g. {', '.join(payload['unmapped_current_files'][:4])})")
    print(f"watchlist -> {out}")
    if payload["needs_url"]:
        print("needs_url (first 10):", ", ".join(payload["needs_url"][:10]))
    return payload


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default="2027")
    args = ap.parse_args()
    build(args.year)