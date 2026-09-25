#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""link_junior_guides.py — 전문대 요강 PDF(adiga_2026_전문대학_모집요강 149개)를 unvCd에 연결.

매칭: PDF 파일명의 학교명 → school_keys.resolve → unvcd_index.unvCd.
출력: unvcd_index.json 에 guide_field 추가 (junior_ba_guide, junior_lang_guide 등)
"""
import os, json, re, sys
sys.path.insert(0, ".")
from school_keys import resolve, resolve_short

B = os.path.dirname(os.path.abspath(__file__))
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
JR_FOLDER = os.path.join(GUIDER, "adiga_2026_전문대학_모집요강")

idx = json.load(open(os.path.join(B, "unvcd_index.json"), encoding="utf-8"))
schools = idx["schools"]
# unvCd -> name map + reverse
name_cd = {}
for cd, v in schools.items():
    base = re.sub(r"\[[^\]]+\]$", "", v["name"]).replace(" ", "")
    name_cd[base] = cd

def get_cd(name):
    base = re.sub(r"\[[^\]]+\]$", "", name).replace(" ", "")
    if base in name_cd: return name_cd[base]
    r = resolve(name)
    if r and r.replace(" ", "") in name_cd: return name_cd[r.replace(" ", "")]
    r2 = resolve_short(name)
    if r2 and r2.replace(" ", "") in name_cd: return name_cd[r2.replace(" ", "")]
    for b, cd in name_cd.items():
        if b.startswith(base[:3]): return cd
    return None

def school_from(fname):
    # 파일명에서 학교명 추출: "가톨릭상지대학교_전문학사_모집요강.pdf" -> "가톨릭상지대학교"
    m = re.match(r"([가-힣A-Za-z._]+?)(?:_전문학사|_전문|_학사|_모집요강|_guide|\.pdf)", fname)
    if m:
        return m.group(1).replace("_", "").replace(".", "")
    return None

matched = unmatched = 0
unmatched_list = []
junior_guides = {}
for fname in sorted(os.listdir(JR_FOLDER)):
    if not fname.lower().endswith(".pdf"):
        continue
    sname = school_from(fname)
    cd = get_cd(sname) if sname else None
    if not cd:
        # 파일명 전체로 매칭 시도
        cd = get_cd(fname.replace("_전문학사_모집요강.pdf", "").replace("_guide.pdf", ""))
    if cd:
        matched += 1
        junior_guides.setdefault(cd, []).append(fname)
    else:
        unmatched += 1
        unmatched_list.append(fname)

print(f"전문대 요강 PDF: 매칭 {matched} / 미매칭 {unmatched}")
print("미매칭 샘플:", unmatched_list[:12])
print()
# 등록유지 전문대 기준 커버리지
kept_jr = [cd for cd, v in schools.items() if v.get("school_type") == "junior" and not v.get("excluded")]
cov = sum(1 for cd in kept_jr if cd in junior_guides)
print(f"등록유지 전문대 {len(kept_jr)} 중 요강PDF 보유 {cov}")

# unvcd_index에 반영
for cd, files in junior_guides.items():
    if cd in schools:
        schools[cd]["junior_gaides_pdf"] = [f for f in files]
json.dump(idx, open(os.path.join(B, "unvcd_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("unvcd_index.json 에 junior_gaides_pdf 반영")