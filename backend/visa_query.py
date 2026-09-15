#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visa_query.py — Korea visa change-rule lookup (for the bot / consulting).

Usage:
  python visa_query.py --from D-4                 # what D-4 can change to (+ income)
  python visa_query.py --family D-2               # family invitation rules
  python visa_query.py --to D-2 --from E-7        # is E-7 -> D-2 possible?
  python visa_query.py --income                   # income requirements table
  python visa_query.py --all                      # everything (JSON)
"""
import json, os, argparse, re

B = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(B, "visa_change_rules_kr.json"), encoding="utf-8"))

def norm(v):
    v = str(v or "").strip().upper().replace("_", "-")
    return v

def find_from(key):
    for k, v in DATA["changeable_from"].items():
        if norm(k) == norm(key):
            return k, v
    return None, None

def cmd_from(key):
    k, v = find_from(key)
    if not v:
        print(f"[{key}] 규정 없음"); return
    print(f"### {k} ({v.get('label','')}) → 변경 가능")
    for t in v.get("can_change_to", []):
        inc = f"  | 소득: {t['income']}" if t.get("income") else ""
        print(f"  • {t['to']}\n     조건: {t.get('condition','')}{inc}")
    for c in v.get("cannot", []):
        print(f"  ❌ {c}")
    if v.get("quota"): print(f"  📊 쿼터: {v['quota']}")

def cmd_family(key):
    fam = DATA["family_invitation"]
    hit = None
    for k, v in fam.items():
        if k != "note" and norm(k) == norm(key):
            hit = (k, v); break
    if not hit:
        print(f"[{key}] 가족초청 규정 없음 (가능: {[k for k in fam if k!='note']})"); return
    k, v = hit
    mark = "✅ 가능" if v.get("possible") else "❌ 불가"
    print(f"### {k} 가족 초청\n  {mark}\n  {v.get('detail','')}")
    if v.get("caveat"): print(f"  ⚠️ {v['caveat']}")

def cmd_transition(fr, to):
    k, v = find_from(fr)
    if not v:
        print(f"[{fr}] 규정 없음"); return
    for t in v.get("can_change_to", []):
        if norm(to) in norm(t["to"]):
            inc = f"\n  소득: {t['income']}" if t.get("income") else ""
            print(f"✅ {fr} → {t['to']}\n  조건: {t.get('condition','')}{inc}")
            if t.get("note"): print(f"  참고: {t['note']}")
            return
    blocked = [c for c in v.get("cannot", []) if norm(to) in norm(c)]
    if blocked:
        print(f"❌ {fr} → {to}: {blocked[0]}")
    else:
        print(f"⚠️ {fr} → {to}: 명시 규정 없음 (출입국 확인 필요)")

def cmd_income():
    inc = DATA["income_requirements"]
    print("### 소득 요건 (2026)")
    print(f"  {inc.get('note','')}")
    for k, v in inc.items():
        if k == "note": continue
        if v.get("min_annual_krw"):
            print(f"  • {k}: 연 {v['min_annual_krw']:,}원 이상")
        elif v.get("basis"):
            print(f"  • {k}: {v['basis']}")
        elif v.get("note"):
            print(f"  • {k}: {v['note']}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="fr"); ap.add_argument("--to")
    ap.add_argument("--family"); ap.add_argument("--income", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all: print(json.dumps(DATA, ensure_ascii=False, indent=1)); return
    if a.income: cmd_income(); return
    if a.family: cmd_family(a.family); return
    if a.fr and a.to: cmd_transition(a.fr, a.to); return
    if a.fr: cmd_from(a.fr); return
    print("usage: --from D-4 | --from E-7 --to D-2 | --family D-2 | --income | --all")

if __name__ == "__main__":
    main()
