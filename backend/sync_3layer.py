# -*- coding: utf-8 -*-
"""Canonical 3-layer sync: verified_kb (source) → consulting_db → data.js.
SAFE: fill-only for consulting_db (preserves enrichment), exact normalized matching,
per-field guards, junior branch included, special sections injected.
Idempotent — safe to run in cron.
"""
import json, re, io, shutil, datetime, sys, subprocess, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

# Values that are placeholders, not a real schedule (never copy one into consulting_db).
PLACEHOLDERS = {"미기재", "정보 없음", "정보없음", "미정", "-", "없음", "unknown", "",
                "해당없음", "추후 안내", "미공개", "미상", "n/a", "null"}

kb = json.load(open(KB, encoding="utf-8"))

# ---------- 1. consulting_db (fill-only) ----------
db = json.load(open(DB, encoding="utf-8"))
shutil.copy(DB, DB.replace(".json", f"_bak_sync_{datetime.datetime.now():%Y%m%d_%H%M}.json"))

CAMPUS_RE = re.compile(r"[\(\[]\s*(ERICA|글로컬|GLOCAL|세종|제\d캠퍼스|분교|캠퍼스)")

idx = {}          # loose key (suffix-stripped): the 본교 row wins over campus variants
idx_exact = {}    # punctuation-stripped key: keeps (ERICA)/(글로컬)/(세종) apart
for sec, lvl in [("schools","BA"),("master","MA"),("junior","전문학사"),("lang_programs","어학연수")]:
    node = kb.get(sec, {})
    sch = node.get("schools", node) if isinstance(node, dict) else {}
    for n, v in sch.items():
        if not isinstance(v, dict):
            continue
        idx_exact.setdefault(re.sub(r"[^가-힣A-Za-z0-9]", "", str(n)), {})[lvl] = v
        k = norm(n)
        cur = idx.setdefault(k, {})
        if lvl in cur and CAMPUS_RE.search(str(n)):
            # 한양대학교(ERICA)/건국대학교(글로컬)/고려대학교(세종) all collapse to the same
            # loose key; without this guard whichever row iterates last silently supplies the
            # 본교 node with another campus's data.
            continue
        cur[lvl] = v

cdb_filled = {}
cdb_period_refreshed = {}
for name, s in db["schools"].items():
    entry = idx_exact.get(re.sub(r"[^가-힣A-Za-z0-9]", "", str(name))) or idx.get(norm(name))
    if not entry: continue
    progs = s.get("programs", {})
    for lvl, v in entry.items():
        p = progs.get(lvl)
        if p is None:
            if lvl == "어학연수":
                # KB holds a Korean-course row for this school but the consulting entry
                # never had the program node — create it so the data is visible
                p = progs.setdefault(lvl, {})
            else:
                continue
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
        # Year-aware refresh: fill-only can never correct a value that came from LAST year's
        # guide, so 전북대 kept serving "2026 early term: Round 1 9.22~10.3 / Round 2 11.5~19"
        # while the KB already held the 2027 dates. When the KB row was rebuilt from a newer
        # guide year than this consulting node was synced from, refresh `period` only — and
        # only when the new value is a real date range that does not move the schedule
        # backwards. Curated fields (majors, scholarship, popular_majors, tuition, topik/ielts
        # prose) are never overwritten by this path.
        m_ky = re.search(r"(20\d\d)", str(v.get("guide_year") or ""))
        kb_year = m_ky.group(1) if m_ky else ""
        m_cy = re.search(r"(20\d\d)", str(p.get("guide_year") or ""))
        cur_year = m_cy.group(1) if m_cy else ""
        if kb_year and kb_year > cur_year:
            newp = v.get("period")
            oldp = p.get("period")
            if isinstance(newp, str) and newp.strip() and newp.strip() not in PLACEHOLDERS:
                ny = [int(y) for y in re.findall(r"(20\d\d)", newp)]
                oy = [int(y) for y in re.findall(r"(20\d\d)", str(oldp or ""))]
                if ny and oy and max(ny) >= max(oy) and oldp != newp:
                    p["period"] = newp
                    ch = True
                    cdb_period_refreshed[lvl] = cdb_period_refreshed.get(lvl, 0) + 1
            p["guide_year"] = kb_year
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
print("[consulting_db] period refreshed from newer guide year:", cdb_period_refreshed)

# ---------- 2. data.js ----------
rc = subprocess.call([sys.executable, os.path.join(BASE, "backend", "_sync_datajs_v3.py")])
print("[data.js] sync rc =", rc)
if rc != 0:
    raise SystemExit("data.js sync failed; refusing to report successful 3-layer sync")

# ---------- 3. normalize line endings (keep diffs clean) ----------
for path, ind in [(KB,1),(DB,1)]:
    obj = json.load(open(path, encoding="utf-8"))
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=ind)
print("[format] normalized LF")
print("3-layer sync complete")
