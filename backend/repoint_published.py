#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repoint path-like guide references in the PUBLISHED tables (consulting_db.json, data.js).

`sync_3layer.py` is fill-only, so a dead path already stored in consulting_db.json is never
overwritten by the KB fix — it has to be corrected here. Same resolver as
repoint_guide_paths.py (exact basename → school+year → school+any).

  python repoint_published.py            # report only
  python repoint_published.py --apply    # rewrite consulting_db.json + data.js
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
from repoint_guide_paths import REF, build_index, manifest_entries, resolve  # noqa: E402

CONSULTING = pp.PUBLISHED["consulting_db"]
DATA_JS = pp.PUBLISHED["data_js"]


def repoint_tree(node, by_name, by_school_year, apply: bool, changed: list, unresolved: list):
    if isinstance(node, dict):
        for key in list(node.keys()):
            item = node[key]
            if isinstance(item, str):
                if key.endswith("_note") or not REF.search(item) or item.startswith("http"):
                    continue
                if os.path.isfile(item):
                    continue
                new, how = resolve(item, by_name, by_school_year)
                rec = {"field": key, "old": item, "new": new, "how": how}
                if new:
                    changed.append(rec)
                    if apply:
                        node[key] = new
                else:
                    unresolved.append(rec)
            else:
                repoint_tree(item, by_name, by_school_year, apply, changed, unresolved)
    elif isinstance(node, list):
        for item in node:
            repoint_tree(item, by_name, by_school_year, apply, changed, unresolved)


def repoint_datajs(by_name, by_school_year, apply: bool):
    text = DATA_JS.read_text(encoding="utf-8")
    changed, unresolved = [], []
    pattern = re.compile(r'"(?![^"]*https?://)([^"\n]*?\.(?:pdf|hwp))"', re.I)

    def swap(m):
        value = m.group(1)
        if os.path.isfile(value):
            return m.group(0)
        new, how = resolve(value, by_name, by_school_year)
        if new:
            changed.append({"field": "data.js", "old": value, "new": new, "how": how})
            return '"' + new.replace("\\", "\\\\") + '"'
        unresolved.append({"field": "data.js", "old": value, "new": None, "how": "unresolved"})
        return m.group(0)

    new_text = pattern.sub(swap, text)
    if apply and changed:
        backup = DATA_JS.with_name(f"data.js.bak_repoint_{dt.datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy2(DATA_JS, backup)
        DATA_JS.write_text(new_text, encoding="utf-8")
        print(f"  data.js backup -> {backup.name}")
    return changed, unresolved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    entries = manifest_entries()
    if not entries:
        print("no library manifest — run guide_library.py --apply first")
        return 2
    by_name, by_school_year = build_index(entries)

    c_changed, c_unres = [], []
    cdb = json.loads(CONSULTING.read_text(encoding="utf-8"))
    repoint_tree(cdb, by_name, by_school_year, args.apply, c_changed, c_unres)
    if args.apply and c_changed:
        backup = CONSULTING.with_name(f"consulting_db_bak_repoint_{dt.datetime.now():%Y%m%d_%H%M%S}.json")
        shutil.copy2(CONSULTING, backup)
        tmp = CONSULTING.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(cdb, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, CONSULTING)
        print(f"  consulting_db backup -> {backup.name}")

    d_changed, d_unres = repoint_datajs(by_name, by_school_year, args.apply)

    print(json.dumps({"consulting_db": {"repointable": len(c_changed), "unresolved": len(c_unres)},
                      "data_js": {"repointable": len(d_changed), "unresolved": len(d_unres)},
                      "applied": args.apply}, ensure_ascii=False, indent=2))
    for rec in (c_changed + d_changed)[:8]:
        print(f"  {rec['field']}: {rec['old'][:60]} -> {Path(rec['new']).name} [{rec['how']}]")
    for rec in (c_unres + d_unres)[:6]:
        print(f"  UNRESOLVED {rec['old'][:80]}")
    if not args.apply:
        print("\nREPORT ONLY (pass --apply to rewrite consulting_db.json + data.js)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())