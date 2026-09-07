# -*- coding: utf-8 -*-
"""Compute schools missing from partial result files, write fill-batch inputs."""
import json, glob, os

BASE = os.path.dirname(os.path.abspath(__file__))

def load_result(f):
    try:
        data = json.load(open(f, encoding='utf-8'))
        if isinstance(data, dict) and isinstance(data.get('schools'), list):
            data = data['schools']
        return [r.get('school', '') for r in data if isinstance(r, dict) and r.get('school')]
    except Exception:
        return []

missing_all = {'BA': [], 'MA': [], 'lang': []}
for track, d in [('BA', '_ba_batches'), ('MA', '_ma_batches'), ('lang', '_lang_batches')]:
    if not os.path.isdir(d):
        continue
    for fin in sorted(glob.glob(d + '/*.json')):
        base = os.path.basename(fin)
        if base.endswith('_result.json') or base.startswith('_'):
            continue
        inp = json.load(open(fin, encoding='utf-8'))
        in_schools = [r['school'] for r in inp]
        resf = fin.replace('.json', '_result.json')
        done = set(load_result(resf))
        missing = [s for s in in_schools if s not in done]
        if missing:
            print('{} {}: missing {} -> {}'.format(track, base, len(missing), ','.join(missing)))
            # preserve prior context rows for the missing schools
            by = {r['school']: r for r in inp}
            missing_all[track].extend(by[s] for s in missing)

for track in missing_all:
    if missing_all[track]:
        fn = os.path.join(BASE, '_fill_{}.json'.format(track.lower()))
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(missing_all[track], f, ensure_ascii=False, indent=1)
        print('WROTE {} ({} schools)'.format(fn, len(missing_all[track])))
