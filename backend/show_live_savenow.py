import subprocess, re
r = subprocess.run(["curl", "-sL", "--max-time", "30", "https://junecamnemi.github.io/camnemi-crm/index.html?v=" + str(int(__import__("time").time()*1000))], capture_output=True, text=True)
h = r.stdout
# extract saveNow function
m = re.search(r"function saveNow\(\) \{[\s\S]*?\n  \}", h)
print(m.group(0) if m else "saveNow NOT FOUND")
