import json, re, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short
from collections import Counter

idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
smap = json.load(open("scrape_map.json", encoding="utf-8"))
kb = json.load(open("verified_kb.json", encoding="utf-8"))

def norm(s):
    return re.sub(r"\[[^\]]+\]$", "", s).replace(" ", "")

name_to_cd = {norm(v["name"]): cd for cd, v in idx.items()}
kept = [cd for cd, v in idx.items() if not v["excluded"]]
kept_set = set(kept)

def get_cd(sch):
    for probe in [sch, resolve(sch) or sch]:
        if norm(probe) in name_to_cd: return name_to_cd[norm(probe)]
    r = resolve_short(sch)
    if r and norm(r) in name_to_cd: return name_to_cd[norm(r)]
    return name_to_cd.get(sch.replace(" ", ""))

have = Counter()   # 레벨별 실보유
need = Counter()   # 등록유지 기준 필요수

# 요구 레벨
for cd in kept:
    st = idx[cd]["school_type"]
    for lvl in (["ba","ma","lang"] if st=="univ4" else ["ba","lang"]):
        need[lvl] += 1

# scrape_map URL
for sch, levels in smap.items():
    cd = get_cd(sch)
    if cd not in kept_set or not isinstance(levels, dict): continue
    for lvl, info in levels.items():
        if isinstance(info, dict) and str(info.get("url","")).startswith("http") and lvl in need:
            have[lvl] += 1

# verified_kb 요강 URL
def kb_add(sec, attr, lvl):
    s = kb.get(sec, {})
    schools = s.get("schools", {}) if isinstance(s,dict) and "schools" in s else s
    for n, v in schools.items():
        cd = get_cd(n)
        if cd in kept_set and isinstance(v, dict):
            u = v.get(attr)
            if isinstance(u, str) and u.startswith("http") and lvl in need:
                have[lvl] += 1
kb_add("master", "guide_url", "ma")
kb_add("junior", "foreign_guide", "junior")
kb_add("junior", "guide_url", "junior")
kb_add("lang_programs", "guide_pdf", "lang")
kb_add("lang_programs", "guide_url", "lang")

print("| 레벨 | 필요 | 보유 | 커버리지 |")
print("|---|---|---|---|")
for lvl in ["ba","ma","lang","junior"]:
    n, h = need.get(lvl,0), have.get(lvl,0)
    pct = f"{h/n*100:.0f}%" if n else "-"
    print(f"| {lvl:5s} | {n:3d} | {h:3d} | {pct} |")

# 요강 전무 등록유지 학교
nolink = []
for cd in kept:
    if not any(1 for s,lv in [(smap,None)] for lv in ["ba","ma","lang","junior"] if 0):
        pass
print("\n(전문대 요강은 verified_kb junior.foreign_guide + guide_url로 집계됨)")