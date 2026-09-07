# -*- coding: utf-8 -*-
import json, os, re, glob

D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
files = [f for f in glob.glob(os.path.join(D, "*.txt")) if not f.endswith("_meta.json") and "_extract" not in f]

# For each school file, find mentions of its department and print window context.
# dept per filename keyword: 치의예과 / 한의예과 / 수의예과
kw_byfile = {}
for f in files:
    base = os.path.basename(f)
    if "치의예과" in base: kw = "치의예과"
    elif "한의예과" in base: kw = "한의예과"
    elif "수의예과" in base: kw = "수의예과"
    else: continue
    kw_byfile[f] = kw

for f in sorted(files):
    base = os.path.basename(f)
    kw = kw_byfile.get(f)
    if kw is None:
        continue
    txt = open(f, encoding="utf-8").read()
    # search keywords for recruitment context
    print("="*100)
    print("FILE:", base, "| kw:", kw, "| len", len(txt))
    # find mentions of kw with window
    for m in re.finditer(re.escape(kw), txt):
        s = max(0, m.start()-120); e = min(len(txt), m.end()+160)
        seg = txt[s:e].replace("\n", " ")
        print(f"  [{kw}] ...{seg}...")
