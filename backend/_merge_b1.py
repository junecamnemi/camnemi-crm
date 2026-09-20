import json, os, re
B = "."
# 배치1 결과 20교
b1 = json.load(open("_fc_batch1_result.json", encoding="utf-8"))
b1_map = {}
for v in b1:
    if v.get("ba_foreign_url"):
        b1_map[v["name"]] = v["ba_foreign_url"]
print("배치1 확보:", len(b1_map))

# 기존 ba URL 병합
ba = json.load(open("_ba_foreign_urls.json", encoding="utf-8"))
for n, u in b1_map.items():
    ba[n] = u

# 등록유지 4년제 커버리지
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
def norm(s): return re.sub(r"\[[^\]]+\]$","",s).replace(" ","")
ba_norm = {norm(k): v for k, v in ba.items()}
kept4 = [v["name"] for v in idx.values() if v["school_type"]=="univ4" and not v.get("excluded")]
cov = sum(1 for n in kept4 if norm(n) in ba_norm)
print(f"등록유지 4년제 {len(kept4)} 중 학부 외국인 URL: {cov} ({cov/len(kept4)*100:.0f}%)")
missing = [n for n in kept4 if norm(n) not in ba_norm]
print(f"미보유 {len(missing)}교:", missing)

json.dump(ba, open("_ba_foreign_urls.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: _ba_foreign_urls.json")