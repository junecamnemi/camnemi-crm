import json, sys, os

def merge_entry(path, school, status, url, title, note):
    data = []
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"WARN: could not parse {path}: {e}; starting fresh")
            data = []
    if not isinstance(data, list):
        data = []
    entry = {"school": school, "status": status, "url": url, "title": title, "note": note}
    data = [e for e in data if e.get("school") != school]
    data.append(entry)
    data.sort(key=lambda e: e.get("school", ""))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"OK {path}: {len(data)} entries")

if __name__ == "__main__":
    path, school, status, url, title, note = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
    merge_entry(path, school, status, url, title, note)
