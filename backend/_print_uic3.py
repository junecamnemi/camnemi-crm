# -*- coding: utf-8 -*-
"""Print UIC-track applicable departments per University Track bachelor school."""
import json

data = json.load(open(r"C:\Users\USER\camnemi-crm\backend\_gksu_uic_majors.json", encoding="utf-8"))

UIC = ["Ajou University", "Daegu University", "Dong-A University", "Inje University",
       "Keimyung University", "Konyang University", "Kookmin University",
       "Korea University of Technology and Education", "Sungshin Women",
       "Yeungnam University"]

for school in UIC:
    entries = data.get(school, [])
    uic = [e for e in entries if "UIC" in (e.get("track") or "")]
    reg = [e for e in entries if "UIC" not in (e.get("track") or "") and "Regional" in (e.get("track") or "")]
    other = [e for e in entries if "UIC" not in (e.get("track") or "") and "Regional" not in (e.get("track") or "")]
    print(f"\n════════ {school} ════════")
    if uic:
        print(f"  ★ UIC-track depts ({len(uic)}):")
        for e in uic:
            print(f"     - {e['kr']} ({e['en']}) | {e['field_en'] or e['field_kr']} | {e['medium']} | TOPIK {e['topik'] or '-'}")
    if reg:
        print(f"  Regional-track depts ({len(reg)}):")
        for e in reg:
            print(f"     - {e['kr']} ({e['en']})")
    if other and not uic and not reg:
        print(f"  all depts ({len(other)}):")
        for e in other:
            print(f"     - {e['kr']} ({e['en']}) | {e['field_en'] or e['field_kr']}")
