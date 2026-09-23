# -*- coding: utf-8 -*-
"""Canonical 3-layer sync: verified_kb (source) → consulting_db → data.js.
SAFE: fill-only for consulting_db (preserves enrichment), exact normalized matching,
per-field guards, junior branch included, special sections injected.
Idempotent — safe to run in cron.
"""
import json, re, io, shutil, datetime, sys, subprocess, os

BASE = r"C:\Users\USER\camnemi-crm"
KB   = os.path.join(BASE, "backend", "verified_kb.json")
DB   = os.path.join(BASE, "backend", "consulting_db.json")
DATA = os.path.join(BASE, "data.js")

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

kb = json.load(open(KB, encoding="utf-8"))

# ---------- 1. consulting_db (fill-only) ----------
db = json.load(open(DB, encoding="utf-8"))
shutil.copy(DB, DB.replace(".json", f"_bak_sync_{datetime.datetime.now():%Y%m%d_%H%M}.json"))

idx = {}
for sec, lvl in [("schools","BA"),("master","MA"),("junior","전문학사"),("lang_programs","어학연수")]:
    node = kb.get(sec, {})
    sch = node.get("schools", node) if isinstance(node, dict) else {}
    for n, v in sch.items():
        if isinstance(v, dict):
            idx.setdefault(norm(n), {})[lvl] = v

cdb_filled = {}
for name, s in db["schools"].items():
    entry = idx.get(norm(name))
    if not entry: continue
    progs = s.get("programs", {})
    for lvl, v in entry.items():
        p = progs.get(lvl)
        if p is None: continue
        def fill(k, val):
            if val and not p.get(k): p[k] = val; return True
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
        if ch: cdb_filled[lvl] = cdb_filled.get(lvl, 0) + 1
    # school-level IEQAS 인증대 필드 (fill-only)
    for lvl, v in entry.items():
        if v.get("ieqas_certified") is not None and s.get("ieqas_certified") is None:
            s["ieqas_certified"] = v.get("ieqas_certified")
            s["ieqas_level"] = v.get("ieqas_level")
            s["ieqas_course"] = v.get("ieqas_course")
            s["ieqas_source"] = v.get("ieqas_source")
            s["ieqas_year"] = v.get("ieqas_year")
            break

with io.open(DB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(db, f, ensure_ascii=False, indent=1)
print("[consulting_db] filled:", cdb_filled)

# ---------- 2. data.js ----------
rc = subprocess.call([sys.executable, os.path.join(BASE,"backend","_sync_datajs_v3.py")])
print("[data.js] sync rc =", rc)

# ---------- 3. normalize line endings (keep diffs clean) ----------
for path, ind in [(KB,1),(DB,1)]:
    obj = json.load(open(path, encoding="utf-8"))
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=ind)
print("[format] normalized LF")
print("3-layer sync complete")
