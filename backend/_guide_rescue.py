#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rescue crawled guide PDFs stranded in a botched clone path inside Hermes scratch.

`C:\\c\\Users\\…\\cache\\scratch\\clone_tmp\\camnemi-crm.git\\backend\\_foreign_*_pdf\\` holds the
crawled 외국인 모집요강 files (a git clone run with an MSYS path created a literal `C:\\c\\` tree).
Hermes prunes idle scratch entries, so these are one cleanup away from being lost and the tuition
resolver keeps reporting "no local guide".

Copies each file into the stable library:  guides/<level>/<year>/<name>
(_foreign_batch10_pdf has no level signal → guides/_archive/unknown/).
Never overwrites; prints a summary. Run with --dry to preview.
"""
import os, re, json, shutil, sys

SRC_BASE = r"C:\c\Users\wisew\AppData\Local\hermes\profiles\univ\cache\scratch\clone_tmp\camnemi-crm.git\backend"
LIB = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides"
MAP = {"_foreign_ba_pdf": "ba", "_foreign_ma_pdf": "ma", "_foreign_junior_pdf": "junior",
       "_foreign_lang_pdf": "lang", "_foreign_batch10_pdf": None}

dry = "--dry" in sys.argv
moved, skipped, missing = [], 0, []
for folder, level in MAP.items():
    src = os.path.join(SRC_BASE, folder)
    if not os.path.isdir(src):
        missing.append(folder)
        continue
    for f in os.listdir(src):
        if not f.lower().endswith(".pdf"):
            continue
        m = re.search(r"(20\d{2})", f)
        year = m.group(1) if m else "unknown"
        if level is None:
            # no level signal: infer from the filename, else park in the archive
            if "한국어교육원" in f or "어학" in f:
                level2 = "lang"
            elif "대학원" in f or "_ma" in f:
                level2 = "ma"
            elif "전문학사" in f or "전문대" in f:
                level2 = "junior"
            else:
                level2, year = "_archive/unknown", ""
            dest = os.path.join(LIB, level2, year, f) if year else os.path.join(LIB, level2, f)
        else:
            dest = os.path.join(LIB, level, year, f)
        if os.path.exists(dest):
            skipped += 1
            continue
        if not dry:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(os.path.join(src, f), dest)
        moved.append(dest)
print(f"copied {len(moved)} | already present {skipped} | missing folders {missing}")
for p in moved[:15]:
    print("   ->", p)
if len(moved) > 15:
    print(f"   … and {len(moved)-15} more")
if not dry:
    json.dump(moved, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_guide_rescue_log.json"),
                          "w", encoding="utf-8"), ensure_ascii=False, indent=1)