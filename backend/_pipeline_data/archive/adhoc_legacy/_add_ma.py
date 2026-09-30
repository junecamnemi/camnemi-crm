import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 직접 브라우저로 확보한 ma/lang URL
adds = {
    "극동대학교": {"ma_foreign": "https://www.kdu.ac.kr/graduate/sub.do?mncd=752"},
    "나사렛대학교": {"ma_foreign": "https://grad.kornu.ac.kr/ngrad/3385/subview.do"},
}
for n, fl in adds.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "univ4":
            v.setdefault("foreign_links", {}).update(fl)
            print(f"{n}: {fl}")

json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")