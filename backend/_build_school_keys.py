#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build school_keys.json — canonical school keys from adiga manifests.
key: clean adiga university name (strip [campus]) ; value: {cd, adiga_full, aliases}
Used to normalize any school reference (lang_programs, discover targets, KB) to one key."""
import os, re, json, csv, glob

AD = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
OUT = r"C:\Users\wisew\camnemi-crm\backend\school_keys.json"
manifests = glob.glob(os.path.join(AD, "adiga_202*/**/download_manifest.csv"), recursive=True) or \
            glob.glob(os.path.join(AD, "adiga_202*/download_manifest.csv"))

clean = {}
for m in manifests:
    try:
        for r in csv.DictReader(open(m, encoding="utf-8-sig")):
            name = r.get("university") or ""
            cd = r.get("unv_cd") or ""
            base = re.sub(r"\[.*?\]|\(.*?\)", "", name).strip()
            if base:
                clean.setdefault(base, {"cd": cd, "adiga": set(), "aliases": {base}})
                clean[base]["adiga"].add(name)
    except Exception as e:
        print("skip", m, e)

out = {}
for base, v in clean.items():
    out[base] = {"cd": v["cd"], "adiga_names": sorted(v["adiga"])}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"adiga 정식 키: {len(out)}개 → {OUT}")

# quick lookup helper preview
def norm(s): return re.sub(r"\[.*?\]|\(.*?\)", "", str(s)).replace("대학원","").strip()
for probe in ["가천대", "가천대학교", "경북대", "전북대학교", "국립부경대학교"]:
    hit = out.get(probe)
    if not hit:
        for b in out:
            if b.startswith(probe) or probe.startswith(b):
                hit = out[b]; break
    print(f"  {probe!r} -> {b if 'b' in dir() and hit else ''} ({hit['cd'] if hit else '-'})")