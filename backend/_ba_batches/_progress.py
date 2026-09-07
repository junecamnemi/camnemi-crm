import json, sys, os

path = r"C:/Users/USER/camnemi-crm/backend/_ba_batches/BA_batch_03_result.json"

if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        results = json.load(f)
else:
    results = []

# input: JSON string on argv[1] = single school result to append/replace
item = json.loads(sys.argv[1])
done = [s for s in results if s.get("school") != item["school"]]
done.append(item)
with open(path, "w", encoding="utf-8") as f:
    json.dump(done, f, ensure_ascii=False, indent=1)
print("OK", len(done))
