#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repoint every path-like guide reference in verified_kb.json to the single library.

Covers `guide_pdf`, `source`, `guide_2027_source` and any other string field, because the
old host paths (`C:/Users/wisew/...`), the stale `~/내 드라이브` mirror and the retired
scatter folders all leave dead references behind. Resolution: exact basename first, then
school+year (preferring [본교] + 외국인), then any year for that school. Trailing
annotations ("(adiga 0000113)") are preserved into `<field>_note`.

  python repoint_guide_paths.py            # report only
  python repoint_guide_paths.py --apply    # rewrite KB (backup + read-back verify)
"""
from __future__ import annotations

import argparse
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

KB = pp.BACKEND / "verified_kb.json"
REF = re.compile(r"\.(pdf|hwp)\b", re.I)
SKIP_FIELDS = {"guide_url", "page_url", "url", "apply_url"}


def manifest_entries() -> list[dict]:
    path = pp.library_manifest()
    if not path.is_file():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("entries", [])
    except Exception:
        return []


def build_index(entries: list[dict]):
    by_name: dict[str, dict] = {}
    groups: dict[tuple[str, str], list[dict]] = {}
    for e in entries:
        e["library_path"] = e.get("library_path") or e.get("path", "")
        by_name.setdefault(e.get("name", ""), e)
        school = school_of(e.get("name", ""))
        if school:
            groups.setdefault((school, e.get("year", "")), []).append(e)

    def rank(e: dict) -> tuple:
        name = e.get("name", "")
        return (0 if "[본교]" in name else 1,
                0 if "외국인" in name else 1,
                len(name))

    by_school_year = {k: sorted(v, key=rank)[0] for k, v in groups.items()}
    return by_name, by_school_year


def ref_token(value: str) -> str | None:
    """The path/filename part of a possibly annotated value."""
    v = value.strip()
    if not REF.search(v) or v.startswith("http"):
        return None
    cut = re.split(r"\s+\(|\s+→|\s+;", v)[0].strip().strip('"')
    return cut or None


def candidate_basenames(value: str) -> list[str]:
    """Every plausible filename inside a value, including ones inside annotations
    (e.g. '2026학년도 전기 … 모집요강 PDF(초당대_대학원_모집요강.pdf) → PDF 저장')."""
    out: list[str] = []
    token = ref_token(value)
    if token:
        out.append(re.split(r"[\\/]", token)[-1])
    for m in re.finditer(r"[^\s\\/()\[\],;]+?\.(?:pdf|hwp)\b", value, re.I):
        name = m.group(0).strip()
        if name and name not in out:
            out.append(name)
    return out


def resolve(value: str, by_name, by_school_year) -> tuple[str | None, str]:
    for base in candidate_basenames(value):
        if base in by_name:
            return by_name[base]["library_path"], "exact-filename"
        school = school_of(base)
        if not school:
            continue
        for year in re.findall(r"(20\d\d)", base) + ["2027", "2026"]:
            hit = by_school_year.get((school, year))
            if hit:
                return hit["library_path"], f"school+year({year})"
        for (s, y), hit in sorted(by_school_year.items(), reverse=True):
            if s == school:
                return hit["library_path"], f"school+any({y})"
    return None, "unresolved"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    entries = manifest_entries()
    if not entries:
        print("no library manifest — run guide_library.py --apply first")
        return 2
    by_name, by_school_year = build_index(entries)
    kb = json.loads(KB.read_text(encoding="utf-8"))
    stats = {"repointed": 0, "already_ok": 0, "unresolved": 0, "notes_preserved": 0}
    changed: list[dict] = []
    unresolved: list[dict] = []

    def visit(node, path):
        if isinstance(node, dict):
            for key in list(node.keys()):
                item = node[key]
                if isinstance(item, str):
                    if (key in SKIP_FIELDS or key.endswith("_note")
                            or not REF.search(item) or item.startswith("http")):
                        continue
                    if os.path.isfile(item) and str(pp.library_root()) in item:
                        stats["already_ok"] += 1
                        continue
                    new, how = resolve(item, by_name, by_school_year)
                    if not new:
                        stats["unresolved"] += 1
                        unresolved.append({"field": f"{path}.{key}", "value": item[:110]})
                        continue
                    stats["repointed"] += 1
                    changed.append({"field": f"{path}.{key}", "old": item, "new": new, "how": how})
                    if args.apply:
                        note = item[len(ref_token(item)):].strip()
                        node[key] = new
                        if note and not isinstance(node.get(f"{key}_note"), str):
                            node[f"{key}_note"] = note
                            stats["notes_preserved"] += 1
                else:
                    visit(item, f"{path}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                visit(item, f"{path}[{i}]")

    visit(kb, "")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if not args.quiet:
        for rec in changed[:10]:
            print(f"  {rec['field']}: {rec['old'][:60]} -> {Path(rec['new']).name} [{rec['how']}]")
        for rec in unresolved[:8]:
            print(f"  UNRESOLVED {rec['field']}: {rec['value'][:80]}")
    if not args.apply:
        print("\nREPORT ONLY (pass --apply to rewrite verified_kb.json)")
        return 0
    backup = KB.with_name(f"verified_kb_bak_repoint_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
    shutil.copy2(KB, backup)
    tmp = KB.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(kb, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, KB)
    back = json.loads(KB.read_text(encoding="utf-8"))
    ok = 0

    def verify(node):
        nonlocal ok
        if isinstance(node, dict):
            for _, v in node.items():
                verify(v)
        elif isinstance(node, list):
            for v in node:
                verify(v)
        elif isinstance(node, str) and REF.search(node) and not node.startswith("http"):
            if os.path.isfile(node) and str(pp.library_root()) in node:
                ok += 1

    verify(back)
    print(f"\nAPPLIED to {KB} (backup {backup.name}) | library refs resolving on disk now: {ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())