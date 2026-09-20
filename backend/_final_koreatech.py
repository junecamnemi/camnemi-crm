import json, os, re
B = "."
ba = json.load(open("_ba_foreign_urls.json", encoding="utf-8"))
ba["한국기술교육대학교"] = "https://www.koreatech.ac.kr/board.es?mid=a40301010200&bid=0046"
json.dump(ba, open("_ba_foreign_urls.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# unvcd_index에 반영
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
def norm(s): return re.sub(r"\[[^\]]+\]$","",s).replace(" ","")
for cd, v in schools.items():
    if v["school_type"]!="univ4" or v.get("excluded"): continue
    n = norm(v["name"])
    if n in ba:
        v.setdefault("foreign_links", {})["ba_foreign"] = ba[n]
json.dump(idx, open("unvcd_index.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# 최종 커버리지
cov = {"ba_foreign":0,"ma_foreign":0,"lang_foreign":0}
n4 = 0
for cd, v in schools.items():
    if v["school_type"]!="univ4" or v.get("excluded"): continue
    n4 += 1
    fl = v.get("foreign_links", {})
    for k in cov:
        if fl.get(k): cov[k]+=1
print(f"4년제 {n4}교 최종:")
for k, c in cov.items():
    print(f"  {k:12s}: {c}/{n4} ({c/n4*100:.0f}%)")