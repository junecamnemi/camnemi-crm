"""
Download all university logos from adiga.kr into C:\\Users\\wisew\\univ_logos\\
and update the customer-pipeline.html UNIV_KNOWLEDGE.logo to local file:// paths.

Re-run whenever you want to refresh the logo set.
"""
import os, json, hashlib, urllib.request

DATA = r"C:\Users\wisew\OneDrive\University AI\adiga_외국인모집요강\data"
HTML = r"C:\Users\wisew\customer-pipeline.html"
LOGO_DIR = r"C:\Users\wisew\univ_logos"

info = json.load(open(os.path.join(DATA, "university_info.json"), encoding="utf-8"))
logos = {v["name"]: v.get("logo", "") for v in info.values() if v.get("logo")}

os.makedirs(LOGO_DIR, exist_ok=True)
for name, url in logos.items():
    safe = hashlib.md5(name.encode()).hexdigest()[:10]
    path = os.path.join(LOGO_DIR, safe + ".png")
    if os.path.exists(path):
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        open(path, "wb").write(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:
        print("FAIL", name, e)

def local_logo(name):
    safe = hashlib.md5(name.encode()).hexdigest()[:10]
    p = os.path.join(LOGO_DIR, safe + ".png")
    return ("file:///" + p.replace("\\", "/")) if os.path.exists(p) else ""

h = open(HTML, encoding="utf-8").read()
start = h.index("const UNIV_KNOWLEDGE = ") + len("const UNIV_KNOWLEDGE = ")
depth = 0; end = None
for i in range(start, len(h)):
    if h[i] == "[": depth += 1
    elif h[i] == "]":
        depth -= 1
        if depth == 0:
            end = i + 1; break
arr = json.loads(h[start:end])
for r in arr:
    r["logo"] = local_logo(r["n"])
h = h[:start] + json.dumps(arr, ensure_ascii=False) + h[end:]
open(HTML, "w", encoding="utf-8").write(h)
print("Updated logos:", sum(1 for r in arr if r["logo"]), "of", len(arr))
