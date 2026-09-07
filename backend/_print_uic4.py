# -*- coding: utf-8 -*-
"""Print UIC-applicable departments for the 10 UIC bachelor universities."""
import json

data = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gksu_uic_majors.json", encoding="utf-8"))

UIC = ["Ajou University", "Daegu University", "Dong-A University", "Inje University",
       "Keimyung University", "Konyang University", "Kookmin University",
       "Korea University of Technology and Education", "Sungshin Women",
       "Yeungnam University"]

for school in UIC:
    entries = data.get(school, [])
    uic = [e for e in entries if "UIC" in (e.get("track") or "")]
    print(f"\n══ {school} — UIC-track: {len(uic)} ══")
    if uic:
        for e in uic:
            med = e["medium"] or "-"
            print(f"   • {e['kr']} ({e['en']}) | {e['field_en'] or e['field_kr']} | {med} | {e['topik'] or '-'}")
    else:
        print("   ⚠ no UIC-marked rows — showing all depts:")
        for e in entries:
            med = e["medium"] or "-"
            print(f"   • {e['kr']} ({e['en']}) | {e['field_en'] or e['field_kr']} | {med} | {e['topik'] or '-'}")
