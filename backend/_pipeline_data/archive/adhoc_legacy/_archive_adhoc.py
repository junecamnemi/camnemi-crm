"""One-time consolidation: move the unreferenced ad-hoc scripts out of backend/ into
_pipeline_data/archive/adhoc_legacy/ (reversible, with a manifest + README index)."""
import json, os, re, shutil
from pathlib import Path

BACKEND = Path(r'C:/Users/wisew/camnemi-crm/backend')
ARCH = BACKEND / '_pipeline_data' / 'archive'
DEST = ARCH / 'adhoc_legacy'
DEST.mkdir(parents=True, exist_ok=True)

keep = json.load(open(ARCH / '_refscan.json', encoding='utf-8'))['kind']
orphans = json.load(open(ARCH / '_orphans.json', encoding='utf-8'))
print('cron/code/doc referenced (kept in place):', len(keep), '| orphans to archive:', len(orphans))


def purpose(path: Path) -> str:
    try:
        text = open(path, encoding='utf-8', errors='ignore').read(4000)
    except OSError:
        return ''
    m = re.search(r'^\s*(?:"""|\'\'\'|#)\s*(.+)', text, re.M)
    if m:
        line = m.group(1).strip().strip('"\'')
        if line and not line.startswith('!'):
            return line[:150]
    m = re.search(r'^#\s*(.+)', text, re.M)
    return m.group(1).strip()[:150] if m else ''


moved, missing = [], []
for name in orphans:
    src = BACKEND / name
    if not src.is_file():
        missing.append(name)
        continue
    shutil.move(str(src), str(DEST / name))
    moved.append({'name': name, 'from': str(src), 'to': str(DEST / name), 'purpose': purpose(DEST / name)})

json.dump({'moved_at': __import__('datetime').datetime.now().isoformat(timespec='seconds'),
           'count': len(moved), 'kept_in_place': sorted(keep), 'missing': missing, 'files': moved},
          open(ARCH / 'adhoc_legacy_MANIFEST.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

groups = {}
for item in moved:
    groups.setdefault(item['name'].split('_')[1] if item['name'].count('_') > 1 else 'misc', []).append(item)
lines = ['# ad-hoc legacy scripts (archived 2026-09-29)',
         '',
         f'{len(moved)} one-off scripts that **nothing references** (no import, no subprocess, no cron job,',
         'no skill doc) were moved out of `backend/` so the guide pipeline has ONE management point:',
         '',
         '- collector `backend/guide_page_collect.py` · census `backend/guide_census.py` ·',
         '  entry point `backend/run_guide_kb_pipeline.py` · data home `backend/_pipeline_data/`',
         '',
         f'Scripts still referenced by cron/code/docs stay in `backend/` ({len(keep)} of them) and are listed',
         'in `adhoc_legacy_MANIFEST.json` → `kept_in_place`.',
         '',
         '## Restore everything',
         '',
         '```bash',
         'cd /c/Users/wisew/camnemi-crm/backend/_pipeline_data/archive',
         'python -c "import json,shutil;m=json.load(open(\'adhoc_legacy_MANIFEST.json\'));[shutil.move(f[\'to\'],f[\'from\']) for f in m[\'files\']]"',
         '```',
         '',
         '## What is here (grouped by script prefix)',
         '']
for g in sorted(groups):
    lines.append(f'### `_{g}_*` ({len(groups[g])})')
    for item in sorted(groups[g], key=lambda x: x['name']):
        lines.append(f"- `{item['name']}`" + (f" — {item['purpose']}" if item['purpose'] else ''))
    lines.append('')
(DEST / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
print('moved:', len(moved), '| missing:', len(missing))
print('README:', DEST / 'README.md')
print('still in backend/:', len([p for p in BACKEND.glob('_*.py')]))