# -*- coding: utf-8 -*-
"""Robust parser: extract per-school blocks independently so one broken entry
doesn't kill the whole batch. Salvages valid entries, reports broken ones."""
import json, os, re, glob

OUTDIR = os.path.join(os.environ.get("LOCALAPPDATA",""), "Temp","bypass_pro")
BS = chr(92)

def find_objects(text):
    """All balanced {...} objects."""
    objs=[]; i=0
    while i < len(text):
        if text[i]=="{":
            depth=0; in_str=False; esc=False; start=i
            for j in range(i,len(text)):
                c=text[j]
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
                            objs.append(text[start:j+1]); i=j; break
            else: break
        i+=1
    return objs

def is_structured(v):
    p=v.get("paths")
    return isinstance(p,list) and len(p)>0 and all(isinstance(x,dict) and "type" in x for x in p)

all_paths={}; broken=[]
files=sorted(glob.glob(os.path.join(OUTDIR,"*_out.txt")))
for fp in files:
    txt=open(fp,encoding="utf-8",errors="ignore").read()
    k=txt.find("Initializing agent")
    seg=re.sub(r"\x1b\[[0-9;]*m","",txt[k:] if k>=0 else txt)
    got=0
    for raw in find_objects(seg):
        # try whole
        parsed=None
        try: parsed=json.loads(raw)
        except Exception:
            # try to salvage: regex each top-level "KEY": {...} entry
            for m in re.finditer(r'"([^"]+)"\s*:\s*(\{)', raw):
                key=m.group(1); st=m.start(2)
                # balance from st
                depth=0; in_str=False; esc=False
                for j in range(st,len(raw)):
                    c=raw[j]
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
                                    v=json.loads(raw[st:j+1])
                                    if is_structured(v): all_paths[key]=v; got+=1
                                except Exception: broken.append(f"{os.path.basename(fp)}:{key}")
                                break
            continue
        if isinstance(parsed,dict):
            for key,v in parsed.items():
                if isinstance(v,dict) and is_structured(v) and key!="school_name|level":
                    all_paths[key]=v; got+=1
    print(f"  {os.path.basename(fp)}: {got}")

print(f"\n총 구조화: {len(all_paths)} | 깨진 엔트리: {len(broken)}")
if broken: print("깨진:", broken[:10])
json.dump(all_paths, open(r"C:\Users\USER\camnemi-crm\backend\_bypass_structured.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
