import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 입시홈페이지에서 외국인 링크 발견했지만 선별 못한 5교 수동 보완
manual = {
    "계명문화대학교": "https://www.kmcu.ac.kr/admission/",
    "구미대학교": "https://www.gumi.ac.kr/admission/index.htm",
    "부산보건대학교": "https://www.bhu.ac.kr/ipsi/main",
    "오산대학교": "https://www.osan.ac.kr/?menuno=976",
    "울산과학대학교": "https://www.uc.ac.kr/ipsi/CMS/Contents/Contents.do?mCode=MN022",
}
applied = 0
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["ba_foreign"] = u
            applied += 1
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"반영: {applied}교")