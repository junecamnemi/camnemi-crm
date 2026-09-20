import json, os
B = os.path.dirname(os.path.abspath(__file__))

# 1) unvcd_index (등록유지 228) 로드
idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))["schools"]

# 2) scrape_map — 우리가 매일 감시하는 학교별 레벨 URL
smap = json.load(open(os.path.join(B, "scrape_map.json"), encoding="utf-8"))
print("=== scrape_map 레벨별 항목 ===")
from collections import Counter
lv = Counter()
for sch, v in smap.items():
    if isinstance(v, dict):
        for l in v: lv[l] += 1
print(dict(lv))

# 3) verified_kb — guide_url / foreign_guide / guide_pdf 필드 보유 여부 (레벨별)
kb = json.load(open(os.path.join(B, "verified_kb.json"), encoding="utf-8"))
def field_cover(sec, label):
    s = kb.get(sec, {})
    schools = s.get("schools", {}) if isinstance(s, dict) and "schools" in s else s
    if not isinstance(schools, dict): return
    gu = sum(1 for v in schools.values() if isinstance(v, dict) and (v.get("guide_url") or v.get("guide_pdf") or v.get("foreign_guide")))
    print(f"  {label}: 총{len(schools)} / 요강URL 보유 {gu}")
print("\n=== verified_kb 요강URL 보유 ===")
field_cover("schools", "BA 학부")
field_cover("master", "MA 대학원")
field_cover("junior", "전문대")
field_cover("lang_programs", "어학연수")

# 4) 협곡: 실제 모집요강 PDF 폴더
print("\n=== 가이드 PDF 폴더 (최상위 디렉토리) ===")
for d in sorted(os.listdir(B)):
    if os.path.isdir(os.path.join(B, d)) and ("모집요강" in d or "guide" in d.lower() or "adiga" in d):
        n = len(os.listdir(os.path.join(B, d)))
        print(f"  {d}: {n}개")