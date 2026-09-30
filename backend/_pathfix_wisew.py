import os

root = r"C:\Users\wisew\camnemi-crm"
pre = []
files = 0
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in ("__pycache__", ".git", "node_modules")]
    for f in fn:
        if not f.endswith(".py"):
            continue
        p = os.path.join(dp, f)
        try:
            s = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if "Users\\wisew" in s or "Users/wisew" in s:
            pre.append(p)
        s2 = (s.replace("Users\\\\wisew", "Users\\\\wisew")
               .replace("Users\\wisew", "Users\\wisew")
               .replace("Users/wisew", "Users/wisew"))
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            files += 1
print("pre-existing wisew files:", pre)
print("patched files:", files)
