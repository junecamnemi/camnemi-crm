import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
adds = {
    "강남대학교": {"lang_foreign": "https://web.kangnam.ac.kr/menu/b6cdaa2d20ed253e51964ec6c6aeba1e.do?encMenuSeq=6962b3e0e6c7e477f53fd9b87bf2229a"},
    "경동대학교": {"lang_foreign": "https://global.kduniv.ac.kr/global/index.php?pCode=1621296454"},
}
for n, fl in adds.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "univ4":
            v.setdefault("foreign_links", {}).update(fl)
            print(f"{n}: {fl}")
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")