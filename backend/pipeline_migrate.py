#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move the pipeline's accumulating artifacts into the ONE data home
(`backend/_pipeline_data/`) and hard-link the legacy paths to the same inode.

Safe by construction: originals are copied to `_pipeline_data/_legacy_backup/`
first, nothing is deleted, and every link is verified by inode + md5.

Usage: python pipeline_migrate.py [--apply] [--verify]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil

import pipeline_paths as pp


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def migrate(dry_run: bool) -> list[dict]:
    pp.scaffold()
    pp.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    for name, (canonical, legacy) in pp.ARTIFACTS.items():
        rec = {"artifact": name, "canonical": str(canonical), "legacy": str(legacy), "action": None}
        has_c, has_l = canonical.exists(), legacy.exists()
        if not has_c and not has_l:
            rec["action"] = "absent"
            results.append(rec)
            continue
        if has_c and has_l:
            same_inode = canonical.stat().st_ino == legacy.stat().st_ino
            same_bytes = md5(canonical) == md5(legacy)
            if same_inode or same_bytes:
                if not same_inode and not dry_run:
                    backup = pp.BACKUP_DIR / f"{dt.datetime.now():%Y%m%d_%H%M%S}_{legacy.name}"
                    shutil.copy2(legacy, backup)
                    legacy.unlink()
                    os.link(canonical, legacy)
                rec["action"] = "already-home" if same_inode else "relinked"
            else:
                backup = pp.BACKUP_DIR / f"{dt.datetime.now():%Y%m%d_%H%M%S}_{legacy.name}"
                if not dry_run:
                    shutil.copy2(legacy, backup)
                rec["action"] = "CONFLICT_legacy_backed_up"
                rec["backup"] = str(backup)
        elif has_l:
            backup = pp.BACKUP_DIR / f"{dt.datetime.now():%Y%m%d_%H%M%S}_{legacy.name}"
            if not dry_run:
                shutil.copy2(legacy, backup)
                canonical.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(legacy), str(canonical))
                os.link(canonical, legacy)
            rec["action"] = ("moved+linked" if not dry_run else "would-move+link")
            rec["backup"] = str(backup)
        else:
            if not dry_run:
                os.link(canonical, legacy)
            rec["action"] = "linked-missing-legacy"
        if canonical.exists() and legacy.exists():
            rec["linked"] = canonical.stat().st_ino == legacy.stat().st_ino
            rec["bytes"] = canonical.stat().st_size
        results.append(rec)
    return results


def verify() -> int:
    bad = []
    for name, (canonical, legacy) in pp.ARTIFACTS.items():
        if not canonical.exists():
            bad.append(f"{name}: canonical missing {canonical}")
            continue
        if not legacy.exists():
            bad.append(f"{name}: legacy path missing {legacy}")
            continue
        if canonical.stat().st_ino != legacy.stat().st_ino:
            bad.append(f"{name}: NOT linked (different inode)")
        elif md5(canonical) != md5(legacy):
            bad.append(f"{name}: link but content differs?!")
    print("LINK VERIFY:", "all artifacts linked to the data home" if not bad else "PROBLEMS")
    for b in bad:
        print("  -", b)
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="perform the migration")
    ap.add_argument("--verify", action="store_true", help="verify links only")
    args = ap.parse_args()
    if args.verify:
        return verify()
    results = migrate(dry_run=not args.apply)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if args.apply:
        idx = pp.build_index({"migration": {"at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
                                            "results": results}})
        print(f"\nINDEX -> {pp.INDEX_FILE}")
        return verify()
    print("\nDRY RUN (pass --apply to migrate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())