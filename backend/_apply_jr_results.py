import json, os, re
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 배치 결과에서 ba_foreign_url 반영
def apply_result(fname):
    try:
        d = json.load(open(fname, encoding="utf-8"))
    except: return 0
    n = 0
    for v in d:
        if not v.get("ba_foreign_url"): continue
        name = v.get("name")
        for cd, s in schools.items():
            if s["name"] == name and s["school_type"] == "junior":
                s.setdefault("foreign_links", {})["ba_foreign"] = v["ba_foreign_url"]
                n += 1
    return n

for f in ["_jr_b1a_result.json", "_jr_batch3_result.json"]:
    c = apply_result(f)
    print(f"{f}: {c}교 반영")

json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장 완료")