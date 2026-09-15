import json, os
B = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals"

def show(fp, label):
    print("="*60)
    print(f"### {label}: {os.path.basename(fp)}")
    d = json.load(open(fp, encoding="utf-8"))
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, list):
                print(f"■ {k} (리스트 {len(v)}):")
                for item in v[:8]:
                    print("   ", json.dumps(item, ensure_ascii=False)[:200])
            elif isinstance(v, dict):
                print(f"■ {k} (dict):")
                print("   ", json.dumps(v, ensure_ascii=False)[:300])
            else:
                print(f"■ {k}: {str(v)[:150]}")
    print()

show(os.path.join(B,"사증_체류_통합분석_pro.json"), "사증+체류 통합분석")
show(os.path.join(B,"체류민원_D2D4D10E7_pro.json"), "D-2/D-4/D-10/E-7 체류")
