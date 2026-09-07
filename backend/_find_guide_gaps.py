# -*- coding: utf-8 -*-
"""Compare data.js 4-year univs against local guide PDFs to find gaps."""
import re, json, os, glob

# Parse data.js properly
txt = open(r'C:\Users\USER\camnemi-crm\data.js', encoding='utf-8').read()
start = txt.find('[')
# find matching close bracket
depth = 0
end = None
for i in range(start, len(txt)):
    if txt[i] == '[': depth += 1
    elif txt[i] == ']':
        depth -= 1
        if depth == 0:
            end = i
            break
data = json.loads(txt[start:end+1])

# 4-year univs (type univ) vs junior
univs = [d for d in data if d.get('type') == 'univ']
juniors = [d for d in data if d.get('type') == 'junior']
print(f'4년제: {len(univs)} | 전문대: {len(juniors)}')

# Local guide lookup helper
def local_guides(folder):
    guides = {}
    for fp in glob.glob(os.path.join(folder, '*.pdf')):
        fn = os.path.basename(fp)
        fn2 = re.sub(r'^0000\d+_', '', fn)
        fn2 = re.sub(r'_20(26|27)_외국인.*', '', fn2)
        fn2 = re.sub(r'\[.*?\]', '', fn2).strip()
        guides[fn2] = fp
    return guides

g2027 = local_guides(r'C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2027_외국인_모집요강/외국인')
g2026 = local_guides(r'C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_외국인_모집요강/외국인')
# MA guides
gma = {}
for fp in glob.glob(r'C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/*.pdf'):
    fn = os.path.basename(fp).replace('_대학원_모집요강.pdf','').replace('_2026전기_일반대학원_국문','')
    gma[fn] = fp

# check each univ: does it have a local guide (any source)?
missing = []
for u in univs:
    n = u['n']
    found = False
    # try match by key name against normalized guide names
    for src_name in [n, n.replace('대학교','대'), n.replace('학교','')]:
        if src_name in g2027 or src_name in g2026 or any(src_name in k for k in g2027) or any(src_name in k for k in g2026):
            found = True
            break
        # guide name contains school name
        for k in list(g2027.keys()) + list(g2026.keys()):
            if n.replace('대학교','') in k or k in n or n in k:
                found = True
                break
        if found: break
    if not found:
        missing.append(n)

print(f'\\n=== 로컬 가이드 없는 4년제: {len(missing)}개 ===')
for m in sorted(missing):
    print(' ', m)
