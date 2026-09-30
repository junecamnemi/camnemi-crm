import json, os
B = "."
# 1) 크롤 결과 21교
crawl = json.load(open("_foreign_crawl_result.json", encoding="utf-8"))
crawl_map = {v["name"]: v["ba_foreign_url"] for v in crawl if v.get("ba_foreign_url")}

# 2) master에서 ba http 보유 77교
master = json.load(open("_univ4_2027_master_links.json", encoding="utf-8"))
ba_have = {v["name"]: v["ba_url"] for v in master.values() if v.get("ba_url")}

# 3) 브라우저 직접 확인 5교
confirmed = {
    "서울대학교": "https://admission.snu.ac.kr/international/undergraduate/spring/guide",
    "연세대학교": "https://admission.yonsei.ac.kr/seoul/admission/html/international/guide.asp",
    "성균관대학교": "https://admission.skku.edu/admission/html/abroad/guide.html",
    "이화여자대학교": "https://isa.ewha.ac.kr/oisa/1442/subview.do",
    "한국외국어대학교": "https://international.hufs.ac.kr/sites/international/content",
}

# 병합 (우선순위: 크롤 > 브라우저확인 > master)
merged = {}
for n, u in ba_have.items():
    merged[n] = u
for n, u in confirmed.items():
    merged[n] = u
for n, u in crawl_map.items():
    merged[n] = u

# 등록유지 4년제 141 기준 커버리지
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
kept4 = [v["name"] for v in idx.values() if v["school_type"]=="univ4" and not v.get("excluded")]
# name 정규화
import re
def norm(s): return re.sub(r"\[[^\]]+\]$","",s).replace(" ","")
merged_norm = {norm(k): v for k, v in merged.items()}
kept_norm = {norm(n): n for n in kept4}
cov = sum(1 for n in kept_norm if n in merged_norm)
print(f"등록유지 4년제 {len(kept4)} 중 학부 외국인 URL 보유: {cov} ({cov/len(kept4)*100:.0f}%)")
# 미보유
missing = [kept_norm[n] for n in kept_norm if n not in merged_norm]
print(f"미보유 {len(missing)}교:", missing)

json.dump(merged, open("_ba_foreign_urls.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: _ba_foreign_urls.json")