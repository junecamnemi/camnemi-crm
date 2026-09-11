#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove inappropriate TOPIK/IELTS/TOEFL requirements from lang_programs (D-4 어학연수).

Rationale (user, 2026-09-12): a Korean-language course exists FOR learning Korean —
TOPIK/IELTS are not admission requirements. Level placement uses a placement test,
not a certificate. Any real requirement is a note, not a req field.
"""
import json, os, shutil, datetime, re

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
CDB = os.path.join(B, "consulting_db.json")
FIELDS = ["topik_req", "ielts_req", "toefl_req"]
shutil.copy(KB, KB.replace(".json", f"_bak_langfix_{datetime.date.today()}.json"))

kb = json.load(open(KB, encoding="utf-8"))
lp = kb["lang_programs"]["schools"]
removed = []
for name, v in lp.items():
    hit = {f: v[f] for f in FIELDS if f in v}
    if hit:
        # keep the fact as a note (audit), but drop the req fields
        note = v.get("lang_req_note") or ""
        v["lang_req_note"] = (f"어학연수 입학요건 아님(참고): {hit}. " + note).strip()
        for f in FIELDS:
            v.pop(f, None)
        tag = v.get("_llm_parsed") or {}
        for f in FIELDS:
            tag.pop(f, None)
        if tag: v["_llm_parsed"] = tag
        else: v.pop("_llm_parsed", None)
        removed.append((name, hit))
open(KB, "w", encoding="utf-8", newline="\n").write(json.dumps(kb, ensure_ascii=False, indent=1) + "\n")

# same cleanup in consulting_db (어학연수 program)
cdb = json.load(open(CDB, encoding="utf-8"))
n = 0
for name, s in cdb["schools"].items():
    p = (s.get("programs") or {}).get("어학연수")
    if p and any(p.get(f) for f in ("topik", "ielts")):
        p.pop("topik", None); p.pop("ielts", None)
        if isinstance(p.get("_kb_sync"), dict):
            p["_kb_sync"].pop("topik", None); p["_kb_sync"].pop("ielts", None)
        n += 1
open(CDB, "w", encoding="utf-8", newline="\n").write(json.dumps(cdb, ensure_ascii=False, indent=1) + "\n")

print(f"verified_kb 어학연수 정정: {len(removed)}건")
for nm, h in removed: print("  -", nm, h)
print(f"consulting_db 어학연수 정정: {n}건")
