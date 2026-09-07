# -*- coding: utf-8 -*-
"""Print University Track (UIC bachelor) university majors nicely."""
import json

data = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gksu_uic_majors.json", encoding="utf-8"))

UIC = ["Ajou University", "Daegu University", "Dong-A University", "Inje University",
       "Keimyung University", "Konyang University", "Kookmin University",
       "Korea University of Technology and Education", "Sungshin Women",
       "Yeungnam University"]

for school in UIC:
    entries = data.get(school, [])
    if not entries:
        continue
    print(f"\n════════ {school} — {len(entries)} departments ════════")
    # group by field
    from collections import defaultdict
    by_field = defaultdict(list)
    for e in entries:
        field = e["field"] or "?"
        by_field[field].append(e)
    for field, items in by_field.items():
        print(f"\n  ◆ {field}")
        for e in items:
            topik = e["topik"] or "-"
            medium = e["medium"] or "-"
            # shorten medium
            if "English" in medium and "Korean" in medium:
                m = "KR/EN"
            elif "English" in medium:
                m = "EN 100%"
            elif "Korean" in medium:
                m = "KR 100%"
            else:
                m = medium
            print(f"     - {e['kr']} ({e['en']}) [{m} | TOPIK {topik}]")
