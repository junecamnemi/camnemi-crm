import json, re, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short
from collections import Counter, defaultdict

B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
master = json.load(open("_guide_2027_master.json", encoding="utf-8"))
sm = json.load(open("scrape_map.json", encoding="utf-8"))

univ4 = {cd: v for cd, v in idx.items() if v["school_type"]=="univ4" and not v.get("excluded")}
name_cd = {re.sub(r"\[[^\]]+\]$","",v["name"]).replace(" ",""):cd for cd,v in univ4.items()}
def get_cd(s):
    for p in [s, resolve(s) or s]:
        b=re.sub(r"\[[^\]]+\]$","",p).replace(" ","")
        if b in name_cd: return name_cd[b]
    r=resolve_short(s)
    if r:
        b=re.sub(r"\[[^\]]+\]$","",r).replace(" ","")
        if b in name_cd: return name_cd[b]
    return name_cd.get(s.replace(" ",""))

# master를 등록유지 4년제에 매핑
out = {}
for rec in master:
    cd = get_cd(rec.get("school",""))
    if cd not in univ4: continue
    out[cd] = {
        "name": univ4[cd]["name"],
        "ba_url": rec.get("ba_url") if str(rec.get("ba_url","")).startswith("http") else None,
        "ba_local": rec.get("ba_url") if not str(rec.get("ba_url","")).startswith("http") else None,
        "ma_url": rec.get("ma_url") if str(rec.get("ma_url","")).startswith("http") else None,
        "lang_url": rec.get("lang_url") if str(rec.get("lang_url","")).startswith("http") else None,
    }

# 커버리지 (등록유지 4년제 141)
def cov(lvl):
    n = sum(1 for v in out.values() if v.get(lvl+"_url"))
    local = sum(1 for v in out.values() if v.get(lvl+"_local"))
    return n, local

print("=== 등록유지 4년제 141교 — 외국인 요강 URL ===")
for lvl, label in [("ba","학부 외국인"), ("ma","석사 외국인"), ("lang","어학원 외국인")]:
    n, loc = cov(lvl)
    print(f"  {label}: http {n}/141 · 로컬adiga {loc}")

# ba가 http 있지만 비어있는 주요 대학
print("\n=== ba(학부 외국인) URL 미보유 대학 (중요) ===")
no_ba = [v["name"] for v in out.values() if not v.get("ba_url")]
print(f"  총 {len(no_ba)}교:", no_ba)

json.dump(out, open("_univ4_2027_master_links.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장: _univ4_2027_master_links.json")