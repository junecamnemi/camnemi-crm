import json, re, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short
from collections import Counter, defaultdict

idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
smap = json.load(open("scrape_map.json", encoding="utf-8"))
kb = json.load(open("verified_kb.json", encoding="utf-8"))

name_cd = {}
for cd, v in idx.items():
    base = re.sub(r"\[[^\]]+\]$", "", v["name"]).replace(" ", "")
    name_cd[base] = cd
kept = {cd for cd, v in idx.items() if not v.get("excluded")}
def get_cd(s):
    for p in [s, resolve(s) or s]:
        b = re.sub(r"\[[^\]]+\]$", "", p).replace(" ", "")
        if b in name_cd: return name_cd[b]
    r = resolve_short(s)
    if r:
        b = re.sub(r"\[[^\]]+\]$", "", r).replace(" ", "")
        if b in name_cd: return name_cd[b]
    return name_cd.get(s.replace(" ", ""))

# 1) scrape_map (학교 자체) 레벨별 URL — 등록유지
sm_links = defaultdict(dict)
for sch, levels in smap.items():
    cd = get_cd(sch)
    if cd not in kept or not isinstance(levels, dict): continue
    for lvl, info in levels.items():
        if isinstance(info, dict) and str(info.get("url","")).startswith("http"):
            sm_links[cd][lvl] = info["url"]

# 2) verified_kb 요강 URL (자체도메인 여부 무관, 필터만)
def kb_links(sec, attr, lvl):
    s = kb.get(sec, {})
    schools = s.get("schools", {}) if isinstance(s,dict) and "schools" in s else s
    for n, v in schools.items():
        cd = get_cd(n)
        if cd in kept and isinstance(v, dict):
            u = v.get(attr)
            if isinstance(u, str) and u.startswith("http"):
                sm_links[cd].setdefault(lvl, u)
kb_links("master", "guide_url", "ma")
kb_links("lang_programs", "guide_pdf", "lang")
kb_links("junior", "guide_url", "junior")
kb_links("junior", "foreign_guide", "junior")

# 레벨별 커버리지
print("=== 학교 자체 홈페이지 요강 URL (등록유지 기준) ===")
req = {"univ4": ["ba","ma","lang"], "junior": ["ba","lang"]}
for st, label in [("univ4","4년제"), ("junior","전문대")]:
    cds = [cd for cd in kept if idx[cd]["school_type"]==st]
    print(f"\n[{label}] {len(cds)}교")
    for lvl in req[st]:
        n = len(cds)
        h = sum(1 for cd in cds if sm_links[cd].get(lvl))
        print(f"  {lvl:5s}: {h}/{n} ({h/n*100:.0f}%)")

# adiga 도메인/로컬경로로 찬 것 제거 확인
json.dump({k: dict(v) for k, v in sm_links.items()},
          open("_school_homepage_guide_links.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장: _school_homepage_guide_links.json")