# -*- coding: utf-8 -*-
"""Merge curation outputs (BA 2027 batches 1-3 + MA batches 0-1) into verified_kb.json.
BA schools -> kb['schools'], MA schools -> kb['master']['schools'].
Only fills schools not already present (or upgrades with richer data flag).
"""
import json, re, os

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
BASE = r"C:\Users\USER\camnemi-crm\backend"

kb = json.load(open(KB, encoding="utf-8"))
ba_sec = kb["schools"]
ma_sec = kb["master"]["schools"]


def clean_school_name(s):
    s = re.sub(r"^\d+_", "", s)
    return s.strip()


def to_kr_amount_range(t):
    """tuition_semester dict from curator -> kb tuition_semester min/max."""
    if not t:
        return None
    if isinstance(t, dict) and ("min" in t or "tuition_min" in t):
        mn = t.get("min") or t.get("tuition_min")
        mx = t.get("max") or t.get("tuition_max")
        if mn and mx:
            return {"min": int(mn), "max": int(mx)}
    return None


def merge_school(target, entry):
    """Merge a curated entry into a KB school dict (create if missing)."""
    name = clean_school_name(entry.get("school", ""))
    if not name:
        return "skip-empty"
    s = target.get(name)
    if s is None:
        s = {"name": name}
        target[name] = s
    changed = []
    if entry.get("period"):
        # store both period & raw apply window; keep KB key 'period'
        if entry["period"] != s.get("period"):
            s["period"] = entry["period"]
            changed.append("period")
    if entry.get("lang_req"):
        # lang_req should be human-readable Korean; keep KB lang_req
        if entry["lang_req"] != s.get("lang_req"):
            s["lang_req"] = entry["lang_req"]
            changed.append("lang_req")
    t = to_kr_amount_range(entry.get("tuition_semester"))
    if t:
        s["tuition_semester"] = t
        changed.append("tuition")
    # scholarships: structured summary
    if entry.get("scholarship_types") or entry.get("scholarship_enroll") or entry.get("scholarship_existing"):
        s["scholarship_curated"] = {
            "types": entry.get("scholarship_types") or [],
            "enroll": entry.get("scholarship_enroll") or [],
            "existing": entry.get("scholarship_existing") or [],
        }
        changed.append("scholarships")
    if entry.get("majors_ba") or entry.get("majors_ma"):
        mkey = "majors_ba" if entry.get("majors_ba") else "majors_ma"
        s[mkey] = entry.get(mkey) or entry.get("majors_ma")
        changed.append("majors")
    if entry.get("notes"):
        s["notes_curated"] = entry["notes"]
    s["guide_curated"] = True
    s["guide_year"] = entry.get("year") or s.get("guide_year")
    return name


# --- BA files ---
ba_added, ba_updated = [], []
for bf in ["_curation_out_batch0.json", "_curation_out_batch1.json", "_curation_out_batch2.json", "_curation_out_batch3.json"]:
    fp = os.path.join(BASE, bf)
    if not os.path.exists(fp):
        print(f"SKIP missing {bf}")
        continue
    arr = json.load(open(fp, encoding="utf-8"))
    for entry in arr:
        name = clean_school_name(entry.get("school", ""))
        res = merge_school(ba_sec, entry)
        if res == "skip-empty":
            continue
        (ba_added if res == name else ba_updated).append(name)

# --- MA files ---
ma_added, ma_updated = [], []
for bf in ["_curation_ma_out_batch0.json", "_curation_ma_out_batch1.json"]:
    fp = os.path.join(BASE, bf)
    if not os.path.exists(fp):
        continue
    arr = json.load(open(fp, encoding="utf-8"))
    for entry in arr:
        name = clean_school_name(entry.get("school", ""))
        res = merge_school(ma_sec, entry)
        if res == "skip-empty":
            continue
        (ma_added if res == name else ma_updated).append(name)

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"BA 추가: {len(ba_added)} {ba_added}")
print(f"BA 업데이트: {len(ba_updated)}")
print(f"MA 추가: {len(ma_added)} {ma_added}")
print(f"MA 업데이트: {len(ma_updated)}")
print(f"BA 총 {len(ba_sec)} | MA 총 {len(ma_sec)}")
