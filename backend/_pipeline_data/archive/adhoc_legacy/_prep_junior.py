import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
out = [{"cd": v["unvCd"], "name": v["name"], "home": v.get("homepage")} for v in jr]
json.dump(out, open("_junior_crawl_targets.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("전문대 대상:", len(out))