# -*- coding: utf-8 -*-
"""TOEFL iBT 80 (≈IELTS 6.0) eligible BA schools + scholarship tier for that score."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
kb = json.load(open(os.path.join(HERE, "verified_kb.json"), encoding="utf-8"))
play = {}
try:
    play = json.load(open(os.path.join(HERE, "scholarship_playbook.json"), encoding="utf-8"))
except Exception:
    pass

TOEFL = 80.0
IELTS_EQ = 6.0

EXCLUDE = {"교육", "신학"}
NAMES = json.load(open(os.path.join(HERE, "_en_names.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "_en_names.json")) else {}


def en(name):
    return NAMES.get(name, name)


def num(x):
    try:
        return float(re.search(r"(\d+\.?\d*)", str(x)).group(1))
    except Exception:
        return None


rows = []
for name, v in kb["schools"].items():
    if v.get("excluded"):
        continue
    tr = v.get("toefl_req")
    ie = v.get("ielts_req")
    lr = str(v.get("lang_req") or "")
    tr_n, ie_n = num(tr), num(ie)
    ok = False
    why = []
    if tr_n is not None and tr_n <= TOEFL:
        ok = True; why.append("TOEFL %g" % tr_n)
    if ie_n is not None and ie_n <= IELTS_EQ:
        ok = True; why.append("IELTS %g" % ie_n)
    if "no minimum" in lr.lower() or "무점수" in lr or "점수 제한 없음" in lr:
        ok = True; why.append("no min score")
    if not ok:
        continue
    # scholarship tier for IELTS 6.0 from playbook
    p = play.get(name) or {}
    en_tiers = p.get("enroll") or {}
    ex_tiers = p.get("existing") or {}
    tier = None
    for key in ("I6.0", "I5.5", "I6", "I5"):
        if key in en_tiers:
            tier = "%s -> %s%% off (admission)" % (key, en_tiers[key])
            break
    rows.append({
        "school": name, "en": en(name), "region": v.get("region") or v.get("loc"),
        "rank": v.get("rank") or "-", "req": lr[:200],
        "toefl": tr, "ielts": ie, "why": ", ".join(why),
        "majors": (v.get("majors") or "")[:220],
        "tuition": v.get("tuition_semester"),
        "period": v.get("period"),
        "sch": json.dumps({"enroll": en_tiers, "existing": ex_tiers,
                           "curated": v.get("scholarship_curated"),
                           "cat": v.get("scholarships_categorized"),
                           "raw": v.get("scholarships")}, ensure_ascii=False),
        "best_tier": tier,
    })

rows.sort(key=lambda r: (str(r["rank"]) == "-", int(str(r["rank"]).lstrip("#")) if str(r["rank"]).lstrip("#").isdigit() else 999))
print(len(rows), "eligible for TOEFL iBT 80")
for r in rows:
    print("\n==", r["school"], "/", r["en"], "|", r["region"], "| rank", r["rank"])
    print("  req:", r["req"][:150])
    print("  tuition:", r["tuition"], "| apply:", r["period"])
    print("  majors:", r["majors"][:150])
    print("  best:", r["best_tier"])
json.dump(rows, open(os.path.join(HERE, "_toefl80_rows.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)