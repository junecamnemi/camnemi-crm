#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_univ4_foreign_links.py — 4년제 141교 × (학부/석사/어학원) 외국인 입시링크 종합 지도.

여러 자산을 unvCd 기준으로 병합 -> 각 학교의 외국인 입시링크 후보들을 한 데 모은다.
출력: backend/univ4_foreign_links.json
"""
import json, re, os, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short

B = os.path.dirname(os.path.abspath(__file__))
# 1) unvcd_index (본교 4년제, 등록유지)
idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]
univ4 = {cd: v for cd, v in idx.items()
         if v["school_type"] == "univ4" and not v.get("excluded")}
print(f"4년제 등록유지: {len(univ4)}")

# 2) scrape_map
smap = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
# 3) verified_kb
kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
# 4) adiga school meta (homepage/ipsi)
basic = json.load(open(os.path.join(B, "_adiga_basic_urls.json"), encoding="utf-8"))
# 5) 외국인 요강 로컬 경로 (adiga 폴더 — 참고용, URL 아님)
fg = json.load(open(os.path.join(B, "_foreign_guide_index.json"), encoding="utf-8"))

name_cd = {}
for cd, v in univ4.items():
    name_cd[re.sub(r"\[[^\]]+\]$", "", v["name"]).replace(" ", "")] = cd

def get_cd(s):
    for p in [s, resolve(s) or s]:
        b = re.sub(r"\[[^\]]+\]$", "", p).replace(" ", "")
        if b in name_cd: return name_cd[b]
    r = resolve_short(s)
    if r:
        b = re.sub(r"\[[^\]]+\]$", "", r).replace(" ", "")
        if b in name_cd: return name_cd[b]
    return name_cd.get(s.replace(" ", ""))

out = {}
for cd, v in univ4.items():
    meta = basic.get(cd, {})
    rec = {
        "unvCd": cd, "name": v["name"], "canonical": re.sub(r"\[[^\]]+\]$", "", v["name"]),
        "homepage": meta.get("homepage") or v.get("homepage"),
        "ipsi_homepage": meta.get("ipsi_homepage") or v.get("ipsi_homepage"),
        "stats": v.get("stats", {}),
        "links": {"ba": [], "ma": [], "lang": []},
        "local_pdf": {"ba2026": None, "ba2027": None},
    }
    out[cd] = rec

# scrape_map 반영
for sch, levels in smap.items():
    cd = get_cd(sch)
    if cd not in out or not isinstance(levels, dict): continue
    for lvl, info in levels.items():
        if lvl in ("ba","ma","lang") and isinstance(info, dict):
            u = info.get("url","")
            if str(u).startswith("http"):
                out[cd]["links"][lvl].append({"kind": "scrape_map", "url": u, "tier": info.get("tier")})

# verified_kb 반영 (MA guide_url, lang guide_pdf)
def kb_add(sec, attr, lvl, kind):
    s = kb.get(sec, {})
    schools = s.get("schools", {}) if isinstance(s,dict) and "schools" in s else s
    for n, v in schools.items():
        cd = get_cd(n)
        if cd in out and isinstance(v, dict):
            u = v.get(attr)
            if isinstance(u, str) and u.startswith("http"):
                out[cd]["links"][lvl].append({"kind": kind, "url": u})
kb_add("master", "guide_url", "ma", "kb_ma_guide")
kb_add("lang_programs", "guide_pdf", "lang", "kb_lang_guide")
kb_add("lang_programs", "guide_url", "lang", "kb_lang_url")

# 외국인 로컬 PDF 경로 (2026/2027)
for cd, fgv in fg.items():
    if cd in out and fgv.get("univ4"):
        for k, p in fgv["univ4"].items():
            if "2026" in k and "외국인" in k: out[cd]["local_pdf"]["ba2026"] = p
            if "2027" in k and "외국인" in k: out[cd]["local_pdf"]["ba2027"] = p

json.dump(out, open(os.path.join(B, "univ4_foreign_links.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"저장: univ4_foreign_links.json ({len(out)}교)")
# sample
for cd in list(out)[:3]:
    r = out[cd]
    print(f"\n{r['name']} ({r['canonical']})")
    print(f"  homepage: {r['homepage']}")
    print(f"  ipsi: {r['ipsi_homepage']}")
    for lvl, links in r["links"].items():
        for l in links:
            print(f"  [{lvl}]({l['kind']}): {l['url'][:70]}")