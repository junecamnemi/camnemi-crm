# -*- coding: utf-8 -*-
"""Merge structured bypass into KB — handles BOTH key formats:
   'BA:학교명' (level:school) and '학교명|BA' (school|level), plus nested bare-level."""
import json, re

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
d = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_bypass_structured.json", encoding="utf-8"))
kb = json.load(open(KB, encoding="utf-8"))

LEVELS = {"BA","MA","junior"}

def is_struct(v):
    p = v.get("paths") if isinstance(v, dict) else None
    return isinstance(p, list) and len(p) > 0 and all(isinstance(x, dict) and "type" in x for x in p)

def norm(s):
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s)
    s = re.sub(r"^\d+_", "", s)          # strip leading file-id
    for suf in ["대학원대학교","대학교","대학원","대학","전문대학","전문대"]:
        if s.endswith(suf): s = s[:-len(suf)]; break
    if s.endswith("대") and len(s) > 1: s = s[:-1]
    return s.replace(" ", "").replace("_","")

# ── 1. normalize keys → (level, school)
pairs = []
for k, v in d.items():
    if not isinstance(v, dict): continue
    # nested: key is a bare level, children are schools
    if k in LEVELS:
        for sub, sv in v.items():
            if is_struct(sv): pairs.append((k, sub, sv))
        continue
    m1 = re.match(r"^(BA|MA|junior):(.+)$", k)          # level:school
    m2 = re.match(r"^(.+)\|(BA|MA|junior)$", k)          # school|level
    if m1 and is_struct(v):
        pairs.append((m1.group(1), m1.group(2), v))
    elif m2 and is_struct(v):
        pairs.append((m2.group(2), m2.group(1), v))

# dedupe by (level, normalized school), prefer longer path list
ded = {}
for lvl, school, v in pairs:
    key = (lvl, norm(school))
    if key not in ded or len(v["paths"]) > len(ded[key][2]["paths"]):
        ded[key] = (lvl, school, v)
print(f"정규화 pairs: {len(pairs)} → dedupe: {len(ded)}")

# ── 2. merge into KB
SEC = {"BA": "schools", "MA": "master", "junior": "junior"}
added = 0; miss = []
for (lvl, sn), (_, school, v) in ded.items():
    sec = kb[SEC[lvl]]
    schools = sec.get("schools", sec)
    tgt = None
    for n in schools:
        if norm(n) == sn: tgt = n; break
    if not tgt:
        for n in schools:
            nn = norm(n)
            if len(sn) >= 3 and (nn == sn or nn.startswith(sn) or sn.startswith(nn)):
                tgt = n; break
    if not tgt:
        miss.append(f"{lvl}:{school}"); continue
    schools[tgt]["lang_bypass"] = {
        "source": "외국인 모집요강 추출 (pro model 정제)",
        "paths": v["paths"],
        **({"notes": v["notes"]} if v.get("notes") else {}),
    }
    added += 1

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"KB lang_bypass 병합: {added}개")
if miss:
    print(f"매칭실패 {len(miss)}: {miss[:15]}")
