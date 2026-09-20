import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
no = [v for v in jr if not v.get("foreign_links",{}).get("ba_foreign")]
out = [{"cd": v["unvCd"], "name": v["name"], "home": v.get("homepage")} for v in no]
print("미보유 전문대:", len(out))
# 3개 배치
import math
n = math.ceil(len(out)/3)
for i in range(3):
    part = out[i*n:(i+1)*n]
    json.dump(part, open(f"_jr_ws_batch{i+1}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  batch{i+1}: {len(part)}")
