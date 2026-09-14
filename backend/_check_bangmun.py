import json, re
rows = [json.loads(l) for l in open(r"C:\Users\USER\camnemi-crm\backend\_apply_pro.jsonl", encoding="utf-8") if l.strip()]
print("=== '방문' 판정 근거 샘플 ===")
n = 0
for r in rows:
    if r.get("primary") == "방문" and n < 12:
        print(f"[{r.get('_level')}] {r.get('_file','')[:36]}")
        print("   ev:", str(r.get("evidence"))[:160])
        n += 1
print()
print("=== '홈페이지' 판정 근거 샘플 ===")
n = 0
for r in rows:
    if r.get("primary") == "홈페이지" and n < 5:
        print(f"[{r.get('_level')}] {r.get('_file','')[:36]}  ev:", str(r.get("evidence"))[:120])
        n += 1
