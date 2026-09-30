#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hunt the A-bucket guide PDFs across every drive (the resolver only looks in the G: library).

For each entry that reported "no local guide", search C:, D:, G: for
  1. the exact expected filename, then
  2. any file whose name contains the school's distinctive stem (학교/대학교 stripped).
Prunes OS/dev trees. Writes backend/_guide_hunt.json and prints where each one actually lives.
"""
import os, json, re

B = os.path.dirname(os.path.abspath(__file__))
SKIP = re.compile(r"(?i)(\\windows(\\|$)|\\program files|\\program files \(x86\)|\\\$recycle|\\system volume|"
                  r"\\appdata\\local\\temp|\\node_modules|\\\.git\\|\\\.cache|\\anaconda|\\python3|"
                  r"\\microsoft\\|\\packages\\|\\winsxs)")
DRIVES = ["C:\\", "D:\\", "G:\\"]


def stems(name):
    s = re.sub(r"(학교|대학교|대학)$", "", name)
    return [x for x in {name, s} if x]


def hunt():
    rep = json.load(open(os.path.join(B, "_tuition_gap_report.json"), encoding="utf-8"))["detail"]
    a = [x for x in rep if x["bucket"] == "A_no_local_guide"]
    found = {}
    index = {}
    scanned = 0
    for root in DRIVES:
        if not os.path.exists(root):
            continue
        for dp, dn, fn in os.walk(root):
            if SKIP.search(dp + "\\"):
                dn[:] = []
                continue
            scanned += 1
            for f in fn:
                if f.lower().endswith(".pdf"):
                    index.setdefault(f, os.path.join(dp, f))
    print("pdf files indexed:", len(index), "dirs scanned:", scanned)
    for x in a:
        key = f"{x['school']}|{x['level']}"
        hits = []
        exp = x.get("guide")
        if exp and exp in index:
            hits.append({"how": "exact_filename", "path": index[exp]})
        for st in stems(x["school"]):
            for f, p in index.items():
                if st in f and {"how": "name_contains", "path": p} not in hits:
                    hits.append({"how": "name_contains", "path": p})
        found[key] = hits
    json.dump(found, open(os.path.join(B, "_guide_hunt.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hit = sum(1 for v in found.values() if v)
    print(f"A entries: {len(a)} | found on disk: {hit} | still missing: {len(a)-hit}\n")
    for k, v in found.items():
        if v:
            print("  ✔", k, "->", v[0]["path"])
            for extra in v[1:4]:
                print("       also:", extra["path"])
        else:
            print("  ✘", k, "(no pdf anywhere)")


if __name__ == "__main__":
    hunt()