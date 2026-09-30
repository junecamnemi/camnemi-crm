# -*- coding: utf-8 -*-
import json, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
univ = json.load(open(os.path.join(HERE, "_adiga_univ_list.json"), encoding="utf-8"))
junior = json.load(open(os.path.join(HERE, "_adiga_junior_list.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)
def norm(n): return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()
def key(n): return re.sub(r"(대학교|대학|대)$", "", norm(n))
UNIV={norm(v) for v in univ.values()}; JUNIOR={norm(v) for v in junior.values()}
KB_SHORT={key(s) for s in ms}; US={key(x) for x in UNIV}; JS={key(x) for x in JUNIOR}
def school_of(f):
    parts=[p for p in re.sub(r"\.(pdf|hwp|html|docx|do)$","",f,flags=re.I).split("_") if not re.fullmatch(r"\d{4,}",p)]
    for p in parts:
        q=norm(p)
        if q.endswith(("대학교","대학")): return q
    for p in parts:
        q=norm(p)
        if q.endswith("대") and len(q)>=2: return q
    return norm(parts[0]) if parts else f
def kind(name):
    n=school_of(name); k=key(n)
    if n in JUNIOR or k in JS: return "junior"
    if n in UNIV or k in US or k in KB_SHORT: return "univ"
    return "unknown"
LV={"ba":"학사","ma":"석사","junior":"전문학사","lang":"어학연수"}
rows=[]
for root,dirs,files in os.walk(G):
    for f in files:
        if not f.lower().endswith((".pdf",".hwp")): continue
        rel=os.path.relpath(os.path.join(root,f),G).replace("\\","/")
        parts=rel.split("/")
        arch="_archive" in parts
        rest=parts[parts.index("_archive")+1:] if arch else parts
        lv=next((p for p in rest if p in LV),None)
        yrf=next((p for p in rest if re.fullmatch(r"20\d\d",p)),None)
        yrn=re.search(r"(20\d\d)",f)
        yr=yrf or (yrn.group(1) if yrn else "unknown")
        rows.append(dict(file=f,rel=rel,level=lv,year=yr,arch=arch,school=school_of(f),kind=kind(f)))
def bucket(r):
    if r["level"]=="lang":
        return {"univ":"어학연수(대학교)","junior":"어학연수(전문대학교)"}.get(r["kind"],"어학연수(미분류)")
    return LV.get(r["level"],"기타")
order=["학사","석사","전문학사","어학연수(대학교)","어학연수(전문대학교)","어학연수(미분류)","기타"]
print("%-20s %6s %6s %6s | %6s %6s %6s | %s"%("bucket","26f","27f","tot","26s","27s","scl","distinct schools(all yrs)"))
for b in order:
    rs=[r for r in rows if bucket(r)==b]
    if not rs: continue
    f26=sum(1 for r in rs if r["year"]=="2026"); f27=sum(1 for r in rs if r["year"]=="2027")
    s26={r["school"] for r in rs if r["year"]=="2026"}; s27={r["school"] for r in rs if r["year"]=="2027"}
    alls={r["school"] for r in rs}
    print("%-20s %6d %6d %6d | %6d %6d %6d | %d"%(b,f26,f27,len(rs),len(s26),len(s27),len(alls),len(alls)))
# union of all buckets school counts
print()
# archived 2027-only check
act={}
for r in rows:
    if not r["arch"] and r["year"]=="2027":
        act.setdefault((r["school"],r["level"]),[]).append(r["rel"])
bad=[]
for r in rows:
    if r["arch"] and r["year"]=="2027" and (r["school"],r["level"]) not in act:
        bad.append(r["rel"])
print("archived-2027 with NO active 2027 copy for same school+level:", len(bad))
for x in bad: print("   ",x)
print("other-year files:", sorted({(r["year"],r["level"]) for r in rows if r["year"] not in ("2026","2027")}))
