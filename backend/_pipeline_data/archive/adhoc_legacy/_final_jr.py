import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
# 여주대·송곡대 - 입시홈페이지 메인으로 기록 (외국인 전형은 adiga PDF로 커버)
manual = {
    "여주대학교": "https://ipsi.yit.ac.kr/",
    "송곡대학교": "https://ipsi.songgok.ac.kr/",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["ba_foreign"] = u
            print(f"  {n}: {u}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 최종 커버리지
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("ba_foreign")]
print(f"\n전문대 {len(jr)} 중 학교홈페이지 URL 보유: {len(have)} ({len(have)/len(jr)*100:.0f}%)")
print("미보유:", [v["name"] for v in jr if not v.get("foreign_links",{}).get("ba_foreign")])