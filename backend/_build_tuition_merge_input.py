#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build merge_tuition.py input from tuition_by_department.json.

Maps school × level (BA/MA) → {ba:{min,max,fields}, ma:{min,max,fields}} where
fields = {college/계열 name: krw}. 전문학사/전공심화 are NOT written here — the
universities_blob view only exposes ba/ma tuition; junior belongs in cat.tuition
(Phase 3). Skip rows with non-positive krw; exclude the '(미분류)' sentinel.
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'tuition_by_department.json')
OUT = os.path.join(BASE, '_merge_tuition_input.json')

def main():
    d = json.load(open(SRC, encoding='utf-8'))
    schools = d['schools']
    recs = []
    for name, lv in schools.items():
        if not isinstance(lv, dict):
            continue
        rec = {'univ': name}
        for key in ('BA', 'MA'):
            blk = lv.get(key)
            if not isinstance(blk, dict):
                continue
            rows = blk.get('rows') or []
            fields = {}
            for r in rows:
                if not isinstance(r, dict):
                    continue
                c = (r.get('college') or '').strip()
                krw = r.get('krw')
                if not c or c == '(미분류)' or not isinstance(krw, (int, float)) or krw <= 0:
                    continue
                fields[c] = int(krw)
            if not fields:
                continue
            vals = list(fields.values())
            rec[key.lower()] = {'min': min(vals), 'max': max(vals), 'fields': fields}
        if any(k in rec for k in ('ba', 'ma')):
            recs.append(rec)
    json.dump(recs, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    nba = sum(1 for r in recs if 'ba' in r)
    nma = sum(1 for r in recs if 'ma' in r)
    print(f"records={len(recs)}  (ba={nba}, ma={nma})  -> {OUT}")

if __name__ == '__main__':
    main()
