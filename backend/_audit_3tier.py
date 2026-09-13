import json, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))

kb = json.load(open('verified_kb.json', encoding='utf-8'))
print("=== 1. verified_kb top-level keys ===")
for k, v in kb.items():
    if isinstance(v, dict):
        print(f"  {k}: dict({len(v)}) subkeys={list(v.keys())[:8]}")
    elif isinstance(v, list):
        print(f"  {k}: list({len(v)})")
    else:
        print(f"  {k}: {type(v).__name__} = {str(v)[:60]}")
