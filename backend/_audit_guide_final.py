import json, re, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short
from collections import Counter, defaultdict

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

# per-school level->set(urls)
links = defaultdict(lambda: defaultdict(set))  # cd -> lvl -> {url}

# scrape_map
for sch, levels in smap.items():
    cd = get_cd(sch)
    if cd not in kept_set or not isinstance(levels, dict): continue
    for lvl, info in levels.items():
        if isinstance(info, dict) and str(info.get("url","")).startswith("http"):
            links[cd][lvl].add(info["url"])

# verified_kb
def kb_add(sec, attr, lvl):
    s = kb.get(sec, {})
    schools = s.get("schools", {}) if isinstance(s,dict) and "schools" in s else s
    for n, v in schools.items():
        cd = get_cd(n)
        if cd in kept_set and isinstance(v, dict):
            u = v.get(attr)
            if isinstance(u, str) and u.startswith("http"):
                links[cd][lvl].add(u)
kb_add("master", "guide_url", "ma")
kb_add("junior", "foreign_guide", "junior")
kb_add("junior", "guide_url", "junior")
kb_add("junior", "foreign_guide_pdf", "junior")
kb_add("lang_programs", "guide_pdf", "lang")
kb_add("lang_programs", "guide_url", "lang")

# 요구 레벨
req = {"univ4": ["ba","ma","lang"], "junior": ["ba","lang"]}
# junior도 ba/lang으로 집계되지만 구분별로 보여줌
print("| 구분 | 학교수 | 레벨 | 필요 | 보유(1+URL) | 커버리지 |")
print("|---|---|---|---|---|---|")
tot_need = Counter(); tot_have = Counter()
for cd in kept:
    st = idx[cd]["school_type"]
    for lvl in req[st]:
        tot_need[lvl] += 1
        if links[cd].get(lvl):
            tot_have[lvl] += 1
for lvl in ["ba", "ma", "lang", "junior"]:
    n, h = tot_need.get(lvl,0), tot_have.get(lvl,0)
    if n:
        print(f"| {'4년제' if lvl in ('ma',) else '전체'}| {n} | {lvl} | {n} | {h} | {h/n*100:.0f}% |")
# 전문대만 ba/lang 따로
for lvl in ["ba", "lang"]:
    n = sum(1 for cd in kept if idx[cd]["school_type"]=="junior")
    h = sum(1 for cd in kept if idx[cd]["school_type"]=="junior" and links[cd].get(lvl))
    print(f"| 전문대 | {n} | {lvl} | {n} | {h} | {h/n*100:.0f}% |")

# 전무 학교
nolink = [idx[cd]["name"] for cd in kept if not links[cd]]
print(f"\n요강 링크 전무: {len(nolink)}교")
print("  ", nolink)

json.dump({k: {l: list(s) for l, s in v.items()} for k, v in links.items()},
          open("_unvcd_guide_links.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장: _unvcd_guide_links.json")