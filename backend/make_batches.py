# -*- coding: utf-8 -*-
"""Split _daily_pending.json into per-track batches of ~12, write input files."""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(BASE, '_daily_pending.json'), encoding='utf-8'))

BATCH_SIZE = 12
out_meta = {}
for tr in ['BA', 'MA', 'lang']:
    rows = d[tr]
    batch_dir = os.path.join(BASE, f'_{tr.lower()}_batches')
    os.makedirs(batch_dir, exist_ok=True)
    batches = [rows[i:i+BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    metas = []
    for bi, batch in enumerate(batches, 1):
        fn = f'{tr}_batch_{bi:02d}.json'
        with open(os.path.join(batch_dir, fn), 'w', encoding='utf-8') as f:
            json.dump(batch, f, ensure_ascii=False, indent=1)
        metas.append({'file': fn, 'n': len(batch),
                      'schools': [r['school'] for r in batch]})
    out_meta[tr] = metas
    print(f'{tr}: {len(batches)} batches, {len(rows)} schools')

with open(os.path.join(BASE, '_batch_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(out_meta, f, ensure_ascii=False, indent=1)

# print compact manifest for dispatch
for tr in ['BA', 'MA', 'lang']:
    print(f'\n===== {tr} =====')
    for m in out_meta[tr]:
        print(f'{m["file"]} ({m["n"]}): {",".join(m["schools"])}')
