# -*- coding: utf-8 -*-
"""Merge per-track batch result files into _guide_2027_master.json and rebuild summary CSV.
Run after ALL subagent batches have completed. Never downgrades a confirmed 2027."""
import json, os, csv, glob, sys

BASE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(BASE, '_guide_2027_master.json')
SUMMARY = os.path.join(BASE, '_guide_2027_summary.csv')

TRACK_DIRS = {
    'ba':  ('_ba_batches',  'ba'),
    'ma':  ('_ma_batches',  'ma'),
    'lang': ('_lang_batches', 'lang'),
}

def load_master():
    return json.load(open(MASTER, encoding='utf-8'))

def save_master(m):
    tmp = MASTER + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    os.replace(tmp, MASTER)

def load_batch_results(dirname):
    rows = []
    for f in sorted(glob.glob(os.path.join(BASE, dirname, '*_result.json'))):
        try:
            data = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            print(f'  [warn] cannot parse {f}: {e}')
            continue
        if isinstance(data, list):
            rows.extend(data)
        elif isinstance(data, dict) and isinstance(data.get('schools'), list):
            rows.extend(data['schools'])
    return rows

def is_2027(status):
    return status in ('2027_guide', '2027_adiga', '2027_own', '2027')

def main():
    m = load_master()
    by_school = {r['school']: r for r in m}
    changed = []
    new_2027 = []
    for track, (dname, field) in TRACK_DIRS.items():
        results = load_batch_results(dname)
        print(f'[{track}] {len(results)} result rows from {dname}')
        for r in results:
            school = (r.get('school') or '').strip()
            status = (r.get('status') or '').strip()
            if not school or status in ('', 'pending'):
                continue
            row = by_school.get(school)
            if row is None:
                # append a new row for unknown school
                row = {'school': school, 'type': 'univ', 'ba_status': '', 'ba_url': '', 'ba_title': '', 'ba_note': '',
                       'lang_status': '', 'lang_url': '', 'lang_title': '', 'lang_note': '',
                       'ma_status': '', 'ma_url': '', 'ma_title': '', 'ma_note': '', 'name_en': ''}
                by_school[school] = row
                m.append(row)
            cur_status = row.get(field + '_status', '')
            url = r.get('url', '') or ''
            title = r.get('title', '') or ''
            note = r.get('note', '') or ''
            # Do not downgrade a confirmed 2027
            if is_2027(cur_status) and not is_2027(status):
                continue
            new_status = status
            if track == 'ba' and status == '2027_guide':
                new_status = '2027_own'   # own-site BA convention in master
            row[field + '_status'] = new_status
            if url:
                row[field + '_url'] = url
            if title:
                row[field + '_title'] = title
            if note:
                row[field + '_note'] = note
            changed.append((track, school, cur_status, '->', new_status))
            if is_2027(new_status):
                new_2027.append((track, school, url))
    save_master(m)
    print(f'\nChanged rows: {len(changed)}')
    for c in changed:
        print('  ', c)
    print(f'\nNEW/CONFIRMED 2027 rows: {len(new_2027)}')
    # ---- rebuild summary CSV ----
    with open(SUMMARY, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['school', 'type', 'BA', 'BA_url', 'MA', 'MA_url', 'lang', 'lang_url'])
        for r in m:
            w.writerow([r.get('school',''), r.get('type',''),
                        r.get('ba_status',''), r.get('ba_url',''),
                        r.get('ma_status',''), r.get('ma_url',''),
                        r.get('lang_status',''), r.get('lang_url','')])
    print(f'Summary written: {SUMMARY} ({len(m)} rows)')

if __name__ == '__main__':
    main()
