import json, os
B = "."
ba = json.load(open("_ba_foreign_urls.json", encoding="utf-8"))
# 인하대 직접 확보
ba["인하대학교"] = "https://apply.inha.ac.kr/"
json.dump(ba, open("_ba_foreign_urls.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("인하대 기록:", ba["인하대학교"])
print("총:", len(ba))