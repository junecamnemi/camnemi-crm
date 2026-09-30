import json, os, re
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
ba = json.load(open("_ba_foreign_urls.json", encoding="utf-8"))
def norm(s): return re.sub(r"\[[^\]]+\]$","",s).replace(" ","")
ba_norm = {norm(k): v for k, v in ba.items()}
# 미보유 39교의 출발 URL
targets = []
for cd, v in idx.items():
    if v["school_type"]!="univ4" or v.get("excluded"): continue
    n = norm(v["name"])
    if n in ba_norm: continue
    targets.append({"cd": cd, "name": v["name"], "ipsi": v.get("ipsi_homepage"), "home": v.get("homepage")})
print("미보유:", len(targets))
json.dump(targets, open("_foreign_crawl_targets2.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: _foreign_crawl_targets2.json")