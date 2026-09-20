import json, os, re
B = "."
picks = json.load(open("_junior_foreign_picks.json", encoding="utf-8"))
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 부적합 URL 제외 (카카오 등)
BAD = ["kakao.com", "pf.kakao"]
applied = 0
for n, u in picks.items():
    if any(b in u for b in BAD):
        print(f"  제외(부적합): {n} -> {u[:40]}")
        continue
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["ba_foreign"] = u
            applied += 1
            break

json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"반영: {applied}교")

# 최종 커버리지
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("ba_foreign")]
print(f"전문대 {len(jr)} 중 학교홈페이지 URL 보유: {len(have)}")
print("미보유:", [v["name"] for v in jr if not v.get("foreign_links",{}).get("ba_foreign")])