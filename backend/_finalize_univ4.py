import json, os, re
B = "."
# 1) 학부 외국인 URL
ba = json.load(open("_ba_foreign_urls.json", encoding="utf-8"))
# 2) 석사/어학원 URL (master에서)
master = json.load(open("_univ4_2027_master_links.json", encoding="utf-8"))
# 3) unvcd_index
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

def norm(s): return re.sub(r"\[[^\]]+\]$","",s).replace(" ","")
# name -> cd
name_cd = {}
for cd, v in schools.items():
    name_cd[norm(v["name"])] = cd

# master의 ma/lang을 name->cd로
ma_map = {norm(v["name"]): v.get("ma_url") for v in master.values() if v.get("ma_url")}
lang_map = {norm(v["name"]): v.get("lang_url") for v in master.values() if v.get("lang_url")}

# unvcd_index에 foreign_links 구조화 반영
updated = 0
for cd, v in schools.items():
    if v["school_type"] != "univ4" or v.get("excluded"):
        continue
    n = norm(v["name"])
    fl = {
        "ba_foreign": ba.get(n),
        "ma_foreign": ma_map.get(n),
        "lang_foreign": lang_map.get(n),
    }
    v["foreign_links"] = fl
    updated += 1

json.dump(idx, open("unvcd_index.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"unvcd_index.json 반영: {updated}교")

# 커버리지 요약
cov = {"ba":0,"ma":0,"lang":0}
for cd, v in schools.items():
    if v["school_type"]!="univ4" or v.get("excluded"): continue
    fl = v.get("foreign_links", {})
    for k in cov:
        if fl.get(k): cov[k]+=1
n4 = sum(1 for v in schools.values() if v["school_type"]=="univ4" and not v.get("excluded"))
print(f"\n4년제 {n4}교 기준:")
for k, c in cov.items():
    print(f"  {k:12s}: {c}/{n4} ({c/n4*100:.0f}%)")