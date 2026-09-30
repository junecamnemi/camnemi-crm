# -*- coding: utf-8 -*-
"""UNDO the library dedupe: move every file back from
   guides/_archive/_dupes/<level>/<year>/ and guides/_archive/_junk/<level>/<year>/
   into guides/<level>/<year>/.
   The 12 .bin files (HTML saved by my failed guide_fetch attempts) stay in
   _archive/_junk/_bin — they are my own scratch, not collected guides.
"""
import os, shutil, sys

G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
DRY = "--apply" not in sys.argv
moved, errs, kept = 0, [], []

for sub in ("_dupes", "_junk"):
    base = os.path.join(G, "_archive", sub)
    if not os.path.isdir(base):
        continue
    for lv in sorted(os.listdir(base)):
        if lv.startswith("_"):          # _bin and other scratch
            kept.append(lv)
            continue
        for yr in sorted(os.listdir(os.path.join(base, lv))):
            src_dir = os.path.join(base, lv, yr)
            if not os.path.isdir(src_dir):
                continue
            dst_dir = os.path.join(G, lv, yr)
            for f in sorted(os.listdir(src_dir)):
                src = os.path.join(src_dir, f)
                dst = os.path.join(dst_dir, f)
                if os.path.exists(dst):
                    print(f"  SKIP (already present): {lv}/{yr}/{f}")
                    continue
                print(f"  RESTORE {lv}/{yr}/{f}")
                moved += 1
                if not DRY:
                    os.makedirs(dst_dir, exist_ok=True)
                    try:
                        shutil.move(src, dst)
                    except Exception as e:
                        errs.append(f"{src}: {e}")
print(f"\n{'DRY RUN — ' if DRY else ''}restored {moved} file(s), errors {len(errs)}")
for e in errs:
    print("  !", e)
if kept:
    print("left in place (scratch, not guides):", sorted(set(kept)))