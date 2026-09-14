# -*- coding: utf-8 -*-
"""Schools accepting TOPIK 2 (or lower / no-TOPIK with alternatives) across BA / MA / junior."""
import json, re

kb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

def lvl_of(v):
    """Extract minimum TOPIK level mentioned in requirement fields."""
    txt = " ".join(str(v.get(k,"")) for k in ("topik_req","lang_req","foreign_topik"))
    nums = [int(m) for m in re.findall(r"(?:TOPIK\s*|토픽\s*)(\d)\s*급", txt)]
    if not nums:
        nums = [int(m) for m in re.findall(r"(\d)\s*급", txt)]
    return min(nums) if nums else None

def norm_region(v):
    return v.get("region") or v.get("loc") or "-"

def tuition_str(v):
    t = v.get("tuition_semester") or v.get("tuition") or v.get("tuition_min")
    if isinstance(t, dict) and t.get("min"): 
        return f"₩{t['min']:,}~₩{t['max']:,}" if t.get('max') else f"₩{t['min']:,}"
    if isinstance(t,(int,float)) and t: return f"₩{int(t):,}"
    return "-"

for sec, label in [("schools","BA (4년제)"), ("junior","전문학사"), ("master","MA (석사)")]:
    node = kb[sec]
    sch = node.get("schools", node) if isinstance(node, dict) else node
    rows=[]
    for n,v in sch.items():
        if not isinstance(v,dict): continue
        lv = lvl_of(v)
        if lv is not None and lv <= 2:
            rows.append((lv, n, norm_region(v), tuition_str(v), str(v.get("period","-"))[:45]))
    rows.sort(key=lambda r:(r[0], r[1]))
    print(f"\n===== {label}: TOPIK 2 이하 ({len(rows)}) =====")
    for lv,n,rg,tu,pe in rows:
        print(f"  [T{lv}] {n} ({rg}) {tu}/sem | {pe}")
