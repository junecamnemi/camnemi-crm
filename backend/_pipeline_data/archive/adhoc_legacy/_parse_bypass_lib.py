# -*- coding: utf-8 -*-
"""Unified robust bypass parser: handles box output, truncated JSON, per-entry salvage.
Scans a directory of hermes output files."""
import json, os, re, sys

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp","bypass_mis")
OUTFILE = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\wisew\camnemi-crm\backend\_bypass_mis_structured.json"
BS = chr(92)

def answer_region(txt):
    k = txt.find("Initializing agent")
    seg = txt[k:] if k >= 0 else txt
    seg = re.sub(r"\x1b\[[0-9;]*m", "", seg)
    # cut off the post-run footer
    for endm in ["Resume this session with:", "Session:"]:
        e = seg.find(endm)
        if e > 0: seg = seg[:e]; break
    return seg

def salvage_entries(text):
    """Yield (key, value) for every '"KEY": { ... }' whose value has structured paths."""
    out = []
    for m in re.finditer(r'"([^"]{2,60})"\s*:\s*\{', text):
        key = m.group(1); st = m.end()-1
        depth=0; in_str=False; esc=False
        for j in range(st, len(text)):
            c = text[j]
            if in_str:
                if esc: esc=False
                elif c==BS: esc=True
                elif c=='"': in_str=False
            else:
                if c=='"': in_str=True
                elif c=="{": depth+=1
                elif c=="}":
                    depth-=1
                    if depth==0:
                        try:
                            v = json.loads(text[st:j+1])
                            p = v.get("paths")
                            if isinstance(p,list) and all(isinstance(x,dict) and "type" in x for x in p):
                                out.append((key, v))
                        except Exception:
                            pass
                        break
    return out

all_paths = {}
files = sorted(f for f in os.listdir(OUTDIR) if f.endswith("_out.txt"))
for fn in files:
    txt = open(os.path.join(OUTDIR, fn), encoding="utf-8", errors="ignore").read()
    seg = answer_region(txt)
    got = 0
    for key, v in salvage_entries(seg):
        if key in ("school_name|level",): continue
        all_paths[key] = v; got += 1
    print(f"  {fn}: {got}")

print(f"\n총: {len(all_paths)}")
json.dump(all_paths, open(OUTFILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUTFILE)
