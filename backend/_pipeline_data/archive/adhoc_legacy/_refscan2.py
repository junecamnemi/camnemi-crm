import os, re, json, glob

BACKEND = r'C:/Users/wisew/camnemi-crm/backend'
SCAN_DIRS = [BACKEND, r'C:/Users/wisew/AppData/Local/hermes/profiles/univ/skills',
             r'C:/Users/wisew/AppData/Local/hermes/profiles/camnemi_admin/skills']
SCAN_FILES = [r'C:/Users/wisew/AppData/Local/hermes/profiles/univ/cron/jobs.json',
              r'C:/Users/wisew/camnemi-crm/ARCHITECTURE.md']
SKIP = ('.git', 'node_modules', '__pycache__', 'site-packages', 'sessions', 'cache', 'output')
EXT = ('.py', '.bat', '.ps1', '.cmd', '.sh', '.yml', '.yaml', '.md', '.json')
names = sorted(os.path.basename(p) for p in glob.glob(BACKEND + '/_*.py'))
pat = re.compile('|'.join(re.escape(n) for n in names))
found = {}
def scan(fp):
    if os.path.splitext(fp)[1].lower() not in EXT:
        return
    try:
        if os.path.getsize(fp) > 3_000_000:
            return
        text = open(fp, encoding='utf-8', errors='ignore').read()
    except OSError:
        return
    for m in set(pat.findall(text)):
        if m != os.path.basename(fp):
            found.setdefault(m, []).append(fp)

for d in SCAN_DIRS:
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = [x for x in dirnames if x not in SKIP]
        if '_pipeline_data' in dirpath:
            continue
        for fn in filenames:
            scan(os.path.join(dirpath, fn))
for fp in SCAN_FILES:
    if os.path.exists(fp):
        scan(fp)

kind = {}
for name, refs in found.items():
    rels = [os.path.relpath(r, 'C:/Users/wisew').replace(chr(92), '/') for r in refs]
    clock = any('/cron/' in r or 'jobs.json' in r for r in rels)
    code = any(os.path.splitext(r)[1].lower() in ('.py', '.bat', '.ps1', '.cmd', '.sh', '.yml', '.yaml') for r in rels)
    doc = any(r.endswith('.md') for r in rels)
    kind[name] = 'cron' if clock else ('code' if code else ('doc' if doc else 'other'))
    print('%-34s %-6s <- %s' % (name, kind[name], rels[0]))

json.dump({'kind': kind, 'refs': {k: v for k, v in found.items()}},
          open(BACKEND + '/_pipeline_data/archive/_refscan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
orphans = [n for n in names if n not in found]
print()
print('total ad-hoc scripts:', len(names))
for k in ('cron', 'code', 'doc', 'other'):
    print('  %-6s: %d' % (k, sum(1 for v in kind.values() if v == k)))
print('orphans (no code/cron/doc reference):', len(orphans))
json.dump(orphans, open(BACKEND + '/_pipeline_data/archive/_orphans.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)