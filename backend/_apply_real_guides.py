#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the newly-collected REAL guides with PRIORITY (ARCHITECTURE: real guide > screenshot/older parse).

For each real-guide record (tier A/B, source LLM-parsed-REAL(router)):
  - set majors_full  = the guide's full major list (authoritative, overwrite)
  - set majors_sample= first 10 (if absent)
  - set period/topik/ielts only if missing (fill-only for reqs)
  - record provenance in `_llm_parsed`

Usage: python _apply_real_guides.py [--write]
"""
import json, os, re, argparse, shutil, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
REAL = os.path.join(B, "guides_llm_parsed_real.jsonl")

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

SEC = {"junior": ("junior", "schools"), "ba": ("schools", None),
       "ma": ("master", "schools"), "lang": ("lang_programs", "schools")}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); a = ap.parse_args()
    kb = json.load(open(KB, encoding="utf-8"))
    rows = [json.loads(l) for l in open(REAL, encoding="utf-8") if l.strip()]

    idx = {}
    for lvl, (s, sub) in SEC.items():
        d = kb[s][sub] if sub else kb[s]
        idx[lvl] = {norm(k): k for k in d}

    stats = {"matched": 0, "majors_over": 0, "period": 0, "req": 0, "unmatched": []}
    for r in rows:
        meta = r.get("_meta") or {}
        tier = meta.get("tier")
        src = r.get("_source") or ""
        # trust REAL guides: tier A/B, or tier unknown (parsed from a real PDF before the router)
        if "REAL" not in src or (tier not in ("A", "B") and tier is not None):
            continue
        lvl = str(r.get("program") or "").strip().lower()
        lvl = {"전문학사": "junior", "대학원": "ma", "어학연수": "lang", "학부": "ba"}.get(lvl, lvl)
        if lvl not in SEC:
            fn = str(r.get("_file") or "")
            lvl = "junior" if ("전문학사" in fn or "전문대" in fn) else ("lang" if "한국어교육" in fn else "ba")
        s, sub = SEC[lvl]
        d = kb[s][sub] if sub else kb[s]
        key = norm(r.get("school"))
        real = idx[lvl].get(key)
        if not real:
            for k2, orig in idx[lvl].items():
                if key and (key in k2 or k2 in key):
                    real = orig; break
        if not real:
            stats["unmatched"].append(r.get("school")); continue
        stats["matched"] += 1
        v = d[real]
        maj = [m for m in (r.get("majors") or []) if m]
        if maj and len(maj) >= len(v.get("majors_full") or v.get("majors_sample") or []):
            v["majors_full"] = maj
            if not v.get("majors_sample"):
                v["majors_sample"] = maj[:10]
            v.setdefault("_llm_parsed", {})["majors_full"] = f"LLM-REAL(tier{tier})"
            stats["majors_over"] += 1
        if r.get("period") and not v.get("period"):
            v["period"] = r["period"]; v.setdefault("_llm_parsed", {})["period"] = f"LLM-REAL(tier{tier})"; stats["period"] += 1
        if lvl != "lang":
            for f, kf in (("topik", "topik_req"), ("ielts", "ielts_req")):
                if r.get(f) not in (None, "") and not v.get(kf):
                    v[kf] = r[f]; v.setdefault("_llm_parsed", {})[kf] = f"LLM-REAL(tier{tier})"; stats["req"] += 1

    print("실제요강 우선 적용:", stats)
    if a.write:
        shutil.copy(KB, KB.replace(".json", f"_bak_real_{datetime.date.today()}.json"))
        open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
        print("저장:", KB)

if __name__ == "__main__":
    main()
