import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]
manual = {
    "대경대학교": "https://international.tk.ac.kr/sub/scholar02.php",
    "안산대학교": "https://iphak.ansan.ac.kr/iphak/content/14",
    "호산대학교": "https://global.hosan.ac.kr/front/course/long.php",
    "조선이공대학교": "https://global.cst.ac.kr/",
}
for n, u in manual.items():
    for cd, v in schools.items():
        if v["name"] == n and v["school_type"] == "junior":
            v.setdefault("foreign_links", {})["lang_foreign"] = u
            print(f"  {n}: {u[:55]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")