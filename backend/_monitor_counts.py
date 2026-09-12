import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'consulting_db.json'
d = json.load(open(path, encoding='utf-8'))
sch = d.get('schools', {})
pm = 0
majors = 0
nmajors = 0
levels = {}
for k, v in sch.items():
    progs = v.get('programs', {}) if isinstance(v, dict) else {}
    for lvl, p in progs.items():
        if not isinstance(p, dict):
            continue
        levels[lvl] = levels.get(lvl, 0) + 1
        pm += len(p.get('popular_majors') or [])
        m = p.get('majors')
        if isinstance(m, list):
            majors += len(m)
        nmajors += (p.get('n_majors') or 0) if isinstance(p.get('n_majors'), (int, float)) else 0
print(json.dumps({
    'file': path,
    'school_count': len(sch),
    'popular_majors_total': pm,
    'majors_list_total': majors,
    'n_majors_total': nmajors,
    'level_program_counts': levels,
}, ensure_ascii=False))
