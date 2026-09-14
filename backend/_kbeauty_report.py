# -*- coding: utf-8 -*-
"""K-Beauty majors: admission req + tuition (+ per-dept fields) + scholarship, from synced KB."""
import json, re

kb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
KW = r"(뷰티|미용|코스메틱|K-뷰티|K뷰티|메이크업|피부|헤어|네일|향장|바이오코스메틱)"

def find_depts(v):
    txt = " ".join(str(v.get(k,"")) for k in ("majors_ba","majors","majors_sample","majors_ma"))
    hits = re.findall(r"[가-힣A-Za-z0-9·\-·()\s]{2,40}?" + KW + r"[가-힣A-Za-z0-9·\-·()\s]{0,20}", txt)
    out=[]
    for h in hits:
        h=re.sub(r"\s+"," ",h).strip(" ,·[]'\"")
        if h and h not in out and len(h)<=40: out.append(h)
    return out[:5]

def tuition_str(v):
    t = v.get("tuition_semester") or v.get("tuition") or v.get("tuition_min")
    if isinstance(t, dict):
        return f"₩{t.get('min'):,}~₩{t.get('max'):,}" if t.get('min') and t.get('max') else str(t)
    if isinstance(t, (int,float)) and t: return f"₩{int(t):,}"
    return str(t) if t else "-"

def sch_topik(v):
    out=[]
    for s in (v.get("scholarships_categorized") or []):
        if s.get("type")!="enroll": continue
        for t in s.get("tiers",[]):
            sc=str(t.get("score",""))
            if "6" in sc or "5" in sc:
                out.append(f"{sc}→{t.get('amount')}")
    return "; ".join(out[:3])

print("========== BA (4년제) ==========")
for n,v in kb["schools"].items():
    d = find_depts(v)
    if d:
        print(f"\n■ {n} [{v.get('region') or v.get('loc')}]")
        print(f"   학과: {', '.join(d)}")
        print(f"   언어: TOPIK {v.get('topik_req','-')} | IELTS {v.get('ielts_req','-')}")
        print(f"   등록금: {tuition_str(v)}/학기")
        bd = v.get("tuition_semester_by_dept")
        if bd and bd.get("fields"): print(f"   계열: {bd['fields']}")
        st = sch_topik(v)
        if st: print(f"   장학(TOPIK5~6): {st}")
        print(f"   기간: {str(v.get('period','-'))[:60]}")

print("\n========== 전문학사 (2~3년제) ==========")
for n,v in kb["junior"]["schools"].items():
    d = find_depts(v)
    if d:
        print(f"\n■ {n} [{v.get('region') or v.get('loc')}]")
        print(f"   학과: {', '.join(d)}")
        print(f"   언어: TOPIK {v.get('topik_req','-')} | IELTS {v.get('ielts_req','-')}")
        print(f"   등록금: {tuition_str(v)}/학기")
        print(f"   기간: {str(v.get('period','-'))[:60]}")
