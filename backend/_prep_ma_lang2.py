import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
targets = ['안양대학교','차의과학대학교','청운대학교','한국체육대학교','한국교원대학교','한국기술교육대학교','한라대학교']
out = []
for n in targets:
    for cd, v in idx.items():
        if v["name"]==n and v["school_type"]=="univ4":
            fl = v.get("foreign_links", {})
            need = []
            if not fl.get("ma_foreign"): need.append("ma")
            if not fl.get("lang_foreign"): need.append("lang")
            out.append({"cd": cd, "name": n, "home": v.get("homepage"), "ipsi": v.get("ipsi_homepage"), "need": "+".join(need)})
            break
json.dump(out, open("_ma_lang_targets2.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
for x in out:
    print(f"  {x['name']}: need={x['need']}")