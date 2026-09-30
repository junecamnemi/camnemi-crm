# -*- coding: utf-8 -*-
"""Re-download the current (2027) guide for the 6 no-guide slots + 11 ambiguous pairs.
Uses backend/guide_fetch.py per target (download + %PDF validation + library filing).
Writes results to _pipeline_data/reports/_redl_results.json"""
import json, os, subprocess, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
OUT = os.path.join(HERE, "_pipeline_data", "reports", "_redl_results.json")

scrape = json.load(open(os.path.join(HERE, "scrape_map.json"), encoding="utf-8"))

TARGETS = [
    # (school, level, why)
    ("동국대학교", "ba", "no_guide"),
    ("수원대학교", "ba", "no_guide"),
    ("신경주대학교", "ba", "no_guide"),
    ("차의과학대학교", "ba", "no_guide"),
    ("부산경상대학교", "junior", "no_guide"),
    ("극동대학교", "ma", "no_guide"),
    ("경북대학교", "ba", "ambiguous"),
    ("고신대학교", "ba", "ambiguous"),
    ("국립공주대학교", "ba", "ambiguous"),
    ("선문대학교", "ba", "ambiguous"),
    ("신구대학교", "junior", "ambiguous"),
    ("연세대학교", "lang", "ambiguous"),
    ("연세대학교", "ma", "ambiguous"),
    ("우송대학교", "ba", "ambiguous"),
    ("이화여자대학교", "lang", "ambiguous"),
    ("장안대학교", "junior", "ambiguous"),
    ("한세대학교", "ba", "ambiguous"),
]


def cached(school, lv):
    for k in (school, school.replace("대학교", "대")):
        ent = scrape.get(k)
        if isinstance(ent, dict):
            v = ent.get(lv)
            if isinstance(v, dict) and v.get("url"):
                return v["url"]
            if isinstance(v, str) and v.startswith("http"):
                return v
    return None


results = []
for school, lv, why in TARGETS:
    url = cached(school, lv)
    if not url:
        results.append({"school": school, "level": lv, "why": why, "url": None,
                        "result": "no_cached_url"})
        print(f"NO-URL {school} [{lv}]")
        continue
    cmd = [PY, "guide_fetch.py", "--url", url, "--school", school, "--level", lv, "--year", "2027"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=HERE)
        out = (p.stdout or "") + (p.stderr or "")
        tail = out.strip().splitlines()[-6:]
        ok = p.returncode == 0
        results.append({"school": school, "level": lv, "why": why, "url": url,
                        "result": "ok" if ok else f"exit{p.returncode}",
                        "log": tail})
        print(f"{'OK ' if ok else 'FAIL'} {school} [{lv}]  exit={p.returncode}")
        for t in tail:
            print("      " + t)
    except Exception as e:
        results.append({"school": school, "level": lv, "why": why, "url": url,
                        "result": f"error:{e}"})
        print(f"ERR  {school} [{lv}] {e}")

json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
c = collections.Counter(r["result"] for r in results)
print("\nsummary:", dict(c))
print("written:", OUT)