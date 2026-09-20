import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "경남정보대학교": "https://kli.kit.ac.kr/",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")