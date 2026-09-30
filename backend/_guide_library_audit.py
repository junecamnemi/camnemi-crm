#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit the guide library: how many folders, how many files, how much duplication.

Operator question: "우리 가이드 전부 폴더 하나에 중복없이 들어 있는거 맞아?" — answer with counts, not
assurance. Reports:
  · every root that holds guides, and how many PDFs each holds
  · duplicate CONTENT (md5) across roots — the same document stored twice
  · duplicate NAME (normalized school+year+level) — same document re-saved under a new name
  · a single canonical root per level+year, so "one folder" can be made true
Writes _guide_library_audit.json
"""
import os, re, json, hashlib, collections, sys

B = os.path.dirname(os.path.abspath(__file__))
ROOTS = [
    r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides",
    r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\_archive",
    r"G:\공유 드라이브\Hermes\Camnemi\02_Crawling_Sheet\University_Project\guides_all",
]
OUT = os.path.join(B, "_guide_library_audit.json")
LEVELS = ("ba", "ma", "junior", "lang")
YEAR = re.compile(r"(20\d\d)")


def norm(name):
    n = os.path.basename(name)
    n = re.sub(r"\.(pdf|hwpx?|xlsx?|docx?)$", "", n, flags=re.I)
    n = re.sub(r"^\d{6,7}_", "", n)                 # 0000196_ 접두어
    n = re.sub(r"[\[\](){}]", " ", n)
    n = re.sub(r"(외국인|모집요강|입학요강|대학원|학부|본교|분교|캠퍼스|국제학생)", " ", n)
    n = re.sub(r"[_\-\s]+", " ", n).strip().lower()
    return re.sub(r"\s+", " ", n)


def level_of(path):
    low = path.lower()
    for lv in LEVELS:
        if re.search(rf"[\\/]{lv}[\\/]|[\\/]{lv}_", low):
            return lv
    if "junior" in low or "전문" in low:
        return "junior"
    return "?"


def year_of(path):
    m = YEAR.search(os.path.basename(path))
    if m:
        return m.group(1)
    m = re.search(r"[\\/](20\d\d)[\\/]", path)
    return m.group(1) if m else "?"


def main():
    files, roots_seen = [], collections.Counter()
    for root in ROOTS:
        if not os.path.isdir(root):
            print(f"  (missing) {root}")
            continue
        for dirpath, _, names in os.walk(root):
            for n in names:
                if not re.search(r"\.pdf$", n, re.I):
                    continue
                p = os.path.join(dirpath, n)
                try:
                    sz = os.path.getsize(p)
                except OSError:
                    continue
                files.append({"path": p, "size": sz, "name": n,
                              "level": level_of(p), "year": year_of(p),
                              "root": root.split("University_Project")[-1].strip("\\/") or root})
                roots_seen[root] += 1
    print(f"PDFs total: {len(files)}")
    for r, c in roots_seen.most_common():
        print(f"   {c:5}  {r[-58:]}")
    by_level = collections.Counter(f["level"] for f in files)
    by_year = collections.Counter(f["year"] for f in files)
    print("by level:", dict(by_level))
    print("by year :", dict(by_year))

    # duplicate content
    h2p = collections.defaultdict(list)
    for f in files:
        try:
            h = hashlib.md5(open(f["path"], "rb").read()).hexdigest()
        except OSError:
            continue
        f["md5"] = h
        h2p[h].append(f["path"])
    dup_content = {h: ps for h, ps in h2p.items() if len(ps) > 1}
    dup_files = sum(len(ps) - 1 for ps in dup_content.values())
    print(f"duplicate CONTENT groups: {len(dup_content)}  (extra copies: {dup_files})")

    # duplicate name within the same level+year (same document re-saved)
    n2p = collections.defaultdict(list)
    for f in files:
        n2p[(f["level"], f["year"], norm(f["name"]))].append(f["path"])
    dup_name = {k: ps for k, ps in n2p.items() if len(ps) > 1}
    print(f"duplicate NAME (same level+year) groups: {len(dup_name)}  "
          f"(extra copies: {sum(len(p)-1 for p in dup_name.values())})")
    print("examples:")
    for k, ps in list(dup_content.items())[:5]:
        print("   content dup:", [os.path.basename(x) for x in ps][:3])
    for k, ps in list(dup_name.items())[:5]:
        print(f"   name dup [{k[0]}/{k[1]}]:", [os.path.basename(x)[:44] for x in ps][:3])

    # is it "one folder"? per level+year, how many distinct roots hold files
    spread = collections.defaultdict(set)
    for f in files:
        spread[(f["level"], f["year"])].add(f["root"])
    print("roots per (level,year) — 1 means 'one folder' is already true:")
    for k in sorted(spread):
        roots = {r.split("\\")[-1] for r in spread[k]}
        print(f"   {k[0]:8}{k[1]}  roots={len(roots)} {sorted(roots)[:4]}")

    json.dump({"total": len(files), "by_level": dict(by_level), "by_year": dict(by_year),
               "roots": {r: c for r, c in roots_seen.items()},
               "dup_content_groups": len(dup_content), "dup_content_extra": dup_files,
               "dup_name_groups": len(dup_name),
               "dup_name_extra": sum(len(p) - 1 for p in dup_name.values()),
               "files": files},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", OUT)


if __name__ == "__main__":
    main()