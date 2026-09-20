import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

def apply(fname):
    try:
        d = json.load(open(fname, encoding="utf-8"))
    except: return 0
    n = 0
    for v in d:
        if not v.get("ba_foreign_url"): continue
        name = v.get("name")
        for cd, s in schools.items():
            if s["name"] == name and s["school_type"] == "junior":
                s.setdefault("foreign_links", {})["ba_foreign"] = v["ba_foreign_url"]
                n += 1
                break
    return n

for f in ["_jr_ws2_batch1_result.json", "_jr_ws2_batch2_result.json", "_jr_ws2_batch3_result.json"]:
    c = apply(f)
    print(f"{f}: {c}교 반영")

json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 최종 커버리지
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("ba_foreign")]
print(f"\n전문대 {len(jr)} 중 학교홈페이지 URL 보유: {len(have)} ({len(have)/len(jr)*100:.0f}%)")
print("미보유:", [v["name"] for v in jr if not v.get("foreign_links",{}).get("ba_foreign")])