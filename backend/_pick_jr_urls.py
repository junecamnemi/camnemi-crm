import json, os, re
B = "."
d = json.load(open("_junior_foreign_crawl.json", encoding="utf-8"))
# 후보 중 외국인/국제/입학 관련 URL 선별
def pick(candidates):
    """외국인 학부 입학 페이지로 가장 적합한 URL 선택"""
    if not candidates: return None
    # 우선순위: 국제처/외국인 > 입시홈페이지 > 입학안내
    for c in candidates:
        u = c["url"].lower()
        t = c["text"].lower()
        if any(k in u for k in ["international", "foreign", "global", "oia", "abroad", "외국인", "국제"]):
            return c["url"]
    for c in candidates:
        u = c["url"].lower()
        if "ipsi" in u or "iphak" in u or "admission" in u or "입학" in c["text"]:
            return c["url"]
    return candidates[0]["url"]

picks = {}
for cd, v in d.items():
    if v.get("candidates"):
        u = pick(v["candidates"])
        if u:
            picks[v["name"]] = u

print(f"선별된 외국인/입학 URL: {len(picks)}교")
for n, u in picks.items():
    print(f"  {n}: {u[:65]}")
json.dump(picks, open("_junior_foreign_picks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)