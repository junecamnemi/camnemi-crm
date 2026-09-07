import subprocess, json
# Check pages config
for url in [
  "https://api.github.com/repos/junecamnemi/camnemi-crm/pages",
]:
    r = subprocess.run(["curl", "-s", "--max-time", "30", url], capture_output=True, text=True)
    print(url)
    print(r.stdout[:600])
    print("---")
