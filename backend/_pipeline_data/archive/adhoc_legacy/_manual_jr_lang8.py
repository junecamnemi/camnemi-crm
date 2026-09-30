import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "경북전문대학교": "https://lifelong.kbc.ac.kr/bbs/content.php?co_id=menu02_05",
    "경인여자대학교": "https://suborg.kiwu.ac.kr/international/cms/FR_CON/index.do?MENU_ID=120&CONTENTS_NO=3",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")