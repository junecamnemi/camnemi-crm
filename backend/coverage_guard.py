# -*- coding: utf-8 -*-
"""Coverage-regression guard for the 3-layer pipeline.
Computes level×field coverage for verified_kb (source), consulting_db, data.js.
Exits non-zero (and prints REGRESSION lines) if a derived layer drops materially
below the source. Run after sync_3layer.py in cron."""
import json, re, sys, os

BASE = r"C:\Users\USER\camnemi-crm"
KB   = os.path.join(BASE, "backend", "verified_kb.json")
DB   = os.path.join(BASE, "backend", "consulting_db.json")
DATA = os.path.join(BASE, "data.js")

TOL = 0.10   # allow derived to be 10% below source before flagging

def norm(x):
    x = re.sub(r"\[.*?\]|\(.*?\)", "", str(x))
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if x.endswith(suf): x = x[:-len(suf)]; break
    if x.endswith("대") and len(x) > 1: x = x[:-1]
    return x.replace(" ","")

kb = json.load(open(KB, encoding="utf-8"))
db = json.load(open(DB, encoding="utf-8"))
c  = open(DATA, encoding="utf-8").read()
s = c.find("["); d=0
for i in range(s, len(c)):
    if c[i]=="[": d+=1
    elif c[i]=="]":
        d-=1
        if d==0: data=json.loads(c[s:i+1]); break

# ---- source coverage (verified_kb) ----
src = {}
for sec, lvl in [("schools","BA"),("master","MA"),("junior","전문학사"),("lang_programs","어학연수")]:
    node = kb.get(sec, {})
    sch = node.get("schools", node) if isinstance(node, dict) else {}
    n = len(sch)
    src[lvl] = {
        "n": n,
        "tuition": sum(1 for v in sch.values() if v.get("tuition_semester") or v.get("tuition") or v.get("tuition_min") or v.get("tuition_range")),
        "scholarship": sum(1 for v in sch.values() if v.get("scholarships") or v.get("scholarships_categorized") or v.get("scholarship_curated") or v.get("scholarships_verified")),
        "period": sum(1 for v in sch.values() if v.get("period")),
    }

# ---- derived coverage ----
der = {}
lvlmap = {"BA":"BA","MA":"MA","전문학사":"전문학사","어학연수":"어학연수"}
der = {l:{"n":0,"tuition":0,"scholarship":0,"period":0} for l in lvlmap}
for name, sc in db["schools"].items():
    for lvl in lvlmap:
        p = sc.get("programs",{}).get(lvl)
        if not p: continue
        der[lvl]["n"] += 1
        if p.get("tuition"): der[lvl]["tuition"] += 1
        if p.get("scholarship"): der[lvl]["scholarship"] += 1
        if p.get("period"): der[lvl]["period"] += 1

djs = {"BA":{"n":0,"tuition":0,"scholarship":0,"period":0},
       "junior":{"n":0,"tuition":0,"scholarship":0,"period":0}}
for u in data:
    typ = u.get("type")
    key = "BA" if typ=="univ" else ("junior" if typ=="junior" else None)
    if not key: continue
    djs[key]["n"] += 1
    t = u.get("tuition")
    if isinstance(t, dict) and (t.get("ba") or t.get("ma")): djs[key]["tuition"] += 1
    if u.get("scholarships"): djs[key]["scholarship"] += 1
    if u.get("period"): djs[key]["period"] += 1

regressions = []
def check(level_label, src_stat, der_stat, der_name):
    for f in ["tuition","scholarship","period"]:
        sv, dv = src_stat.get(f,0), der_stat.get(f,0)
        if sv == 0: continue
        if dv < sv * (1 - TOL):
            regressions.append(f"{der_name} [{level_label}].{f}: {dv} < source {sv} (missing {sv-dv})")

for lvl, alias in [("BA","BA"),("MA","MA")]:
    check(lvl, src[lvl], der[lvl], "consulting_db")
check("전문학사", src["전문학사"], der["전문학사"], "consulting_db")
check("어학연수", src["어학연수"], der["어학연수"], "consulting_db")
check("BA", src["BA"], djs["BA"], "data.js")
check("전문학사", src["전문학사"], djs["junior"], "data.js")

print("=== 3-layer coverage ===")
for l in ["BA","MA","전문학사","어학연수"]:
    print(f"src {l}: n={src[l]['n']} tuition={src[l]['tuition']} sch={src[l]['scholarship']} period={src[l]['period']}")
for l in ["BA","MA","전문학사","어학연수"]:
    print(f"db  {l}: n={der[l]['n']} tuition={der[l]['tuition']} sch={der[l]['scholarship']} period={der[l]['period']}")
for l in ["BA","junior"]:
    print(f"js  {l}: n={djs[l]['n']} tuition={djs[l]['tuition']} sch={djs[l]['scholarship']} period={djs[l]['period']}")

if regressions:
    print("\nREGRESSION DETECTED:")
    for r in regressions: print("  !", r)
    sys.exit(1)
print("\nNo coverage regression.")
