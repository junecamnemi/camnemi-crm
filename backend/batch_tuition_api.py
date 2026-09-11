#!/usr/bin/env python3
"""batch_tuition_api.py — fetch 2026 tuition for a list of universities from 대학알리미
and emit merge-ready JSON (per-semester KRW, aggregated by 계열)."""
import json, sys, time, statistics, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uni_tuition_api import find_schlid, depts, v8

# 대학알리미 학부 등록금 = ANNUAL 천원 -> per-semester KRW = val*1000/2
def per_sem(v):
    try: return int(round(float(str(v).strip()) * 500))
    except Exception: return None

def one(name, grad=False):
    ids = find_schlid(name)
    if not ids: return None
    sid = ids[0]
    ref, ds = depts(sid)
    if not ds: return None
    by = {}
    for smid, mid, nm, lclft, dght in ds:
        if not lclft: continue
        val = v8(sid, smid, mid, nm, ref)
        ps = per_sem(val) if val is not None else None
        if ps and ps > 0: by.setdefault(lclft, []).append(ps)
        time.sleep(0.05)
    if not by: return None
    fields = {k: int(statistics.median(v)) for k, v in by.items()}
    return {'univ': name, 'ba': {'min': min(fields.values()), 'max': max(fields.values()), 'fields': fields}}

if __name__ == '__main__':
    names = json.load(open(sys.argv[1], encoding='utf-8')) if len(sys.argv) > 1 and sys.argv[1].endswith('.json') else sys.argv[1:]
    out = []
    for n in names:
        try:
            r = one(n)
            if r:
                out.append(r)
                print(f"OK  {n}: {r['ba']['min']}~{r['ba']['max']} ({len(r['ba']['fields'])}계열)", flush=True)
            else:
                print(f"--  {n}: no data", flush=True)
        except Exception as e:
            print(f"ERR {n}: {str(e)[:60]}", flush=True)
        json.dump(out, open(r'C:\Users\USER\_acadinfo_tuition.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        time.sleep(0.8)
    print("saved", len(out))
