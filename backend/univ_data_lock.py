#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONE shared single-writer lock for every Camnemi university-data entry point.

University data is a single chain — collect → detect/download → parse → merge → KB →
consulting DB/data.js → canonical → Supabase — but it used to be driven by three separate
cron jobs, each with its OWN lock name (`camnemi_guides`, `camnemi_pipeline`) plus the
pipeline's private lock file. Different lock names never intersect, so the 04:00 pipeline
could still be inside its multi-hour parse stage while the 06:00 collector and the 08:00
canonical publisher wrote the same verified_kb.json / consulting_db.json / guide library.

This module gives all of them the SAME lock: whoever holds it owns the university data for
that window; a second runner is refused (exit 9) instead of interleaving writes.

Usage:
    from univ_data_lock import acquire, release
    acquire()                 # raises SystemExit(9) when another run holds the lock
    ...
    release()                 # also released automatically at process exit

CLI:
    python univ_data_lock.py --status     # who holds it, if anyone
    python univ_data_lock.py --check      # exit 0 if free, 9 if held
"""
from __future__ import annotations

import atexit
import datetime
import json
import os
import sys
import time

LOCK = os.environ.get("UNIV_DATA_LOCK") or os.path.join(
    r"C:\Users\wisew\camnemi-crm\backend\_pipeline_data", ".univ_data.lock")
STALE_HOURS = float(os.environ.get("UNIV_DATA_LOCK_STALE_HOURS", "8"))
BLOCKED_EXIT = 9
_HELD = False


def _holder_alive(pid):
    """True/False when we can prove it, None when psutil is unavailable."""
    try:
        import psutil
    except ImportError:
        return None
    try:
        return psutil.pid_exists(int(pid))
    except Exception:
        return None


def _read():
    try:
        return json.loads(open(LOCK, encoding="utf-8").read())
    except Exception:
        return {}


def acquire(stale_hours=None, wait_minutes=0.0):
    """Take the shared lock, or exit 9 if another university-data run holds it.

    wait_minutes > 0: poll until the holder releases it (for a downstream job that must
    follow an upstream run — e.g. the canonical publish waiting for the collection/parse
    pipeline — instead of skipping the day on a collision).
    """
    global _HELD
    stale = STALE_HOURS if stale_hours is None else float(stale_hours)
    deadline = time.time() + float(wait_minutes) * 60.0
    waited = False
    if _HELD:
        return LOCK
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    while True:
        for _ in range(3):
            try:
                with open(LOCK, "x", encoding="utf-8") as f:
                    json.dump({"pid": os.getpid(),
                               "started": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                               "argv": " ".join(sys.argv[:3])}, f)
                _HELD = True
                atexit.register(release)
                if waited:
                    print("univ_data_lock: acquired after waiting for the previous run", flush=True)
                return LOCK
            except FileExistsError:
                holder = _read()
                pid = holder.get("pid")
                age_h = (time.time() - os.path.getmtime(LOCK)) / 3600.0
                alive = _holder_alive(pid) if pid else None
                if alive is False or age_h >= stale:
                    why = (f"holder pid {pid} is gone" if alive is False
                           else f"lock is {age_h:.1f}h old (>= {stale}h)")
                    print(f"univ_data_lock: stealing stale lock ({why})", flush=True)
                    try:
                        os.remove(LOCK)
                    except OSError:
                        pass
                    continue
                if time.time() < deadline:
                    if not waited:
                        print(f"univ_data_lock: waiting up to {wait_minutes:.0f} min for the current run "
                              f"(pid={pid}, started={holder.get('started')}, age={age_h:.1f}h)", flush=True)
                        waited = True
                    time.sleep(30)
                    break
                print(f"univ_data_lock: BLOCKED — another university-data run holds {LOCK} "
                      f"(pid={pid}, started={holder.get('started')}, age={age_h:.1f}h, "
                      f"argv={holder.get('argv')})", flush=True)
                raise SystemExit(BLOCKED_EXIT)
        else:
            print(f"univ_data_lock: could not acquire {LOCK}", flush=True)
            raise SystemExit(BLOCKED_EXIT)


def release():
    global _HELD
    if not _HELD:
        return
    _HELD = False
    try:
        os.remove(LOCK)
    except FileNotFoundError:
        pass


def main():
    if "--status" in sys.argv:
        if os.path.exists(LOCK):
            print(json.dumps({"held": True, "lock": LOCK, **_read()}, ensure_ascii=False, indent=1))
        else:
            print(json.dumps({"held": False, "lock": LOCK}, ensure_ascii=False))
        return 0
    if "--check" in sys.argv:
        try:
            acquire()
        except SystemExit as exc:
            return exc.code or BLOCKED_EXIT
        release()
        print("free")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())