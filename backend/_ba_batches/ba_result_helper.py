import json, sys, io

PATH = r"C:/Users/USER/camnemi-crm/backend/_ba_batches/BA_batch_01_result.json"

def load():
    try:
        with io.open(PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save(results):
    with io.open(PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("SAVED", len(results))

def upsert(school, status, url, title, note):
    results = load()
    results = [r for r in results if r.get("school") != school]
    results.append({"school": school, "status": status, "url": url, "title": title, "note": note})
    save(results)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "upsert":
        upsert(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif cmd == "show":
        for r in load():
            print(json.dumps(r, ensure_ascii=False))
