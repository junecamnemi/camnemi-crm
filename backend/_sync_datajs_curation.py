# -*- coding: utf-8 -*-
"""Update data.js from curated KB entries (46 schools: BA 35 + MA 11).
For each school in the curation outputs, sync:
  - req.topik/req.ielts (parse from lang_req when KB has numeric)
  - scholarships[] structured from scholarship_curated (types/enroll/existing)
  - period (KB 'period' field) — data.js entries may lack it; add 'period' field
Writes data.js back (preserving window.UNIV_KNOWLEDGE = [...] wrapper).
"""
import json, re, os

DATA = r"C:\Users\USER\camnemi-crm\data.js"
BASE = r"C:\Users\USER\camnemi-crm\backend"
KB = json.load(open(os.path.join(BASE, "verified_kb.json"), encoding="utf-8"))

# curation output files (source of truth for these 46 schools)
CURATION_FILES = [
    "_curation_out_batch0.json", "_curation_out_batch1.json",
    "_curation_out_batch2.json", "_curation_out_batch3.json",
    "_curation_ma_out_batch0.json", "_curation_ma_out_batch1.json",
]

curated = {}  # name -> {level, period, lang_req, tuition, sch_enroll, sch_existing, types}
for cf in CURATION_FILES:
    fp = os.path.join(BASE, cf)
    if not os.path.exists(fp):
        continue
    for e in json.load(open(fp, encoding="utf-8")):
        name = re.sub(r"^\d+_", "", e.get("school", "")).strip()
        curated.setdefault(name, {"level": "ma" if "ma_" in cf else "ba"})
        curated[name].update({
            "period": e.get("period"),
            "lang_req": e.get("lang_req"),
            "tuition": e.get("tuition_semester"),
            "sch_enroll": e.get("scholarship_enroll") or [],
            "sch_existing": e.get("scholarship_existing") or [],
            "sch_types": e.get("scholarship_types") or [],
        })

# read data.js
content = open(DATA, encoding="utf-8").read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[": depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            end = i
            break
data = json.loads(content[start:end + 1])

# map KB school name -> data.js entry (for MA schools, they exist under univ type too)
dn = {u.get("n"): u for u in data}
def parse_topik(lr):
    m = re.search(r"TOPIK\s*(\d+)\s*급", lr or "")
    return int(m.group(1)) if m else None

def parse_ielts(lr):
    m = re.search(r"IELTS\s*(\d+\.?\d*)", lr or "")
    return float(m.group(1)) if m else None

def to_amount_str(s):
    s = str(s)
    if "→" in s or "%" in s:
        return s
    return s

updated, added_period, added_req = [], 0, 0
for name, c in curated.items():
    u = dn.get(name)
    if not u:
        continue
    # 1) period field
    if c.get("period") and not u.get("period"):
        u["period"] = c["period"]
        added_period += 1
    # 2) req.topik / req.ielts — only fill if currently null/missing (don't clobber verified req)
    req = u.setdefault("req", {})
    lr = c.get("lang_req")
    if lr:
        tp = parse_topik(lr)
        il = parse_ielts(lr)
        # only fill if not already set (existing req may be curated already)
        if tp and req.get("topik") in (None, 0, ""):
            req["topik"] = tp
        if il and req.get("ielts") in (None, 0, ""):
            req["ielts"] = il
    # 3) scholarships — replace ONLY if we have structured enroll/existing ladder data
    sch = u.get("scholarships") or []
    if c.get("sch_enroll") or c.get("sch_existing"):
        new_sch = []
        # convert 'TOPIK 4 → 100%' strings to tier objects
        for sec, typ in (("sch_enroll", "enroll"), ("sch_existing", "existing")):
            ladder = c.get(sec) or []
            if not ladder:
                continue
            tiers = []
            for line in ladder:
                m = re.match(r"(TOPIK|IELTS)\s*([\d.]+)\s*[→~]\s*(\d{1,3})%", line)
                if m:
                    tiers.append({
                        "score_type": m.group(1),
                        "score": int(m.group(2)) if "." not in m.group(2) else float(m.group(2)),
                        "amount": f"{m.group(3)}%",
                    })
            if tiers:
                new_sch.append({
                    "name": "입학장학금" if typ == "enroll" else "재학 성적장학금",
                    "level": "undergrad" if c["level"] == "ba" else "grad",
                    "type": typ,
                    "tiers": tiers,
                })
        if new_sch:
            # merge: keep non-ladder existing scholarships, add/replace ours
            keep = [s for s in sch if not (s.get("type") in ("enroll", "existing") and s.get("tiers"))]
            u["scholarships"] = keep + new_sch
    updated.append(name)

# write back
content_out = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end + 1:]
open(DATA, "w", encoding="utf-8").write(content_out)
print(f"업데이트 {len(updated)}개 학교 | period 추가 {added_period}")
print("업데이트 목록:", updated)
