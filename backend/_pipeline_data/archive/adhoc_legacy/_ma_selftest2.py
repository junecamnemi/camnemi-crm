import json, re

kb = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
ma = kb["master"]["schools"]
for k in ["조선대학교", "청운대학교"]:
    v = ma.get(k, {})
    print(f"=== {k} (석사) ===")
    for f in ["lang_req", "note", "majors", "region", "tuition", "guide_status"]:
        if v.get(f):
            print(f"  {f}: {json.dumps(v[f], ensure_ascii=False)[:400]}")
    print()
