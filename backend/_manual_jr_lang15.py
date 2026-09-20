import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "인덕대학교": "https://www.induk.ac.kr/global/cms/frCmnCon/index.do?MENU_ID=300",
}
applied = 0
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            applied += 1
            print(f"  {n}: {u[:50]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"반영: {applied}교")

# 최종
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("lang_foreign")]
print(f"전문대 어학원: {len(have)}/{len(jr)}")