# -*- coding: utf-8 -*-
"""Summarize junior college foreigner-guide acquisition status into a JSON for the
KB. Categories: has_foreign_pdf, no_public_foreign_guide, closed(폐교), merged."""
import json, os

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

def norm(s):
    s = s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
    s = s.replace("_전문학사_외국인모집요강","").replace(".pdf","")
    return s
files = [f for f in os.listdir(SAVEDIR) if f.endswith(".pdf")]
foreign_files = [f for f in files if "_외국인모집요강" in f]
foreign_have = set(norm(f) for f in foreign_files)

# No-public-foreign-guide schools (from agent reports)
no_public = ["강원도립대학교","강릉영동대학교","구미대학교","군산간호대학교","나주대학교","동아보건대학교",
             "부산예술대학교","서울여자간호대학교","세경대학교","기독간호대학교","연암공과대학교","장안대학교",
             "재능대학교","전북과학대학교","전주기전대학","창원문성대학교","포항대학교","한국관광대학교",
             "한국농수산대학교","한국영상대학교"]
closed = ["광양보건대학교"]          # 폐교 2026-08-31
merged = ["조선간호대학교"]          # 조선대 통합 (2027부터 4년제 간호대학)

status = {}
for n, v in js.items():
    sn = norm(n)
    if sn in foreign_have:
        status[n] = {"foreign_guide": "obtained"}
    elif n in closed:
        status[n] = {"foreign_guide": "closed"}
    elif n in merged:
        status[n] = {"foreign_guide": "merged"}
    elif n in no_public:
        status[n] = {"foreign_guide": "no_public_guide"}
    else:
        status[n] = {"foreign_guide": "not_checked"}

obtained = sum(1 for v in status.values() if v["foreign_guide"]=="obtained")
nopub = sum(1 for v in status.values() if v["foreign_guide"]=="no_public_guide")
print(f"외국인 요강 확보: {obtained}")
print(f"공개 요강 없음: {nopub}")
print(f"폐교: {len(closed)} | 통합: {len(merged)} | 미확인: {sum(1 for v in status.values() if v['foreign_guide']=='not_checked')}")
json.dump(status, open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_status.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장: _junior_foreign_status.json")
