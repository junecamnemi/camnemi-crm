#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data.js integrity guard — run before publishing data.js / after any KB sync.

Regression guard for the 2026-09-29 incident: a one-off rewrite of data.js dropped
the whole `window.UNIV_GUIDES` block (leaving `]}}};`), so the file stopped parsing
and UNIV_KNOWLEDGE / UNIV_GUIDES / UNIV_SPECIAL all failed to load in the app.

Checks:
  1. `node --check data.js` exits 0  (real JS parse, not just JSON)
  2. all three globals exist and parse, with record counts reported
  3. every data.js writer goes through _datajs_safe.write_safe (no ad-hoc writes)
  4. round-trip: parse -> render reproduces data.js byte-for-byte, i.e. the shared
     writer is lossless (nothing is dropped when a generator rebuilds the file)

Exit 0 = OK, 1 = FAIL.  Usage:  python backend/tests/datajs_integrity_test.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "backend"))
import _datajs_safe as S  # noqa: E402

DATA = os.path.join(REPO, "data.js")
WRITERS = [
    "backend/_sync_datajs_v3.py",
    "backend/_sync_datajs_lang_guide.py",
    "backend/_sync_datajs_curation.py",
]

fails = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


print("data.js integrity guard")

# 1. node --check
r = subprocess.run(["node", "--check", DATA], capture_output=True, text=True)
check("node --check data.js", r.returncode == 0,
      "" if r.returncode == 0 else (r.stderr or "").strip().splitlines()[-1] if (r.stderr or "").strip() else "")

# 2. three globals
try:
    g = S.parse_globals(DATA)
    counts = {"UNIV_KNOWLEDGE": len(g["knowledge"]), "UNIV_GUIDES": len(g["guides"]),
              "UNIV_SPECIAL": len(g["special"])}
    check("all three globals present", True, str(counts))
    check("UNIV_KNOWLEDGE non-empty", counts["UNIV_KNOWLEDGE"] > 0)
    check("UNIV_GUIDES non-empty", counts["UNIV_GUIDES"] > 0)
    check("UNIV_SPECIAL non-empty", counts["UNIV_SPECIAL"] > 0)
except Exception as ex:
    check("all three globals present", False, str(ex))
    counts = None

# 3. writers use the shared safe writer
for w in WRITERS:
    p = os.path.join(REPO, w)
    if not os.path.exists(p):
        check("writer present: " + w, False)
        continue
    src = open(p, encoding="utf-8").read()
    check("writer uses write_safe: " + w, "write_safe(" in src)

# 4. lossless round-trip through the shared renderer
if counts:
    try:
        raw = open(DATA, encoding="utf-8").read().replace("\r\n", "\n")
        out = S.render(g["prefix"], g["knowledge"], g["guides"], g["special"], knowledge_indent=1)
        check("render() round-trip is byte-identical", out == raw,
              "" if out == raw else "differs at %d" % next(i for i in range(min(len(out), len(raw)))
                                                           if out[i] != raw[i]))
    except Exception as ex:
        check("render() round-trip is byte-identical", False, str(ex))

print("\n" + ("FAILED: " + ", ".join(fails) if fails else "ALL CHECKS PASSED"))
sys.exit(1 if fails else 0)