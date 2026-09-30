import os, re, json, glob
ROOTS = [r'C:/Users/wisew/AppData/Local/hermes', r'C:/Users/wisew/camnemi-crm']
SKIP = ('.git', 'node_modules', 'guides', '_pipeline_data', 'site-packages', '__pycache__')
names = sorted(os.path.basename(p) for p in glob.glob(r'C:/Users/wisew/camnemi-crm/backend/_*.py'))
pat = re.compile('|'.join(re.escape(n) for n in names))
hits, scanned = {}, 0
for root in ROOTS:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in ('.py', '.json', '.bat', '.ps1', '.cmd', '.yml', '.yaml', '.md', '.txt', '.sh'):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(fp) > 3_000_000:
                    continue
                text = open(fp, encoding='utf-8', errors='ignore').read()
            except OSError:
                continue
            scanned += 1
            for m in set(pat.findall(text)):
                if m != fn:
                    hits.setdefault(m, []).append(fp)
print('scanned files:', scanned)
print('ad-hoc scripts referenced elsewhere:', len(hits))
keep = sorted(hits)
json.dump({'keep': keep, 'refs': {k: v[:4] for k, v in hits.items()}}, open('_pipeline_data/archive/_refscan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k in keep:
    print('   %-34s <- %s' % (k, os.path.relpath(hits[k][0], 'C:/Users/wisew').replace(chr(92), '/')))
print('orphan count:', len(names) - len(keep), 'of', len(names))
