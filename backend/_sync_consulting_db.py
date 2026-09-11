#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync consulting_db from the updated verified_kb (fill-only, enrichment preserved).

Rebuilding with _build_consulting_db.py DROPS popular_majors/similar_majors (364+348),
so we patch in place: for each school/program, fill majors/period/topik/ielts from
verified_kb only when consulting_db lacks it. Enrichment is never touched.

Usage: python _sync_consulting_db.py [--write]
"""
import json, os, re, argparse, shutil, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
CDB = os.path.join(B, "consulting_db.json")

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

LEVEL_MAP = {"BA": ("schools", None), "MA": ("master", "schools"),
             "전문학사": ("junior", "schools"), "어학연수": ("lang_programs", "schools")}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); a = ap.parse_args()
    kb = json.load(open(KB, encoding="utf-8"))
    cdb = json.load(open(CDB, encoding="utf-8"))

    # index verified_kb per level
    src = {}
    for lvl, (sec, sub) in LEVEL_MAP.items():
        d = kb[sec][sub] if sub else kb[sec]
        src[lvl] = {norm(k): (k, v) for k, v in d.items()}

    stats = {lvl: {"matched": 0, "majors": 0, "period": 0, "lang": 0} for lvl in LEVEL_MAP}
    for name, sch in cdb["schools"].items():
        for lvl, prog in (sch.get("programs") or {}).items():
            if lvl not in src:
                continue
            key = norm(name)
            hit = src[lvl].get(key)
            if not hit:
                for k2, (orig, v) in src[lvl].items():
                    if key and (key in k2 or k2 in key):
                        hit = (orig, v); break
            if not hit:
                continue
            stats[lvl]["matched"] += 1
            v = hit[1]
            # majors (fill-only)
            if not prog.get("majors"):
                m = v.get("majors") or v.get("majors_ba") or v.get("majors_sample")
                if m:
                    prog["majors"] = m; stats[lvl]["majors"] += 1
                    prog.setdefault("_kb_sync", {})["majors"] = "verified_kb"
            # period
            if not prog.get("period") and v.get("period"):
                prog["period"] = v["period"]; stats[lvl]["period"] += 1
                prog.setdefault("_kb_sync", {})["period"] = "verified_kb"
            # topik / ielts (fill-only) — 어학연수는 입학요건 아님
            if lvl != "어학연수":
                for f, kf in (("topik", "topik_req"), ("ielts", "ielts_req")):
                    if not prog.get(f) and v.get(kf):
                        prog[f] = v[kf]; stats[lvl]["lang"] += 1
                        prog.setdefault("_kb_sync", {})[f] = "verified_kb"

    print("=== consulting_db 동기화 (fill-only) ===")
    for lvl, s in stats.items():
        print(f"  {lvl}: matched {s['matched']} | majors +{s['majors']} | period +{s['period']} | 요건 +{s['lang']}")
    # preserve check
    pm = sum(1 for sch in cdb["schools"].values() for pv in (sch.get("programs") or {}).values() if pv.get("popular_majors"))
    print(f"  popular_majors 유지: {pm} (기대 364)")

    if a.write:
        shutil.copy(CDB, CDB.replace(".json", f"_bak_sync_{datetime.date.today()}.json"))
        open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
        print("저장:", CDB)

if __name__ == "__main__":
    main()
