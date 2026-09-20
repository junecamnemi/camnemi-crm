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

links = defaultdict(lambda: defaultdict(set))
for sch, levels in smap.items():
    cd = get_cd(sch)
    if cd in kept_set and isinstance(levels, dict):
        for lvl, info in levels.items():
            if isinstance(info, dict) and str(info.get("url","")).startswith("http"):
                links[cd][lvl].add(info["url"])
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
kb_add("lang_programs", "guide_pdf", "lang")
kb_add("lang_programs", "guide_url", "lang")

# 전문대 PDF
req = {"univ4": ["ba","ma","lang"], "junior": ["ba","lang"]}
print("| 구분 | 레벨 | 필요 | URL보유 | +전문대PDF | 최종 |")
print("|---|---|---|---|---|---|")
for label, st, lvls in [("4년제","univ4",["ba","ma","lang"]), ("전문대","junior",["ba","lang"])]:
    cds = [cd for cd in kept if idx[cd]["school_type"]==st]
    for lvl in lvls:
        n = len(cds)
        u = sum(1 for cd in cds if links[cd].get(lvl))
        pdf = sum(1 for cd in cds if idx[cd].get("junior_gaides_pdf"))
        final = u
        if lvl == "ba" and st == "junior":
            final = pdf  # 전문대 학사는 PDF로
        if lvl == "lang" and st == "junior":
            final = pdf
        print(f"| {label} | {lvl} | {n} | {u} | {pdf if st=='junior' else '-'} | {final} ({final/n*100:.0f}%) |")