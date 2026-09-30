# -*- coding: utf-8 -*-
"""Operator-requested counts + the funnel behind '182'."""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
man = json.load(open(os.path.join(G, "_library_manifest.json"), encoding="utf-8"))
act = [e for e in man["entries"] if not e.get("archived")]

univ = json.load(open(os.path.join(HERE, "_adiga_univ_list.json"), encoding="utf-8"))
junior = json.load(open(os.path.join(HERE, "_adiga_junior_list.json"), encoding="utf-8"))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
ms = kb.get("master", {}).get("schools", kb)


def norm(n):
    return re.sub(r"\[.*?\]|\(.*?\)", "", n).strip()


def short(n):
    n = norm(n)
    return n[:-3] if n.endswith("대학교") else (n[:-2] if n.endswith("대학") else n)


UNIV = {norm(v) for v in univ.values()}
JUNIOR = {norm(v) for v in junior.values()}
def key(n):
    return re.sub(r"(대학교|대학|대)$", "", norm(n))


KB_SHORT = {key(s) for s in ms}
US = {key(x) for x in UNIV}
JS = {key(x) for x in JUNIOR}


def school_of(f):
    parts = [p for p in re.sub(r"\.(pdf|hwp|html|docx|do)$", "", f, flags=re.I).split("_")
             if not re.fullmatch(r"\d{4,}", p)]
    for p in parts:
        q = norm(p)
        if q.endswith(("대학교", "대학")):
            return q
    for p in parts:
        q = norm(p)
        if q.endswith("대") and len(q) >= 2:
            return q
    return norm(parts[0]) if parts else f


def kind(name):
    n = school_of(name)
    k = key(n)
    if n in JUNIOR or k in JS:
        return "junior"
    if n in UNIV or k in US or k in KB_SHORT:
        return "univ"
    return "unknown"


B = collections.defaultdict(list)
for e in act:
    lv, k = e["level"], kind(e["name"])
    b = {"ba": "학사", "ma": "석사", "junior": "전문학사"}.get(lv)
    if lv == "lang":
        b = {"univ": "어학연수(대학교)", "junior": "어학연수(전문대학교)"}.get(k, "어학연수(미분류)")
    B[b or "기타"].append((school_of(e["name"]), e["name"], lv, k))

for b in ["학사", "석사", "어학연수(대학교)", "전문학사", "어학연수(전문대학교)", "어학연수(미분류)", "기타"]:
    if b in B:
        print(f"{b}: {len(B[b])}건 ({len({s for s, n, lv, k in B[b]})}개 학교)")

slots = {(s, lv) for b in B.values() for s, n, lv, k in b}
print(f"\n합계: {sum(len(v) for v in B.values())}건 / (학교,레벨) 슬롯 {len(slots)}개")
print("미분류 어학연수:", [(s, n) for s, n, lv, k in B.get("어학연수(미분류)", [])])
print("어학연수 전체:", sorted({s for b in ("어학연수(대학교)", "어학연수(전문대학교)", "어학연수(미분류)")
                                for s, *_ in B.get(b, [])}))

wl = os.path.join(HERE, "_pipeline_data", "reports", "_2027_watchlist.json")
w = json.load(open(wl, encoding="utf-8"))
print("\n=== 312 KB school×level slots (why not more) ===")
print("watchlist counts:", json.dumps(w.get("counts"), ensure_ascii=False))
lv = collections.Counter()
for e in w.get("entries", []):
    if isinstance(e, dict) and e.get("status"):
        lv[(e.get("level") or "?", e["status"])] += 1
for k in sorted(lv):
    print("   ", k, lv[k])