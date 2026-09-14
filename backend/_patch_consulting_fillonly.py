# -*- coding: utf-8 -*-
"""In-place FILL-ONLY patch of consulting_db from verified_kb.
STRICT: exact normalized name match only (no fuzzy). NEVER creates a new program level.
Preserves all enrichment (popular_majors, similar_majors, toefl)."""
import json, re, shutil, datetime

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
DB = r"C:\Users\USER\camnemi-crm\backend\consulting_db.json"
shutil.copy(DB, DB.replace(".json", f"_bak_patch_{datetime.datetime.now():%Y%m%d_%H%M}.json"))

kb = json.load(open(KB, encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x = x[:-len(suf)]; break
    if x.endswith("대") and len(x) > 1: x = x[:-1]
    return x.replace(" ", "")

# strict index: norm(KB name) -> {level: record}
idx = {}
for sec, lvl in [("schools","BA"),("master","MA"),("junior","전문학사"),("lang_programs","어학연수")]:
    node = kb.get(sec, {})
    sch = node.get("schools", node) if isinstance(node, dict) else {}
    for n, v in sch.items():
        if isinstance(v, dict):
            idx.setdefault(norm(n), {})[lvl] = v

def first(*vals):
    for v in vals:
        if v: return v
    return None

filled = {}
matched = {"BA":0,"MA":0,"전문학사":0,"어학연수":0}
for name, s in db["schools"].items():
    entry = idx.get(norm(name))          # EXACT only
    if not entry: continue
    progs = s.get("programs", {})
    for lvl, v in entry.items():
        p = progs.get(lvl)               # only fill EXISTING levels
        if p is None: continue
        matched[lvl] += 1
        def fill(key, val):
            if val and not p.get(key):
                p[key] = val; return True
            return False
        ch = False
        if lvl in ("BA","MA"):
            ch |= fill("tuition", first(v.get("tuition_semester"), v.get("tuition"), v.get("tuition_min")))
            ch |= fill("scholarship", first(v.get("scholarships"), v.get("scholarships_categorized"),
                                            v.get("scholarship_curated"), v.get("scholarships_verified")))
            ch |= fill("tuition_by_dept", v.get("tuition_semester_by_dept"))
            ch |= fill("period", v.get("period"))
            ch |= fill("topik", first(v.get("topik_req"), v.get("lang_req")))
            ch |= fill("ielts", v.get("ielts_req"))
            ch |= fill("majors", first(v.get("majors_ba"), v.get("majors")))
            ch |= fill("lang_bypass", v.get("lang_bypass"))
        elif lvl == "전문학사":
            ch |= fill("tuition", first(v.get("tuition_semester"), v.get("tuition_min")))
            ch |= fill("scholarship", first(v.get("scholarships_categorized"), v.get("scholarships"), v.get("scholarship_curated")))
            ch |= fill("period", v.get("period"))
            ch |= fill("topik", first(v.get("topik_req"), v.get("foreign_topik")))
            ch |= fill("ielts", v.get("ielts_req"))
        elif lvl == "어학연수":
            ch |= fill("period", v.get("period"))
            ch |= fill("tuition", v.get("tuition_range"))
        if ch: filled[lvl] = filled.get(lvl, 0) + 1

json.dump(db, open(DB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("matched:", matched)
print("filled:", filled)
# integrity checks
for lvl in ["BA","MA","전문학사","어학연수"]:
    print(f"  {lvl} programs: {sum(1 for s in db['schools'].values() if lvl in s.get('programs',{}))}")
print("popular_majors:", sum(1 for s in db['schools'].values() for p in s.get('programs',{}).values() if p.get('popular_majors')))
