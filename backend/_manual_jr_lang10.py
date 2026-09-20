import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "동아방송예술대학교": "https://klec.dima.ac.kr/kr/regular/regular_course.php",
    "대구보건대학교": "https://global.dhc.ac.kr/",
    "영진전문대학": "https://kcenter.yju.ac.kr/",
    "연성대학교": "https://dept.yeonsung.ac.kr/kschool/cms/FR_CON/index.do?MENU_ID=180",
    "인덕대학교": "https://www.induk.ac.kr/global/index.do",
    "원광보건대학교": "https://www.wu.ac.kr/sites/global/contents/menu_3937.jsp",
    "숭의여자대학교": "https://www.sewu.ac.kr/inic/korea/introduction.do",
    "신성대학교": "http://intl.shinsung.ac.kr/",
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