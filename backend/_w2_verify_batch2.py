# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_w2_out_batch2.json", encoding="utf-8"))
print("entries:", len(d))
for e in d:
    assert e["level"] == "ba" and e["year"] == "2026", e["school"]
    ts = e["tuition_semester"]
    print("-", e["school"], "| period:", (e["period"] or "")[:40], "| tuition:", ts, "| sch_enroll:", "Y" if e["scholarship_enroll"] else "-", "| majors:", len(e["majors_ba"]))
print("JSON parse OK")
