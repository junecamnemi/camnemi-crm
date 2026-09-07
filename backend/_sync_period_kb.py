# -*- coding: utf-8 -*-
"""Sync period + lang from verified_kb.json into data.js for ALL KB schools that
already carry curated period/lang (esp. the original 43-deep set + 46 curated)."""
import json, re

DATA = r"C:\Users\USER\camnemi-crm\data.js"
KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))

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

n_period, n_topik, n_ielts = 0, 0, 0
# KB schools section (BA) + master
for sec in ("schools",):
    for name, s in kb[sec].items():
        u = dn.get(name)
        if not u:
            continue
        if s.get("period") and not u.get("period"):
            u["period"] = s["period"]
            n_period += 1
        lr = s.get("lang_req")
        if lr:
            req = u.setdefault("req", {})
            tp = parse_topik(lr)
            il = parse_ielts(lr)
            if tp and req.get("topik") in (None, 0, ""):
                req["topik"] = tp
                n_topik += 1
            if il and req.get("ielts") in (None, 0, ""):
                req["ielts"] = il
                n_ielts += 1

content_out = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end + 1:]
open(DATA, "w", encoding="utf-8").write(content_out)
print(f"period 추가 {n_period} | topik 추가 {n_topik} | ielts 추가 {n_ielts}")
