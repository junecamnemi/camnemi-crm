# -*- coding: utf-8 -*-
"""Print ONLY UIC-track-applicable departments for UIC bachelor universities."""
import json

data = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gksu_uic_majors.json", encoding="utf-8"))

UIC = ["Ajou University", "Daegu University", "Dong-A University", "Inje University",
       "Keimyung University", "Konyang University", "Kookmin University",
       "Korea University of Technology and Education", "Sungshin Women",
       "Yeungnam University"]

for school in UIC:
    entries = data.get(school, [])
    uic = [e for e in entries if "UIC" in (e.get("track") or "")]
    other = [e for e in entries if "UIC" not in (e.get("track") or "")]
    print(f"\n════════ {school} ════════")
    if uic:
        print(f"  ★ UIC-track departments ({len(uic)}):")
        for e in uic:
            medium = "EN100%" if "English" in (e["medium"] or "") and "Korean" not in (e["medium"] or "") else (e["medium"] or "-")
            print(f"     - {e['kr']} ({e['en']}) | {e['field']} | {medium} | TOPIK {e['topik'] or '-'}")
    else:
        print(f"  (no UIC-track column found; {len(other)} depts total — check)")
