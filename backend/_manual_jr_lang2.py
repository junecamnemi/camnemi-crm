import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "신구대학교": "https://global.shingu.ac.kr/cms/FR_CON/index.do?MENU_ID=200",
    "용인예술과학대학교": "https://ate.ysc.ac.kr/global/CMS/Board/Board.do?mCode=MN047",
    "충청대학교": "https://www.ok.ac.kr/www/contents.do?key=5695",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")