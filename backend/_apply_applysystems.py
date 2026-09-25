#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mirror the DeepSeek-Pro application-system classification into verified_kb + consulting_db."""
import json, os, re, shutil, datetime

B = r"C:\Users\wisew\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json"); CDB = os.path.join(B, "consulting_db.json")
AGG = os.path.join(B, "_apply_pro_agg.json")

def norm(s):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", str(s or "")).replace("대학교", "").replace("대학", "")

agg = json.load(open(AGG, encoding="utf-8"))
LEVEL_MAP = {"학부": ["schools", None], "전문대": ["junior", "schools"],
             "대학원": ["master", "schools"], "어학연수": ["lang_programs", "schools"]}

kb = json.load(open(KB, encoding="utf-8"))
shutil.copy(KB, KB.replace(".json", f"_bak_applysys_{datetime.date.today()}.json"))

def get_section(kb, spec):
    if spec[1] is None:
        return kb[spec[0]]
    return kb[spec[0]][spec[1]]

applied = 0
for lvl, info in agg.items():
    spec = LEVEL_MAP.get(lvl)
    if not spec:
        continue
    sec = get_section(kb, spec)
    idx = {}
    for k in sec:
        idx.setdefault(norm(k), k)
    for s, v in info.get("schools", {}).items():
        key = idx.get(norm(s))
        if not key:
            continue  # name mismatch
        ent = sec[key]
        prim = v.get("primary")
        if prim and prim != "미기재":
            ent["apply_system"] = prim
            ent["apply_system_all"] = v.get("all") or [prim]
            if v.get("ev"):
                ent["apply_evidence"] = v["ev"]
            ent["apply_source"] = "LLM(pro)-scan 2026-09-12"
            applied += 1

open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")
print(f"verified_kb 반영: {applied}개교 apply_system 추가")

# mirror to consulting_db
cdb = json.load(open(CDB, encoding="utf-8"))
c_applied = 0
for lvl, info in agg.items():
    for s, v in info.get("schools", {}).items():
        if not v.get("primary") or v["primary"] == "미기재":
            continue
        # find in cdb
        for name, ent in cdb["schools"].items():
            if norm(name) == norm(s):
                if "프로그램" not in ent:
                    ent["apply_system"] = v["primary"]
                    c_applied += 1
                break
open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")
print(f"consulting_db 반영: {c_applied}개교 apply_system 추가")