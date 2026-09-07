#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1. Fix erroneous student counts in data.js (을지대 412 -> 5641 verified via Wikipedia).
2. Build an exclusion set: 신학대/교육대 + 학생수 < 2000.
3. Apply exclusion to verified_kb.json (add 'excluded' flag + reason) and save a clear report."""
import re, json, os

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"
KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"

# --- 1. fix student counts (verified from Wikipedia / official sources) ---
STU_FIXES = {
    "을지대학교": 5641,  # 위키백과 2022 학부생 5,641명 (대전+성남+의정부 3캠퍼스)
}

# --- 2. exclusion rules ---
# theological colleges: name contains these markers (신학대/장신대/성서대/침례신학/감리교신학/루터대/총신대/신학/성결대)
THEO_MARKERS = ["신학대", "장신대", "성서대", "침례신학", "감리교신학", "루터대", "총신대", "신학", "기독대"]
# education universities: name contains 교육대 (한국교원대 is 교육 특화 국립대 - include; 한국기술교육대 is ENGINEERING - keep)
EDU_MARKERS = ["교육대", "한국교원대"]
# Catholic comprehensive univs to KEEP (they are not theological-only)
KEEP_CATHOLIC = ["가톨릭대학교", "대구가톨릭대학교", "부산가톨릭대학교", "가톨릭꽃동네대학교"]
# schools NOT to exclude despite markers/student-count (comprehensive/special univs)
KEEP_OVERRIDE = ["성결대학교", "한국기술교육대학교", "포항공과대학교", "한국과학기술원"]
STU_MIN = 2000

# --- apply fixes to data.js ---
with open(DATA_FILE, encoding="utf-8") as f:
    content = f.read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[":
        depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            data = json.loads(content[start : i + 1])
            break

for u in data:
    if u.get("n") in STU_FIXES:
        old = u.get("stu")
        u["stu"] = STU_FIXES[u["n"]]
        print(f"학생수 보정: {u['n']} {old} → {STU_FIXES[u['n']]}")

# write back data.js
d = 0
end = -1
for i in range(start, len(content)):
    if content[i] == "[":
        d += 1
    elif content[i] == "]":
        d -= 1
        if d == 0:
            end = i + 1
            break
new_content = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end:]
with open(DATA_FILE, "w", encoding="utf-8") as f:
    f.write(new_content)
print("data.js 저장 완료")

# --- 3. build exclusion set from data.js ---
excluded = {}  # name -> reason
for u in data:
    n = u.get("n", "")
    if n in KEEP_CATHOLIC or n in KEEP_OVERRIDE:
        continue
    reasons = []
    if any(m in n for m in THEO_MARKERS):
        reasons.append("신학대")
    if any(m in n for m in EDU_MARKERS):
        reasons.append("교육대")
    stu = u.get("stu")
    if stu is not None and stu < STU_MIN:
        reasons.append(f"학생수 {stu}명 (<{STU_MIN})")
    if reasons:
        excluded[n] = reasons

print(f"\n=== 제외 대상: {len(excluded)}개 ===")
for n, r in excluded.items():
    print(f"  {n}: {', '.join(r)}")

# --- 4. apply to verified_kb.json ---
with open(KB, encoding="utf-8") as f:
    kb = json.load(f)

def mark_excluded(schools_dict):
    cnt = 0
    # reset any previous exclusion flags first
    for name, s in schools_dict.items():
        s.pop("excluded", None)
        s.pop("exclude_reason", None)
    for name, s in schools_dict.items():
        base = name.replace("(ERICA)", "").strip()
        # match: exact match first; fuzzy only if unambiguous (avoid 가톨릭대학교 vs 광주가톨릭대학교)
        matched = None
        if base in excluded:
            matched = base
        else:
            # fuzzy: only when the EXCLUDED name is a substring of the KB school name
            # (excluded name inside base). Never the reverse — prevents "가톨릭대학교"
            # (KB) from matching "광주가톨릭대학교" (excluded).
            for ex_name in excluded:
                if ex_name in base:
                    matched = ex_name
                    break
        if matched:
            s["excluded"] = True
            s["exclude_reason"] = ", ".join(excluded[matched])
            cnt += 1
    return cnt

n_ba = mark_excluded(kb.get("schools", {}))
n_ma = mark_excluded(kb.get("master", {}).get("schools", {}))
n_junior = mark_excluded(kb.get("junior", {}).get("schools", {}))

# save exclusion report
report = {"excluded": {n: r for n, r in excluded.items()}}
with open(r"C:\Users\USER\camnemi-crm\backend\_exclusion_applied.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with open(KB, "w", encoding="utf-8") as f:
    json.dump(kb, f, ensure_ascii=False, indent=2)

print(f"\nKB 반영: 학부 {n_ba}개, 석사 {n_ma}개, 전문대학 {n_junior}개 제외 표시")
print("저장: backend/_exclusion_applied.json")
