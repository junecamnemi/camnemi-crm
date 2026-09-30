import os, re, json
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
B = os.path.dirname(os.path.abspath(__file__))

def walk_foreign(root):
    """파일명에서 unvCd_학교명[캠퍼스]_연도_타입 추출"""
    out = []
    if not os.path.isdir(root): return out
    for f in sorted(os.listdir(root)):
        if not f.lower().endswith(('.pdf','.hwp','.hwpx','.hml')): continue
        m = re.match(r"(\d{7})_(.+?)_(202[567])_(외국인|재외국민)", f)
        if m:
            out.append({"unvCd": m.group(1), "name": m.group(2), "year": m.group(3),
                        "type": m.group(4), "file": f, "path": os.path.join(root, f)})
        else:
            out.append({"file": f, "path": os.path.join(root,f), "parse":"?"})
    return out

# 수집
foreign_index = {}
def add(root, level):
    for it in walk_foreign(root):
        if "unvCd" not in it: continue
        cd = it["unvCd"]
        foreign_index.setdefault(cd, {"univ4": {}, "junior": {}})
        # 레벨 판단: 경로에 전문대 있으면 junior
        lvl = "junior" if "전문대" in it["path"] else "univ4"
        foreign_index[cd][lvl][f"{it['year']}_{it['type']}"] = it["path"]

add(os.path.join(GUIDER,"adiga_2026_외국인_모집요강","외국인"), "univ4")
add(os.path.join(GUIDER,"adiga_2027_외국인_모집요강","외국인"), "univ4")
add(os.path.join(GUIDER,"adiga_2027_외국인_모집요강","재외국민"), "univ4")  # 재외국민 별도 marked
# 전문대
jr = os.path.join(GUIDER,"adiga_2026_전문대학_모집요강")
for root,dd,ff in os.walk(jr):
    for f in ff:
        if not f.lower().endswith(('.pdf','.hwp','.hwpx')) or '외국인' not in f: continue
        m = re.match(r"(.+?)_전문학사_외국인모집요강|(.+?)_외국인", f)
        # unvCd 없는 경우 이름만
        foreign_index.setdefault("?", {"univ4":{}, "junior":{}})["junior"][f]=os.path.join(root,f)

# 통계
print("=== 외국인 요강 인덱스 ===")
n4 = sum(1 for cd,v in foreign_index.items() if v["univ4"])
nj = sum(1 for cd,v in foreign_index.items() if v["junior"])
print(f"univCd별: 4년제 요강 보유 {n4} / junior 보유 {nj} / 총 univCd {len(foreign_index)}")
# 연도별
from collections import Counter
years = Counter()
for cd,v in foreign_index.items():
    for lvl, d in v.items():
        for k in d:
            y = k.split("_")[0]
            years[(lvl, y)] += 1
print("연도×레벨:", dict(years))
# 전문대 이름매칭 위한 임시 (unvCd 없음)
no_cd = foreign_index.get("?",{})
print("전문대 (unvCd 파싱만):", len(no_cd["junior"]))

json.dump(foreign_index, open(os.path.join(B,"_foreign_guide_index.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n저장: _foreign_guide_index.json")