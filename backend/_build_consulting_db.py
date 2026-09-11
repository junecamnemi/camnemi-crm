# -*- coding: utf-8 -*-
"""Step 1: Build the unified consulting DB schema (schools_consulting) from the
existing KB sections (schools=BA, master, junior, lang_programs).
School-centric: each school has region/rank + programs{BA,MA,전문학사,어학연수}."""
import json, re

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

ba = kb["schools"]                       # BA 학사
ma = kb["master"]["schools"]             # MA 석사
jr = kb["junior"]["schools"]             # 전문학사
lang = kb.get("lang_programs", {}).get("schools", {})  # 어학연수

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace(" ","")

# school keyed lookup across all levels
schools = {}
def get_school(name):
    sn = norm(name)
    # find existing key (exact or norm-match)
    for k in schools:
        if norm(k)==sn: return schools[k]
    s = {"name": name, "region": None, "rank": None, "programs": {}}
    schools[name] = s
    return s

# ---- BA ----
for n, v in ba.items():
    s = get_school(n)
    s["region"] = v.get("region") or v.get("loc")
    s["rank"] = v.get("rank")
    s["programs"]["BA"] = {
        "topik": v.get("topik_req") or v.get("lang_req"),
        "ielts": v.get("ielts_req"),
        "tuition": v.get("tuition_semester") or v.get("tuition_min"),
        "tuition_max": v.get("tuition_max"),
        "scholarship": v.get("scholarships"),
        "period": v.get("period"),
        "majors": v.get("majors_ba") or v.get("majors"),
        "track": v.get("track"),
        "guide_status": v.get("guide_analyzed"),
    }

# ---- MA ----
for n, v in ma.items():
    s = get_school(n)
    if not s["region"]: s["region"] = v.get("region")
    if not s["rank"]: s["rank"] = v.get("rank")
    s["programs"]["MA"] = {
        "topik": v.get("lang_req") or v.get("topik_req"),
        "ielts": v.get("ielts_req"),
        "tuition": v.get("tuition_semester") or v.get("tuition_min"),
        "tuition_max": v.get("tuition_max"),
        "scholarship": v.get("scholarships"),
        "period": v.get("period"),
        "majors": v.get("majors"),
        "n_majors": v.get("n_majors"),
        "guide_status": v.get("guide_status"),
        "scholarship_topik6": v.get("scholarship_topik6_verified"),
    }

# ---- 전문학사 ----
for n, v in jr.items():
    s = get_school(n)
    if not s["region"]: s["region"] = v.get("region")
    s["programs"]["전문학사"] = {
        "topik": v.get("topik_req") or v.get("foreign_topik"),
        "ielts": v.get("ielts_req"),
        "tuition": v.get("tuition_semester") or v.get("tuition_min"),
        "tuition_max": v.get("tuition_max") or v.get("foreign_tuition"),
        "scholarship": v.get("scholarships_categorized"),
        "period": v.get("period"),
        "majors": v.get("majors_sample"),
        "guide_url": v.get("guide_url"),
        "foreign_guide": v.get("foreign_guide"),
        "guide_type": v.get("guide_type"),
        "excluded": v.get("excluded"),
        "exclude_reason": v.get("exclude_reason"),
    }

# ---- 어학연수 ----
for n, v in lang.items():
    s = get_school(n)
    if not s["region"]: s["region"] = v.get("region")
    s["programs"]["어학연수"] = {
        "tuition": v.get("tuition_range"),
        "structure": v.get("structure"),
        "d4_eligible": v.get("d4_eligible"),
        "dorm": v.get("dorm"),
        "period": v.get("period"),
        "guide_pdf": v.get("guide_pdf"),
        "topik": v.get("topik_req"),
        "ielts": v.get("ielts_req"),
    }

# build result with meta
result = {
    "meta": {
        "note": "통합 외국인 상담 DB (2026-09-06). 학교 중심, programs{BA,MA,전문학사,어학연수}. 레벨별로 topik/ielts/tuition/scholarship/period/majors 포함.",
        "levels": ["BA","MA","전문학사","어학연수"],
    },
    "schools": schools,
}

json.dump(result, open(r"C:\Users\USER\camnemi-crm\backend\consulting_db.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
n_schools=len(schools)
n_ba=sum(1 for s in schools.values() if "BA" in s["programs"])
n_ma=sum(1 for s in schools.values() if "MA" in s["programs"])
n_jr=sum(1 for s in schools.values() if "전문학사" in s["programs"])
n_lang=sum(1 for s in schools.values() if "어학연수" in s["programs"])
print(f"통합 DB: {n_schools}개 학교")
print(f"  BA {n_ba} | MA {n_ma} | 전문학사 {n_jr} | 어학연수 {n_lang}")
