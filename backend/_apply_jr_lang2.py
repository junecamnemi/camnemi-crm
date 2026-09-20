import json, os
B = "."
d = json.load(open("_junior_lang2_crawl.json", encoding="utf-8"))
idx = json.load(open("unvcd_index.json", encoding="utf-8"))
schools = idx["schools"]

# 어학원 URL 선별
def pick_lang(candidates):
    for c in candidates:
        u = c["url"].lower(); t = c["text"].lower()
        if any(k in u for k in ["korean","language","klec","kli","어학","한국어","연수"]) and any(k in t for k in ["한국어","어학","language","korean","연수","교육","학당"]):
            return c["url"]
    for c in candidates:
        u = c["url"].lower(); t = c["text"].lower()
        if any(k in u for k in ["korean","language","klec","kli","어학","한국어","연수"]):
            return c["url"]
    return None

applied = 0
for cd, v in d.items():
    if not v.get("candidates"): continue
    u = pick_lang(v["candidates"])
    if not u: continue
    name = v["name"]
    for c2, s in schools.items():
        if s["name"] == name and s["school_type"] == "junior":
            s.setdefault("foreign_links", {})["lang_foreign"] = u
            applied += 1
            print(f"  {name}: {u[:60]}")
            break
json.dump(idx, open("unvcd_index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n반영: {applied}교")

# 최종
jr = [v for v in schools.values() if v["school_type"]=="junior" and not v.get("excluded")]
have = [v["name"] for v in jr if v.get("foreign_links",{}).get("lang_foreign")]
print(f"전문대 어학원 URL 보유: {len(have)}/{len(jr)}")