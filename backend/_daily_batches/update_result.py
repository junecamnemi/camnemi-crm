import json, sys, os

def update(filepath, school, status, url, title, note):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    entry = {"school": school, "status": status, "url": url, "title": title, "note": note}
    data = [e for e in data if e.get("school") != school]
    data.append(entry)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # verify
    with open(filepath, 'r', encoding='utf-8') as f:
        json.load(f)
    print(f"OK {school} -> {status} in {os.path.basename(filepath)}")

if __name__ == '__main__':
    filepath, school, status, url, title, note = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
    update(filepath, school, status, url, title, note)
