# -*- coding: utf-8 -*-
"""Sync MA curated data into data.js — map short curator names to full data.js school names."""
import json, re, os

DATA = r"C:\Users\USER\camnemi-crm\data.js"
BASE = r"C:\Users\USER\camnemi-crm\backend"

# MA curation: short name -> (matching data.js name, period, lang_req, enroll, existing)
MA_FILES = ["_curation_ma_out_batch0.json", "_curation_ma_out_batch1.json"]
curated = []
for cf in MA_FILES:
    fp = os.path.join(BASE, cf)
    if not os.path.exists(fp):
        continue
    for e in json.load(open(fp, encoding="utf-8")):
        curated.append(e)

# map short -> full school name
SHORT2FULL = {
    "가톨릭대": "가톨릭대학교", "국민대": "국민대학교", "인제대": "인제대학교",
    "전주대": "전주대학교", "제주국제대": "제주국제대학교", "조선대": "조선대학교",
    "중부대": "중부대학교", "창신대": "창신대학교", "청주대": "청주대학교",
    "초당대": "초당대학교", "충북대": "충북대학교",
}

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
dn = {u.get("n"): u for u in data}

def parse_topik(lr):
    m = re.search(r"TOPIK\s*(\d+)\s*급", lr or "")
    return int(m.group(1)) if m else None

def parse_ielts(lr):
    m = re.search(r"IELTS\s*(\d+\.?\d*)", lr or "")
    return float(m.group(1)) if m else None

n_updated = 0
for e in curated:
    short = e.get("school", "")
    full = SHORT2FULL.get(short, short)
    u = dn.get(full)
    if not u:
        print(f"  SKIP {full} (not in data.js)")
        continue
    # period (only if missing)
    if e.get("period") and not u.get("period"):
        u["period"] = e["period"]
    # req fill if missing
    req = u.setdefault("req", {})
    lr = e.get("lang_req")
    if lr:
        tp, il = parse_topik(lr), parse_ielts(lr)
        if tp and req.get("topik") in (None, 0, ""):
            req["topik"] = tp
        if il and req.get("ielts") in (None, 0, ""):
            req["ielts"] = il
    # scholarships: add structured grad tiers
    if e.get("scholarship_enroll") or e.get("scholarship_existing"):
        sch = u.get("scholarships") or []
        new_tiers = []
        for sec, typ in (("scholarship_enroll", "enroll"), ("scholarship_existing", "existing")):
            for line in (e.get(sec) or []):
                m = re.match(r"(TOPIK|IELTS)\s*([\d.]+)\s*[→~]\s*(\d{1,3})%", line)
                if m:
                    new_tiers.append({
                        "score_type": m.group(1),
                        "score": int(m.group(2)) if "." not in m.group(2) else float(m.group(2)),
                        "amount": f"{m.group(3)}%",
                        "type": typ,
                    })
        if new_tiers:
            keep = [s for s in sch if not (s.get("type") in ("enroll", "existing"))]
            u["scholarships"] = keep + [{
                "name": "대학원 외국인 장학금",
                "level": "grad",
                "type": "enroll",
                "tiers": new_tiers,
            }]
    # majors_ma fill
    if e.get("majors_ma") and not u.get("majors_ma"):
        u["majors_ma"] = e["majors_ma"]
    n_updated += 1
    print(f"  ✓ {full}")

content_out = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end + 1:]
open(DATA, "w", encoding="utf-8").write(content_out)
print(f"MA 업데이트 {n_updated}개")
