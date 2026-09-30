#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop phantom levels and label each entry with its school type.

Operator's point: "김포대는 전문학사니까 당연히 없지" — 김포대학교 is a 전문대, so reporting it under
"BA schools missing tuition" was nonsense. Cause: a school can carry a level it does not really run.
A level entry is a phantom when it has NO per-college rows AND NO majors in the KB for that level,
while the same school has another level that does (that other level is the real one).

  · 김포대학교        BA majors=7, 전문학사 majors=0  → keep BA(전공심화), drop empty 전문학사
  · 한국농수산대학교   BA majors=18, 전문학사 majors=0 → drop empty 전문학사
  · 제주한라대학교     both have rows (전문학사 + 전공심화) → keep both
Also stamps `school_type` (전문대 if it appears in the junior KB section, else 4년제) so downstream
reporting can never again put a 전문대 in a "BA" list.

  python _tuition_level_cleanup.py --dry
  python _tuition_level_cleanup.py
"""
import os, json, sys, shutil, datetime

B = os.path.dirname(os.path.abspath(__file__))
TBD = os.path.join(B, "tuition_by_department.json")
KB = os.path.join(B, "verified_kb.json")
TODAY = datetime.date.today().isoformat()


def main():
    kb = json.load(open(KB, encoding="utf-8"))
    SEC = {"BA": kb["schools"], "MA": kb["master"]["schools"], "전문학사": kb["junior"]["schools"]}
    doc = json.load(open(TBD, encoding="utf-8"))
    dry = "--dry" in sys.argv

    def majors(lv, name):
        v = SEC.get(lv, {}).get(name)
        return len((v or {}).get("majors") or [])

    dropped, retyped = [], 0
    for name, lvs in doc["schools"].items():
        # school type: junior-section membership means 전문대
        jr = name in SEC["전문학사"]
        # A hollow junior record does not make a school a 전문대: 한국농수산대학교 is 4년제 (BA
        # majors=18) that merely carries a 전문학사 row. Type follows where the school's own majors are.
        jr_real = jr and not (majors("BA", name) > 0 or majors("MA", name) > 0)
        is4 = name in SEC["BA"] or name in SEC["MA"]
        stype = ("전문대" if (jr_real and not is4)
                 else ("전문대(전공심화 있음)" if jr_real else "4년제"))
        for lv, e in list(lvs.items()):
            if not isinstance(e, dict):
                continue
            if e.get("school_type") != stype:
                e["school_type"] = stype
                retyped += 1
            if e.get("rows"):
                continue
            # phantom test: this level has nothing of its own, but the school has a level that does
            if majors(lv, name) == 0:
                # the school's real level is one that has rows OR its own majors — 한국농수산대학교 is a
                # 4년제 (BA majors=18) carrying a hollow 전문학사 record, so rows alone is too narrow.
                others = [l for l, o in lvs.items()
                          if l != lv and isinstance(o, dict)
                          and (o.get("rows") or majors(l, name) > 0)]
                if others:
                    dropped.append((name, lv, stype, "rows없음+majors0, 실제 레벨=" + ",".join(others)))
                    if not dry:
                        lvs.pop(lv)
    print(f"phantom levels dropped: {len(dropped)} | school_type stamped/updated: {retyped}")
    for n, lv, st, why in dropped:
        print(f"   - {n[:20]:22}[{lv:8}] {st:16} {why}")
    if not dry:
        shutil.copy(TBD, TBD.replace(".json", f"_bak_levelcleanup_{TODAY}.json"))
        doc["meta"]["level_cleanup"] = TODAY
        doc["meta"]["level_cleanup_note"] = ("phantom levels removed (no rows, no majors, school's real "
                                             "level is another); school_type stamped")
        json.dump(doc, open(TBD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    left = {}
    for lv in SEC:
        left[lv] = sum(1 for lvs in doc["schools"].values() for l, e in lvs.items()
                       if l == lv and isinstance(e, dict) and not e.get("rows"))
    total = sum(1 for lvs in doc["schools"].values() for e in lvs.values() if isinstance(e, dict))
    withr = sum(1 for lvs in doc["schools"].values() for e in lvs.values()
                if isinstance(e, dict) and e.get("rows"))
    print("missing by level:", left)
    print(f"entries with rows: {withr} / {total}")


if __name__ == "__main__":
    main()