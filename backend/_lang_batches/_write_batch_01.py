import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = r'C:/Users/USER/camnemi-crm/backend/_lang_batches/lang_batch_01_result.json'
data = json.load(sys.stdin)
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("WROTE", len(data), "records to", path)
