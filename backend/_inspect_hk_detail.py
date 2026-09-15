import json, os
B = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"
d = json.load(open(os.path.join(B,"체류민원_D2D4D10E7_pro.json"), encoding="utf-8"))
print("keys:", list(d.keys()))
for s in d["by_status"]:
    print("="*70)
    for k,v in s.items():
        if isinstance(v,list) and v:
            print(f"\n■ {k} ({len(v)}):")
            for x in v[:6]:
                print("   ", str(x)[:140])
        elif isinstance(v,dict):
            print(f"\n■ {k}: {json.dumps(v,ensure_ascii=False)[:300]}")
        elif v:
            print(f"\n■ {k}: {str(v)[:250]}")
