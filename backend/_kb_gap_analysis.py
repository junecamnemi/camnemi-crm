# -*- coding: utf-8 -*-
"""Identify gaps: schools whose foreigner admission data is incomplete/missing.
For MA: compare KB master vs local grad-guide folder vs known foreigner-guide sources.
For BA/junior/lang: check KB field coverage. Output a gap report + batch list."""
import json, os, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

# ---- MA gaps: schools in KB master lacking lang_req/tuition/scholarship ----
ma = kb["master"]["schools"]
ma_gaps = []
for n, v in ma.items():
    missing = [f for f in ["lang_req","tuition","tuition_semester","scholarships","period"] if not v.get(f)]
    if len(missing) >= 2:
        ma_gaps.append({"school": n, "missing": missing, "region": v.get("region")})
print(f"MA 데이터 불완전(2+ 필드 누락): {len(ma_gaps)}개")

# ---- BA gaps ----
ba = kb["schools"]
ba_gaps = []
for n, v in ba.items():
    missing = [f for f in ["topik_req","ielts_req","tuition_semester","period","majors_ba"] if not v.get(f)]
    if len(missing) >= 2:
        ba_gaps.append({"school": n, "missing": missing, "region": v.get("region")})
print(f"BA 데이터 불완전(2+ 필드 누락): {len(ba_gaps)}개")

# ---- junior gaps (foreign_guide not obtained) ----
jr = kb["junior"]["schools"]
jr_gaps = [{"school": n, "fg": v.get("foreign_guide","missing")} for n,v in jr.items() if v.get("foreign_guide","missing") != "obtained"]
print(f"전문학사 외국인전형 미확보: {len(jr_gaps)}개")

# save gap report
gap = {"ma": ma_gaps, "ba": ba_gaps, "junior": jr_gaps}
json.dump(gap, open(r"C:\Users\USER\camnemi-crm\backend\_kb_gap_report.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("갭 리포트 저장: _kb_gap_report.json")
print()
print("=== MA 불완전 샘플 ===")
for g in ma_gaps[:25]: print(f"  {g['school']}: {g['missing']}")
