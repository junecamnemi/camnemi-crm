import json, sys, os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BA_batch_06_result.json')
with open(path, 'r', encoding='utf-8') as f:
    results = json.load(f)

updates = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []
for u in updates:
    for r in results:
        if r['school'] == u['school']:
            for k, v in u.items():
                if k != 'school':
                    r[k] = v
            break
    else:
        results.append(u)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print('OK', len(results))
