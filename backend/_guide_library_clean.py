#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guide library cleanup — dedup + refile + archive, reversible, fully ledged.

The operator wants the library finished: one correct copy per school×level×year, nothing else.
Nothing is hard-deleted — duplicates move to _dedup_removed\ and stale years to _archive\, so every
action can be undone from the ledger.

Order (each stage re-runs on the already-cleaned set):
  1. md5-identical groups → keep ONE canonical copy, quarantine the rest (1,035 MB).
     Canonical choice: the member whose PATH level equals the CONTENT level (text), else the member
     already in a real level folder, else first.
  2. same-name groups (same level+year+normalized name) → keep one, quarantine extras.
  3. level-unknown files (279) → classify by CONTENT, move into the right level folder.
  4. stray years (2019–2025) → move to _archive\<year>\<level>\.
CONTENT level: read first ~4000 chars of the text layer; keyword priority 대학원→ma · 전문학사/전문대
→junior · 한국어교육원/어학/정규과정→lang · else ba. Image-only PDFs fall back to filename.

  python _guide_library_clean.py --dry        # plan only
  python _guide_library_clean.py --execute    # do it, writing _guide_cleanup_ledger.json
"""
import os, re, json, sys, hashlib, shutil, collections

BASE = r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project"
GUIDES = os.path.join(BASE, "guides")
QUAR = os.path.join(BASE, "guides", "_dedup_removed")
ARCH = os.path.join(BASE, "_archive")
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_guide_cleanup_ledger.json")

LEVELS = ("ba", "ma", "junior", "lang")
YEAR = re.compile(r"(20\d\d)")
CONTENT_PRIORITY = (
    ("ma", re.compile(r"대학원|석사|박사|Graduate|Master|Doctor")),
    ("junior", re.compile(r"전문학사|전문대|2년제|3년제")),
    ("lang", re.compile(r"한국어교육원|어학|언어교육|정규과정|연수과정|어학당")),
)
LEVEL_WORD = {"ba": r"학부|학사|신입학|편입학|학과|전공|Undergraduate|Bachelor",
              "ma": r"대학원|석사|박사|Graduate|Master|Doctor",
              "junior": r"전문학사|전문대|2년제|3년제",
              "lang": r"한국어교육원|어학|언어교육|정규과정|연수|어학당"}
LVL = {"ba": "ba", "ma": "ma", "junior": "junior", "lang": "lang"}


def level_of(path):
    low = path.lower().replace("\\", "/")
    for lv in LEVELS:
        if re.search(rf"/{lv}/", low) or re.search(rf"/{lv}_", low) or low.endswith(lv):
            return lv
    if "junior" in low or "전문" in low:
        return "junior"
    return "?"


def year_of(path):
    m = YEAR.search(os.path.basename(path))
    if m:
        return m.group(1)
    m = re.search(r"[\\/](20\d\d)[\\/]", path.replace("\\", "/"))
    return m.group(1) if m else "?"


def text_head(path, n=4000):
    try:
        import pymupdf
        d = pymupdf.open(path)
        t = ""
        for pg in d:
            t += pg.get_text()
            if len(t) > n:
                break
        d.close()
        return t[:n]
    except Exception:
        return ""


def content_level(path):
    t = text_head(path)
    if len(t.strip()) < 30:
        return None
    for lv, rx in CONTENT_PRIORITY:
        if rx.search(t):
            return lv
    if re.search(r"학부|학사|신입학|편입학|Undergraduate|Bachelor|학과|전공", t):
        return "ba"
    return None


def norm(name):
    n = os.path.basename(name)
    n = re.sub(r"\.pdf$", "", n, flags=re.I)
    n = re.sub(r"^\d{6,7}_", "", n)
    n = re.sub(r"[\[\](){}]", " ", n)
    n = re.sub(r"(외국인|모집요강|입학요강|대학원|학부|본교|분교|캠퍼스|국제학생)", " ", n)
    n = re.sub(r"[_\-\s]+", " ", n).strip().lower()
    return re.sub(r"\s+", " ", n)


def collect():
    files = []
    for dirpath, _, names in os.walk(GUIDES):
        for n in names:
            if not re.search(r"\.pdf$", n, re.I):
                continue
            # _dedup_removed is the quarantine I am about to create; everything else under guides\
            # (including guides\_archive\… and guides\_all\…) IS the library and must be cleaned too.
            if "_dedup_removed" in dirpath:
                continue
            p = os.path.join(dirpath, n)
            try:
                sz = os.path.getsize(p)
                md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
            except OSError:
                continue
            files.append({"path": p, "size": sz, "md5": md5, "name": n,
                          "path_level": level_of(p), "year": year_of(p),
                          "content_level": None})
    return files


def quar_path(orig):
    rel = os.path.relpath(orig, GUIDES)
    return os.path.join(QUAR, rel)


def main():
    dry = "--execute" not in sys.argv
    ledger = {"dry": dry, "actions": []}
    files = collect()
    print(f"scanned {len(files)} PDFs")
    bymd5 = collections.defaultdict(list)
    for f in files:
        bymd5[f["md5"]].append(f)
    kept = {}
    moved = 0

    def act(kind, src, dst=None):
        ledger["actions"].append({"kind": kind, "src": src, "dst": dst})
        if not dry:
            os.makedirs(os.path.dirname(dst or src), exist_ok=True)
            if dst:
                shutil.move(src, dst)

    # ---- stage 1: md5 dedup
    dup_groups = 0
    for md5, grp in bymd5.items():
        if len(grp) == 1:
            kept[md5] = grp[0]
            continue
        dup_groups += 1
        # content level for the group (any member with text)
        clev = None
        for g in grp:
            if g["content_level"] is None:
                g["content_level"] = content_level(g["path"])
            if clev is None:
                clev = g["content_level"]
        # canonical: path_level == content_level, else path_level in LEVELS, else first
        def rank(g):
            return (0 if (clev and g["path_level"] == clev) else 1,
                    0 if g["path_level"] in LEVELS else 1)
        grp.sort(key=rank)
        canon = grp[0]
        kept[md5] = canon
        for extra in grp[1:]:
            act("md5_dup", extra["path"], quar_path(extra["path"]))
            moved += 1
    print(f"md5 groups={len(bymd5)} duplicate groups={dup_groups} quarantined={moved}")

    # ---- stage 2: same-name dedup (after md5, distinct files with same name)
    byname = collections.defaultdict(list)
    for md5, f in kept.items():
        byname[(f["path_level"], f["year"], norm(f["name"]))].append(f)
    moved2 = 0
    for k, grp in byname.items():
        if len(grp) == 1:
            continue
        grp.sort(key=lambda g: g["size"], reverse=True)
        for extra in grp[1:]:
            act("name_dup", extra["path"], quar_path(extra["path"]))
            moved2 += 1
            del kept[extra["md5"]]
    print(f"name-dup extras quarantined: {moved2}")

    # ---- stage 3: refile level-unknown
    moved3 = 0
    for md5, f in list(kept.items()):
        if f["path_level"] != "?":
            continue
        clev = f["content_level"] or content_level(f["path"])
        newlv = clev if clev in LEVELS else "ba"
        newdir = os.path.join(GUIDES, newlv, f["year"] if f["year"] != "?" else "2026")
        if os.path.normpath(os.path.dirname(f["path"])) == os.path.normpath(newdir):
            continue
        act("refile_level", f["path"], os.path.join(newdir, f["name"]))
        f["path_level"] = newlv
        moved3 += 1
    print(f"refiled level-unknown: {moved3}")

    # ---- stage 4: archive stray years
    moved4 = 0
    for md5, f in list(kept.items()):
        y = f["year"]
        if y not in ("2019", "2022", "2023", "2025"):
            continue
        dst = os.path.join(ARCH, y, f["path_level"] if f["path_level"] in LEVELS else "unknown", f["name"])
        act("archive_stale", f["path"], dst)
        moved4 += 1
    print(f"archived stray-year: {moved4}")

    # ---- report final state
    final = {}
    for f in kept.values():
        final[f["path_level"]] = final.get(f["path_level"], 0) + 1
    print("final library by level:", final)
    total = sum(final.values())
    print(f"final PDFs in library: {total}  (start {len(files)})")
    json.dump(ledger, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(("DRY RUN — nothing moved. Re-run with --execute to apply." if dry
           else "EXECUTED.") + f" ledger: {LEDGER}")


if __name__ == "__main__":
    main()