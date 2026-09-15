"""Re-attach enrichment fields dropped by the consulting DB rebuild.

Only keys that exist in the backup but are missing in the freshly built DB are
copied back; everything the rebuild produced (levels, tuition, topik/ielts,
popular_majors, periods) is left untouched.
"""
import json
import sys

BAK = 'consulting_db_bak_monitor_20260916_0801.json'
CUR = 'consulting_db.json'

bak = json.load(open(BAK, encoding='utf-8'))
cur = json.load(open(CUR, encoding='utf-8'))

summary = {}
for name, s in bak.get('schools', {}).items():
    tp = (cur['schools'].get(name) or {}).get('programs') or {}
    for lvl, p in (s.get('programs') or {}).items():
        if not isinstance(p, dict):
            continue
        q = tp.get(lvl)
        if not isinstance(q, dict):
            continue
        for k, v in p.items():
            if k not in q and v not in (None, '', [], {}):
                q[k] = v
                key = f'{lvl}.{k}'
                summary[key] = summary.get(key, 0) + 1

json.dump(cur, open(CUR, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('restored fields:', json.dumps(summary, ensure_ascii=False))
