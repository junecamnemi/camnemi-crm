# -*- coding: utf-8 -*-
"""TOPIK<=2 schools WITH their majors listed."""
import json, re

kb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

def min_topik(v):
    txt = " ".join(str(v.get(k,"")) for k in ("topik_req","lang_req","foreign_topik"))
    nums = [int(m) for m in re.findall(r"(?:TOPIK\s*|토픽\s*)(\d)\s*급", txt)] or [int(m) for m in re.findall(r"(\d)\s*급", txt)]
    return min(nums) if nums else None

def majors(v):
    src = None
    for k in ("majors_ba","majors","majors_sample"):
        if v.get(k): src = v[k]; break
    if not src: return []
    if isinstance(src, str):
        parts = re.split(r"[,/·|]|\s{2,}", src)
    else:
        parts = src
    out=[]
    for p in parts:
        p = re.sub(r"\s+"," ", str(p)).strip(" ,·•-")
        p = re.sub(r"^[ㆍ·\-•]\s*","",p)
        if p and 2 <= len(p) <= 45 and p not in out:
            out.append(p)
    return out

def tuition_str(v):
    t = v.get("tuition_semester") or v.get("tuition") or v.get("tuition_min")
    if isinstance(t, dict) and t.get("min"):
        return f"₩{t['min']:,}~{t['max']:,}" if t.get('max') else f"₩{t['min']:,}"
    if isinstance(t,(int,float)) and t: return f"₩{int(t):,}"
    return "-"

for sec,label in [("schools","BA 4년제"), ("junior","전문학사"), ("master","MA 석사")]:
    node = kb[sec]; sch = node.get("schools", node) if isinstance(node,dict) else node
    rows=[]
    for n,v in sch.items():
        if not isinstance(v,dict): continue
        lv = min_topik(v)
        if lv is not None and lv <= 2:
            rows.append((lv, n, v.get("region") or v.get("loc") or "-", tuition_str(v), majors(v)))
    rows.sort(key=lambda r:(r[0], r[1]))
    print(f"\n########## {label}: TOPIK≤2 ({len(rows)}) ##########")
    for lv,n,rg,tu,mj in rows:
        print(f"\n■ {n} [T{lv}] ({rg}) {tu}/sem")
        if mj:
            print("   " + " / ".join(mj[:28]) + (" …" if len(mj)>28 else ""))
        else:
            print("   (학과 정보 미확보)")
