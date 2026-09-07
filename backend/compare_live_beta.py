import subprocess
# Check LIVE site vs BETA for the fix markers
r = subprocess.run(["curl", "-sL", "--max-time", "30", "https://junecamnemi.github.io/camnemi-crm/index.html"], capture_output=True, text=True)
live = r.stdout
r2 = subprocess.run(["curl", "-s", "--max-time", "10", "http://localhost:8833/index.html"], capture_output=True, text=True)
beta = r2.stdout
print("=== LIVE site ===")
print("  size:", len(live))
print("  flushPendingPush:", live.count("flushPendingPush"))
print("  __pendingPayload:", live.count("__pendingPayload"))
print("  local-wins dedupe:", live.count("cIsLocal"))
print("  BETA BYPASS:", live.count("BETA BYPASS"))
print("=== BETA (localhost:8833) ===")
print("  size:", len(beta))
print("  flushPendingPush:", beta.count("flushPendingPush"))
print("  __pendingPayload:", beta.count("__pendingPayload"))
print("  local-wins dedupe:", beta.count("cIsLocal"))
print("  BETA BYPASS:", beta.count("BETA BYPASS"))
