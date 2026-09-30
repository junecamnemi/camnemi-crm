import json, os, re
B = "."
d = json.load(open("_junior_ipsi_probe.json", encoding="utf-8"))
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 후보에서 외국인 학부 입학 URL 선별
def pick_foreign(candidates):
    """외국인/국제/글로벌 링크 우선, 없으면 입학/모집요강"""
    for c in candidates:
        u = c["url"].lower(); t = c["text"].lower()
        if any(k in u for k in ["international","foreign","global","oia","abroad","irc","국제","글로벌","외국인"]):
            return c["url"]
    for c in candidates:
        t = c["text"].lower()
        if "국제학생" in t or "외국인" in t or "재외" in t:
            return c["url"]
    return None

applied = 0
for cd, v in d.items():
    if not v["hit_url"]: continue
    u = pick_foreign(v["candidates"])
    if not u: continue
    name = v["name"]
    for c2, s in schools.items():
        if s["name"] == name and s["school_type"] == "junior":
            s.setdefault("foreign_links", {})["ba_foreign"] = u
            applied += 1
            print(f"  {name}: {u[:60]}")
            break

json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n반영: {applied}교")

# 최종 커버리지
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("ba_foreign")]
print(f"전문대 {len(jr)} 중 학교홈페이지 URL 보유: {len(have)} ({len(have)/len(jr)*100:.0f}%)")