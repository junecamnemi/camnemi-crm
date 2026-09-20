import json, os
B = "."
idx = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
targets = ['극동대학교','나사렛대학교','한국교원대학교','한국기술교육대학교','한라대학교',
           '강남대학교','경동대학교','안양대학교','차의과학대학교','청운대학교','한국체육대학교']
out = []
for n in targets:
    for cd, v in idx.items():
        if v["name"]==n and v["school_type"]=="univ4":
            out.append({"cd": cd, "name": n, "ipsi": v.get("ipsi_homepage"), "home": v.get("homepage"),
                        "need": "ma+lang" if n in ['극동대학교','나사렛대학교','한국교원대학교','한국기술교육대학교','한라대학교'] else "lang"})
            break
json.dump(out, open("_ma_lang_targets.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("대상:", len(out))
for x in out:
    print(f"  {x['name']}: need={x['need']}")