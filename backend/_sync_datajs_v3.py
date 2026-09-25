# -*- coding: utf-8 -*-
"""Sync verified_kb → data.js (site/bot layer) — comprehensive, safe.
- exact normalized matching only (no fuzzy)
- per-field guards (never clobber existing values)
- junior branch included (was missing → 0% period/scholarship)
- adds visa_restricted flag + window.UNIV_SPECIAL sections
"""
import json, re, shutil, datetime

DATA = r"C:\Users\wisew\camnemi-crm\data.js"
KB   = r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json"
shutil.copy(DATA, DATA + f".bak_sync_{datetime.datetime.now():%Y%m%d_%H%M}")

content = open(DATA, encoding="utf-8").read()
s = content.find("["); d = 0
for i in range(s, len(content)):
    if content[i] == "[": d += 1
    elif content[i] == "]":
        d -= 1
        if d == 0: end = i; break
data = json.loads(content[s:end+1])
tail = content[end+1:]

kb = json.load(open(KB, encoding="utf-8"))

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x = x[:-len(suf)]; break
    if x.endswith("대") and len(x) > 1: x = x[:-1]
    return x.replace(" ", "")

def first(*vals):
    for v in vals:
        if v: return v
    return None

# KB indexes
ba_idx  = {norm(n): v for n, v in kb["schools"].items()}
ma_idx  = {norm(n): v for n, v in kb["master"]["schools"].items()}
jr_idx  = {norm(n): v for n, v in kb["junior"]["schools"].items()}
lang_idx= {norm(n): v for n, v in kb.get("lang_programs", {}).get("schools", {}).items()}

# visa-restricted set (normalized)
vr = kb.get("visa_restricted_2026", {})
def _vrn(x):
    if isinstance(x, dict): x = x.get("school") or x.get("name") or ""
    return norm(x)
vr_degree = {_vrn(x) for x in (vr.get("degree_restricted") or vr.get("degree") or [])}
vr_lang   = {_vrn(x) for x in (vr.get("lang_restricted") or vr.get("lang") or [])}

upd = {"univ": {}, "junior": {}}

def bump(bucket, key):
    upd[bucket][key] = upd[bucket].get(key, 0) + 1

for u in data:
    typ = u.get("type")
    n = norm(u.get("n", ""))
    if typ == "univ":
        v = ba_idx.get(n)
        # MA tuition into the same entry (per-field guard)
        mv = ma_idx.get(n)
        if v:
            if v.get("period") and not u.get("period"):
                u["period"] = v["period"]; bump("univ", "period")
            sch = first(v.get("scholarships"), v.get("scholarships_categorized"),
                        v.get("scholarship_curated"), v.get("scholarships_verified"))
            if sch and not u.get("scholarships"):
                u["scholarships"] = sch; bump("univ", "scholarships")
            if v.get("lang_bypass") and not u.get("lang_bypass"):
                u["lang_bypass"] = v["lang_bypass"]; bump("univ", "lang_bypass")
            if v.get("tuition_semester_by_dept"):
                t = u.setdefault("tuition", {})
                bt = t.setdefault("ba", {}) if isinstance(t, dict) else None
                if isinstance(bt, dict) and not bt.get("fields"):
                    bt["fields"] = v["tuition_semester_by_dept"]["fields"]; bump("univ", "ba_by_dept")
            tv = first(v.get("tuition_semester"), v.get("tuition"), v.get("tuition_min"))
            if tv and isinstance(u.get("tuition"), dict):
                if not u["tuition"].get("ba"):
                    u["tuition"]["ba"] = tv if isinstance(tv, dict) else {"min": tv}; bump("univ", "ba_tuition")
        if mv:
            tv = first(mv.get("tuition_semester"), mv.get("tuition"), mv.get("tuition_min"))
            if tv:
                t = u.setdefault("tuition", {})
                if isinstance(t, dict) and not t.get("ma"):
                    t["ma"] = tv if isinstance(tv, dict) else {"min": tv}; bump("univ", "ma_tuition")
        # visa flag
        if n in vr_degree or n in vr_lang:
            u["visa_restricted"] = {"degree": n in vr_degree, "lang": n in vr_lang}
            bump("univ", "visa_flag")
    elif typ == "junior":
        v = jr_idx.get(n)
        if v:
            if v.get("period") and not u.get("period"):
                u["period"] = v["period"]; bump("junior", "period")
            sch = first(v.get("scholarships_categorized"), v.get("scholarships"), v.get("scholarship_curated"))
            if sch and not u.get("scholarships"):
                u["scholarships"] = sch; bump("junior", "scholarships")
            if v.get("lang_bypass") and not u.get("lang_bypass"):
                u["lang_bypass"] = v["lang_bypass"]; bump("junior", "lang_bypass")
            tv = first(v.get("tuition_semester"), v.get("tuition_min"))
            if tv and isinstance(u.get("tuition"), dict) and not u["tuition"].get("ba"):
                u["tuition"]["ba"] = tv if isinstance(tv, dict) else {"min": tv}; bump("junior", "ba_tuition")
        if n in vr_degree or n in vr_lang:
            u["visa_restricted"] = {"degree": n in vr_degree, "lang": n in vr_lang}
            bump("junior", "visa_flag")

# special sections payload
special = {
    "visa_restricted_2026": vr,
    "note_visa_restricted": "degree=true → 추천금지; lang=true → D-4만 금지(학위는 가능). 출처: 교육부·법무부 2026.2.12",
    "free_major_programs": kb.get("free_major_programs", {}),
    "ai_departments": kb.get("ai_departments", {}),
    "medical_reqs": kb.get("medical_reqs", {}),
}

new = content[:s] + json.dumps(data, ensure_ascii=False, indent=1) + tail
# append/replace UNIV_SPECIAL block
new = re.sub(r"\n*// __UNIV_SPECIAL__\nwindow\.UNIV_SPECIAL = .*?;\n", "\n", new, flags=re.S)
if "window.UNIV_SPECIAL" in new:
    new = re.sub(r"window\.UNIV_SPECIAL = .*?;\n", "", new, flags=re.S)
new = new.rstrip() + "\n\nwindow.UNIV_SPECIAL = " + json.dumps(special, ensure_ascii=False) + ";\n"

open(DATA, "w", encoding="utf-8").write(new)
print("data.js 동기화:")
for b in upd:
    print(f"  [{b}]", dict(sorted(upd[b].items(), key=lambda x: -x[1])))
print("UNIV_SPECIAL 섹션 추가 완료")
