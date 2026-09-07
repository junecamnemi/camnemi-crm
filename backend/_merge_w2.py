# -*- coding: utf-8 -*-
"""Merge wave-2 BA 2026 curation outputs (completed batches 2-7, 9) into verified_kb.json."""
import json, re, os

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
BASE = r"C:\Users\USER\camnemi-crm\backend"
kb = json.load(open(KB, encoding="utf-8"))
ba_sec = kb["schools"]

FILES = ["_w2_out_batch0.json", "_w2_out_batch1.json", "_w2_out_batch2.json", "_w2_out_batch3.json",
         "_w2_out_batch4.json", "_w2_out_batch5.json", "_w2_out_batch6.json", "_w2_out_batch7.json",
         "_w2_out_batch8.json", "_w2_out_batch9.json"]


def clean(n):
    return re.sub(r"^\d+_", "", n or "").strip()


def merge(entry):
    name = clean(entry.get("school"))
    if not name:
        return "skip"
    s = ba_sec.get(name)
    if s is None:
        s = {"name": name}
        ba_sec[name] = s
    if entry.get("period") and not s.get("period"):
        s["period"] = entry["period"]
    if entry.get("lang_req") and not s.get("lang_req"):
        s["lang_req"] = entry["lang_req"]
    t = entry.get("tuition_semester")
    if t and isinstance(t, dict):
        mn = t.get("min")
        mx = t.get("max")
        if mn and mx and "tuition_semester" not in s:
            s["tuition_semester"] = {"min": int(mn), "max": int(mx)}
    # scholarships: keep curated scholarship data in KB as scholarship_curated
    if entry.get("scholarship_enroll") or entry.get("scholarship_existing") or entry.get("scholarship_types"):
        s["scholarship_curated"] = {
            "types": entry.get("scholarship_types") or [],
            "enroll": entry.get("scholarship_enroll") or [],
            "existing": entry.get("scholarship_existing") or [],
        }
    if entry.get("majors_ba"):
        s["majors_ba"] = entry["majors_ba"]
    if entry.get("notes"):
        s["notes_curated"] = entry["notes"]
    s["guide_curated"] = True
    s.setdefault("year", entry.get("year", "2026"))
    return name


added, updated = [], []
for f in FILES:
    fp = os.path.join(BASE, f)
    if not os.path.exists(fp):
        print(f"SKIP {f}")
        continue
    for e in json.load(open(fp, encoding="utf-8")):
        r = merge(e)
        if r == "skip":
            continue
        (added if r not in ba_sec or True else updated)  # placeholder; track below
        # track properly:
        if r not in added and r not in updated:
            added.append(r)

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"BA 추가/업데이트 {len(added)}개")
print("BA 총:", len(ba_sec))
