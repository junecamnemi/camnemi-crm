#!/usr/bin/env python3
"""merge_scholarships_json.py — merge subagent-collected scholarship JSON (from
official university 장학금 pages) into universities.scholarships.

Input: [{"univ":"한양대학교","scholarships":[{name,type,level,tiers:[...]}]}, ...]
(or a dict keyed by name). Appends to scholarships_llm.jsonl in the parser's shape
and re-runs merge_scholarships.main() so the merge logic stays in one place.

Usage: python merge_scholarships_json.py <file.json> [more.json ...]
"""
import json, os, sys, glob

BASE = os.path.dirname(os.path.abspath(__file__))
JSONL = os.path.join(BASE, 'scholarships_llm.jsonl')

def load_records(paths):
    recs = []
    for p in paths:
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print("skip", p, e); continue
        if isinstance(d, dict):
            d = list(d.values()) if all(isinstance(v, dict) for v in d.values()) else [d]
        for r in (d or []):
            if isinstance(r, dict) and r.get('univ'):
                recs.append(r)
    return recs

def main():
    paths = sys.argv[1:]
    if not paths:
        paths = glob.glob(r'C:\Users\USER\_schol_*.json')
    recs = load_records(paths)
    print(f"loaded {len(recs)} records from {len(paths)} files")
    # normalize into the parser JSONL shape
    n = 0
    with open(JSONL, 'a', encoding='utf-8') as f:
        for r in recs:
            schs = r.get('scholarships')
            if not isinstance(schs, list) or not schs: continue
            f.write(json.dumps({'_id': 'manual_' + r['univ'], 'school': r['univ'],
                                'scholarships': schs, '_prog': 'ba'}, ensure_ascii=False) + "\n")
            n += 1
    print(f"appended {n} records")
    # run the shared merge
    import importlib
    sys.path.insert(0, BASE)
    ms = importlib.import_module('merge_scholarships')
    ms.main()

if __name__ == '__main__':
    main()
