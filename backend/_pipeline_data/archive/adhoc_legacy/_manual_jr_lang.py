import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
# 전주비전대 + 어학원 PDF 있는 학교 수동 보완
manual = {
    "전주비전대학교": "http://www.jvision.ac.kr?menu=281",
    "김포대학교": "https://global.ukp.ac.kr/",
    "대림대학교": "https://dept.daelim.ac.kr/DLkli/index.do",
    "명지전문대학": "https://mjklec.mjc.ac.kr/",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")