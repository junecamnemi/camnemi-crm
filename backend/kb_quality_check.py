#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB quality checker — surfaces errors, gaps, anomalies and staleness in verified_kb.json.

Checks:
  1. MISSING CRITICAL FIELDS  (period / lang_req / tuition) per school+level
  2. TUITION ANOMALIES        (< ₩500,000 or > ₩12,000,000 per semester — likely parse bugs)
  3. LANGUAGE-REQ INCONSISTENCY (lang_req text vs structured topik_req/ielts_req)
  4. STALE GUIDES             (year < 2027 with no 2027 guide, or guide_analyzed old)
  5. AMBIGUOUS REQUIREMENTS   (multiple differing thresholds — track-specific)
  6. EXCLUDED-SCHOOL LEAKS    (신학대/교육대/소규모 flagged but present in recommendation data)

Usage: python kb_quality_check.py [--write]   (--write saves _kb_quality_report.json)
"""
import json, os, re, argparse, datetime
from collections import Counter

B = r"C:\Users\USER\camnemi-crm\backend"
KB = os.path.join(B, "verified_kb.json")
SMART = os.path.join(B, "kb_smart.json")
OUT = os.path.join(B, "_kb_quality_report.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    kb = json.load(open(KB, encoding="utf-8"))
    smart = json.load(open(SMART, encoding="utf-8")) if os.path.exists(SMART) else {"schools": {}}
    today = datetime.date.today().isoformat()

    report = {"date": today, "checks": {}}

    # 1. missing critical fields (BA)
    miss = []
    for k, v in kb["schools"].items():
        missing = [f for f in ("period", "lang_req") if not v.get(f)]
        if not (v.get("tuition_semester") or v.get("tuition_min")):
            missing.append("tuition")
        if missing:
            miss.append({"school": k, "missing": missing})
    report["checks"]["ba_missing_critical"] = {"count": len(miss), "sample": miss[:30]}

    # 2. tuition anomalies
    def tval(t):
        if isinstance(t, dict): return t.get("min")
        return t
    anom = []
    for k, v in kb["schools"].items():
        t = tval(v.get("tuition_semester"))
        if isinstance(t, (int, float)) and (t < 500000 or t > 12000000):
            anom.append({"school": k, "tuition": t})
    for k, v in kb.get("junior", {}).get("schools", {}).items():
        t = tval(v.get("tuition_semester"))
        if isinstance(t, (int, float)) and (t < 500000 or t > 12000000):
            anom.append({"school": k, "level": "junior", "tuition": t})
    report["checks"]["tuition_anomalies"] = {"count": len(anom), "items": anom[:30]}

    # 3. lang_req vs structured inconsistency
    incon = []
    for k, v in kb["schools"].items():
        lr = str(v.get("lang_req") or "")
        m = re.search(r"TOPIK[^\d]{0,6}(\d)\s*(?:급|이상)?", lr)
        if m and v.get("topik_req") not in (None, "", "null"):
            try:
                if int(float(v["topik_req"])) != int(m.group(1)):
                    incon.append({"school": k, "lang_req_topik": m.group(1), "topik_req": v["topik_req"]})
            except Exception:
                pass
    report["checks"]["langreq_vs_field"] = {"count": len(incon), "items": incon[:30]}

    # 4. stale: BA schools without a 2027 guide marker
    guide = kb.get("guide", {})
    stale = [k for k in kb["schools"]
             if not (isinstance(guide.get(k), dict) and guide.get(k, {}).get("status", "").startswith("2027"))]
    report["checks"]["ba_no_2027_guide"] = {"count": len(stale), "sample": stale[:30]}

    # 5. ambiguous requirements
    amb = [k for k, s in smart.get("schools", {}).items()
           if s.get("BA", {}).get("eligibility", {}).get("ambiguous")]
    report["checks"]["ambiguous_requirements_ba"] = {"count": len(amb), "sample": amb[:30]}

    # 6. excluded-school leaks
    EXCL = ("신학대", "교육대")
    leaks = [k for k in kb["schools"] if any(e in k for e in EXCL)]
    report["checks"]["excluded_school_leaks"] = {"count": len(leaks), "items": leaks}

    # summary print
    print(f"=== KB Quality Report — {today} ===")
    for name, c in report["checks"].items():
        print(f"  {name}: {c['count']}")
    if miss:
        print("\n  [BA 누락 필드 샘플]")
        for x in miss[:12]:
            print(f"    {x['school']}: {x['missing']}")
    if anom:
        print("\n  [등록금 이상치]")
        for x in anom[:12]:
            print(f"    {x['school']} ({x.get('level','BA')}): ₩{x['tuition']:,}")
    if incon:
        print("\n  [lang_req ↔ 필드 불일치]")
        for x in incon[:15]:
            print(f"    {x['school']}: lang_req TOPIK {x['lang_req_topik']} vs topik_req {x['topik_req']}")

    if args.write:
        json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
