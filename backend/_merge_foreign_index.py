import json, re, os, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short

B = os.path.dirname(os.path.abspath(__file__))
idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))
schools = idx["schools"]
fidx = json.load(open(os.path.join(B, "_foreign_guide_index.json"), encoding="utf-8"))

# unvCd -> 이름급 매칭용
name_cd = {}
for cd, v in schools.items():
    base = re.sub(r"\[[^\]]+\]$", "", v["name"]).replace(" ", "")
    name_cd[base] = cd

def get_cd(name):
    base = name.replace(" ", "")
    if base in name_cd: return name_cd[base]
    r = resolve(name)
    if r and r.replace(" ", "") in name_cd: return name_cd[r.replace(" ", "")]
    r2 = resolve_short(name)
    if r2 and r2.replace(" ", "") in name_cd: return name_cd[r2.replace(" ", "")]
    return None

# 4년제: unvCd 키로 직접
merged = {"univ4_foreign": {}, "junior_foreign": {}}
for cd, v in fidx.items():
    if cd == "?" or not v.get("univ4"): continue
    if cd in schools:
        merged["univ4_foreign"][cd] = v["univ4"]

# 전문대: 이름으로 매칭 (univCd 없음, "?"에 들어있던 것 + 4년제 중 junior)
# 실제 전문대 외국인은 junior 레벨이지만 인덱스가 "?"로 모음 - 재구성 필요
# adiga_2026_전문대학에서 외국인 파일을 다시 이름으로 수집
GUIDER = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
jr_root = os.path.join(GUIDER, "adiga_2026_전문대학_모집요강")
junior_foreign = {}
for root, dd, ff in os.walk(jr_root):
    for f in ff:
        if not f.lower().endswith(('.pdf','.hwp','.hwpx')) or '외국인' not in f: continue
        # 강동대학교_전문학사_외국인모집요강.pdf
        m = re.match(r"(.+?)_전문학사_외국인모집요강\.pdf", f)
        sname = m.group(1) if m else None
        cd = get_cd(sname) if sname else None
        if cd:
            junior_foreign.setdefault(cd, []).append(os.path.join(root, f))
        else:
            print("  전문대 미매칭:", f)

print(f"4년제 외국인요강 unvCd 매핑: {len(merged['univ4_foreign'])}")
print(f"전문대 외국인요강 unvCd 매핑: {len(junior_foreign)}")

# unvcd_index 반영
for cd, paths in merged["univ4_foreign"].items():
    schools[cd]["foreign_guides_4yr"] = paths
for cd, paths in junior_foreign.items():
    schools[cd]["foreign_guides_ba"] = paths

json.dump(idx, open(os.path.join(B, "unvcd_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nunvcd_index.json 반영 완료")

# 최종 커버리지 (등록유지 기준)
kept = [cd for cd, v in schools.items() if not v.get("excluded")]
ka = [cd for cd in kept if schools[cd]["school_type"]=="univ4"]
kj = [cd for cd in kept if schools[cd]["school_type"]=="junior"]
ca = sum(1 for cd in ka if schools[cd].get("foreign_guides_4yr"))
cj = sum(1 for cd in kj if schools[cd].get("foreign_guides_ba"))
print(f"\n등록유지 4년제 {len(ka)} 중 외국인요강 보유 {ca} ({ca/len(ka)*100:.0f}%)")
print(f"등록유지 전문대 {len(kj)} 중 외국인요강 보유 {cj} ({cj/len(kj)*100:.0f}%)")