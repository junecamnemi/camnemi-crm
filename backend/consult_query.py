# -*- coding: utf-8 -*-
"""Consulting query tool for the unified foreigner-admission DB (consulting_db.json).
Search by level, region, IELTS/TOPIK, major (popular/similar), max tuition.
Output: school, region, each program's topik/ielts/tuition/period/popular-majors.

Usage:
  python consult_query.py --level ba --ielts 5.5 --region 부산
  python consult_query.py --level ma --topik 6 --major data
  python consult_query.py --level junior --region 경기 --max_tuition 2000000
  python consult_query.py --level lang --region 서울          # 어학연수
"""
import json, os, re, argparse, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from en_output import en_name, en_region, fmt_usd
except ImportError:
    def en_name(n): return n
    def en_region(r): return r
    def fmt_usd(k): return f"${k//1400*100//100*100}" if k else None

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "consulting_db.json")
db = json.load(open(DB, encoding="utf-8"))
schools = db["schools"]

LEVEL_MAP = {"ba":"BA", "ma":"MA", "junior":"전문학사", "lang":"어학연수", "junior2":"전문학사"}

POPULAR_KW = {
    "business":["경영","회계","경제","무역","마케팅","금융","세무"],
    "computer":["컴퓨터","소프트웨어","인공지능","데이터","AI","정보통신","전자공학","정보보안"],
    "data":["데이터","빅데이터","인공지능","AI","통계","정보"],
    "engineering":["기계","전자","전기","화학공학","건축","토목","산업공학","식품공학","로봇"],
    "nursing":["간호","보건","의료","물리치료","작업치료","임상병리"],
    "beauty":["뷰티","미용","화장품","향장","코스메틱","피부","헤어","네일"],
    "food":["조리","외식","호텔외식","식품","바리스타","제과","영양"],
    "aviation":["항공","항공서비스","승무","운항"],
    "design":["디자인","패션","시각","산업디자인","건축디자인"],
    "media":["미디어","방송","콘텐츠","영상","광고","신문","게임"],
    "global":["글로벌","국제","영어","호텔","관광","비즈니스"],
    "ai":["인공지능","AI","데이터","로봇","지능정보"],
    "pharmacy":["약학","제약","신약","바이오의약"],
}

def matches_major(prog, query):
    majors = prog.get("majors")
    if not majors: return False
    if isinstance(majors, str): majors = [m.strip() for m in majors.replace("/"," ").split() if m.strip()]
    kw = POPULAR_KW.get(query.lower(), [query])
    for m in majors:
        for k in kw:
            if k.lower() in str(m).lower(): return True
    return False

def parse_topik(v):
    if not v: return None
    m = re.search(r"(\d)급", str(v))
    return int(m.group(1)) if m else None

def parse_ielts(v):
    if not v: return None
    m = re.search(r"IELTS\s*(\d(?:\.\d)?)", str(v))
    return float(m.group(1)) if m else None

def fmt_tuition(t):
    if not t: return "confirm"
    if isinstance(t, dict): t = t.get("min", t.get("max"))
    if isinstance(t, int): return fmt_usd(t) or str(t)
    # string like ₩3,809,000 or {min..max}
    return str(t)

def main():
    ap = argparse.ArgumentParser(description="Camnemi unified consulting DB query")
    ap.add_argument("--level", choices=["ba","ma","junior","lang"], default="ba")
    ap.add_argument("--region", type=str)
    ap.add_argument("--ielts", type=float)
    ap.add_argument("--topik", type=int)
    ap.add_argument("--major", type=str)
    ap.add_argument("--max_tuition", type=int, help="max tuition KRW/semester")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    lv = LEVEL_MAP[args.level]

    results=[]
    for name, s in schools.items():
        prog = s["programs"].get(lv)
        if not prog: continue
        # exclusion
        if prog.get("excluded"): continue
        if args.region and args.region not in str(s.get("region","")): continue
        # language eligibility
        if args.topik:
            ptop = parse_topik(prog.get("topik"))
            if ptop and args.topik < ptop: continue
        if args.ielts:
            piel = parse_ielts(prog.get("ielts"))
            if piel and args.ielts < piel: continue
        if args.major and not matches_major(prog, args.major): continue
        # tuition
        if args.max_tuition:
            t = prog.get("tuition")
            tv = None
            if isinstance(t, dict): tv = t.get("min")
            elif isinstance(t, int): tv = t
            elif isinstance(t,str):
                mm = re.search(r"(\d{6,7})", t.replace(",",""))
                tv = int(mm.group(1)) if mm else None
            if tv and tv > args.max_tuition: continue
        # scoring for sort: prefer has-tuition + popular majors
        score = 0
        if prog.get("tuition"): score += 2
        if prog.get("popular_majors"): score += 1
        results.append((score, name, s, prog))

    results.sort(key=lambda x: -x[0])
    results = results[:args.top]

    print(f"=== {lv} / {'all regions' if not args.region else args.region} / {'IELTS '+str(args.ielts) if args.ielts else ''}{' TOPIK '+str(args.topik) if args.topik else ''} / {'major='+args.major if args.major else ''} → {len(results)} schools ===")
    for i,(score,name,s,prog) in enumerate(results,1):
        topik = prog.get("topik") or "-"
        ielts = prog.get("ielts") or "-"
        tu = fmt_tuition(prog.get("tuition"))
        per = prog.get("period") or "-"
        pop = prog.get("popular_majors") or []
        poptxt = ", ".join(pop[:4]) if pop else ""
        print(f"{i}. {en_name(name)} ({s.get('region','')})")
        print(f"   TOPIK: {topik} | IELTS: {ielts} | Tuition: {tu}/sem")
        if per != "-": print(f"   Apply: {per}")
        if poptxt: print(f"   인기/유사과: {poptxt}")
        sch = prog.get("scholarship")
        if sch: print(f"   Scholarship: {str(sch)[:120]}")
        print()

if __name__ == "__main__":
    main()
