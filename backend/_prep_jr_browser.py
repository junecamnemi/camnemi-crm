import json, os, re
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
jr = [v for v in idx.values() if v["school_type"]=="junior" and not v.get("excluded")]
no = [v for v in jr if not v.get("foreign_links",{}).get("ba_foreign")]
print(f"미보유 전문대: {len(no)}")
# 홈페이지 도메인에서 ipsi/iphak 경로 후보 생성
out = []
for v in no:
    home = v.get("homepage") or ""
    m = re.match(r"https?://([^/]+)", home)
    domain = m.group(1) if m else ""
    out.append({"cd": v["unvCd"], "name": v["name"], "home": home, "domain": domain})
json.dump(out, open("_jr_browser_targets.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
for x in out[:20]:
    print(f"  {x['name']}: {x['domain']}")