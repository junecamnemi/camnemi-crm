# -*- coding: utf-8 -*-
"""Merge 6 junior scholarship batch files into verified_kb.json."""
import json, os, glob

KB = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB, encoding="utf-8"))
junior = kb["junior"]["schools"]

merged = {}
for fp in sorted(glob.glob(r"C:\Users\USER\camnemi-crm\backend\_junior_scholarships_batch*.json")):
    d = json.load(open(fp, encoding="utf-8"))
    for name, schols in d.items():
        if name not in merged:
            merged[name] = []
        merged[name].extend(schols)

updated = 0
for name, schols in merged.items():
    if name in junior:
        junior[name]["scholarships_categorized"] = schols
        updated += 1

json.dump(kb, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"전문대 장학금 반영: {updated}개 학교")

# stats
with_data = sum(1 for s in junior.values() if s.get("scholarships_categorized") and len(s["scholarships_categorized"]) > 0)
total = len(junior)
print(f"전문대 장학금 보유: {with_data}/{total} ({(with_data/total*100):.0f}%)")

# cleanup
for fp in sorted(glob.glob(r"C:\Users\USER\camnemi-crm\backend\_junior_scholarships_batch*.json")):
    os.remove(fp)
print("임시 배치 파일 정리 완료")
