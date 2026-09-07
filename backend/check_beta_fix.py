import subprocess
h = subprocess.run(["curl", "-s", "--max-time", "30", "http://localhost:8833/index.html"], capture_output=True, text=True).stdout
checks = {
  "BETA BYPASS (login skip)": "BETA BYPASS" in h,
  "flushPendingPush": h.count("flushPendingPush") >= 3,
  "__pendingPayload": h.count("__pendingPayload") >= 3,
  "exportAllData updated_at": "updated_at: card.dataset.updated_at" in h,
  "syncPush(snapshot)": "syncPush(snapshot)" in h,
  "boot flush": "flushPendingPush();" in h,
}
for k, v in checks.items(): print(("OK " if v else "MISSING ") + k)
print("size:", len(h))
