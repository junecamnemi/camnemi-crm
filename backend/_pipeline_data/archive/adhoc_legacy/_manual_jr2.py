import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 웹 검색으로 확보한 전문대 외국인 학부 URL
manual = {
    "마산대학교": "https://info.masan.ac.kr/",
    "명지전문대학": "https://eng.mjc.ac.kr/ibuilder.do?menu_idx=3204",
    "목포과학대학교": "https://www.msu.ac.kr/ipsi/board/read?boardManagementNo=1416&boardNo=3450&menuLevel=2&menuNo=499",
    "백석문화대학교": "https://ipsi.bscu.ac.kr/ipsi/2994/subview.do",
    "부산과학기술대학교": "http://kj.bist.ac.kr/pub/sub07/01.php",
    "서영대학교": "https://ci.seoyeong.ac.kr/globalsy/main.do",
    "서울예술대학교": "https://seoularts.ac.kr/eng/web/content.do?proFn=9943200",
    "수원과학대학교": "https://ipsi.ssc.ac.kr/foreigner/index.do",
    "수원여자대학교": "https://entr.swwu.ac.kr/viewer/foreigner/list.do?mno=sub01_08",
    "신구대학교": "https://global.shingu.ac.kr/",
    "신성대학교": "http://intl.shinsung.ac.kr/",
    "연성대학교": "https://dept.yeonsung.ac.kr/interedu/index.do",
    "영진전문대학": "https://oic.yju.ac.kr/guidance/admission-guide",
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
print(f"\n반영: {applied}교")

# 최종 커버리지
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("ba_foreign")]
print(f"전문대 {len(jr)} 중 학교홈페이지 URL 보유: {len(have)} ({len(have)/len(jr)*100:.0f}%)")
print("미보유:", [v["name"] for v in jr if not v.get("foreign_links",{}).get("ba_foreign")])