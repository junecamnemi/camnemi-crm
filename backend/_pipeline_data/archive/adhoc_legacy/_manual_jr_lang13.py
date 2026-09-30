import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "대구과학대학교": "https://global.tsu.ac.kr/torg/contents/sub/835",
    "두원공과대학교": "https://global.doowon.ac.kr/info/korean/kr/courses",
    "부산과학기술대학교": "http://kj.bist.ac.kr/pub/sub07/01.php",
    "오산대학교": "https://www.osan.ac.kr/?menuno=1048",
    "전남과학대학교": "https://www.cntu.ac.kr/menu.es?mid=e30407000000",
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