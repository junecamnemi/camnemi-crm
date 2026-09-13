import json, os
os.chdir(r"C:\Users\USER\camnemi-crm")
arr=json.load(open(r'backend\_djs_parsed.json',encoding='utf-8'))
kb=json.load(open(r'backend\verified_kb.json',encoding='utf-8'))
D={x['n']:x for x in arr}
BA=kb['schools']; MA=kb['master']['schools']; JR=kb['junior']['schools']; LG=kb['lang_programs']['schools']
def nz(v):
    if v is None: return False
    if isinstance(v,(list,dict)): return len(v)>0
    if isinstance(v,str): return v.strip() not in ('','-','not_checked','unknown')
    return True
def kbhas(v,ks): return any(nz(v.get(k)) for k in ks)

print("=== 5. KB -> data.js 누락 ===")
print("school presence:")
for lbl,d in [('BA',BA),('MA',MA),('JR',JR),('LANG',LG)]:
    miss=[k for k in d if k not in D]
    print(f"  {lbl}: KB {len(d)} / data.js에 없음 {len(miss)}", miss[:12])

def gap(lbl, d, kbks, dfn):
    g=[k for k,v in d.items() if kbhas(v,kbks) and (k not in D or not dfn(D[k]))]
    print(f"  [{lbl}] KB有 & data.js無: {len(g)}  sample={g[:12]}")
    return g
print("\nfield gaps:")
SC=['scholarships','scholarships_categorized','scholarship','scholarship_curated']
g1=gap('BA scholarship', BA, SC, lambda x: nz(x.get('scholarships')))
g2=gap('BA period', BA, ['period'], lambda x: nz(x.get('period')))
g3=gap('BA tuition', BA, ['tuition_semester','tuition_min'], lambda x: isinstance(x.get('tuition'),dict) and (x['tuition'].get('ba') or {}).get('min') is not None)
g4=gap('BA ielts', BA, ['ielts_req'], lambda x: nz(x.get('i')) or nz((x.get('req') or {}).get('ielts')))
g5=gap('MA tuition', MA, ['tuition','tuition_min','tuition_semester'], lambda x: isinstance(x.get('tuition'),dict) and (x['tuition'].get('ma') or {}).get('min') is not None)
g6=gap('MA scholarship', MA, SC, lambda x: nz(x.get('scholarships')))
g7=gap('MA period', MA, ['period'], lambda x: nz(x.get('period')))
g8=gap('JR scholarship', JR, SC, lambda x: nz(x.get('scholarships')))
g9=gap('JR tuition', JR, ['tuition_min','tuition_semester'], lambda x: isinstance(x.get('tuition'),dict) and any((x['tuition'].get(k) or {}).get('min') is not None for k in ('ba','ma')))
g10=gap('JR period', JR, ['period'], lambda x: nz(x.get('period')))
g11=gap('LANG tuition', LG, ['tuition_range'], lambda x: False)  # data.js has no lang tuition field at all
print("\n  [LANG] data.js에 어학 학비/기간 필드 자체 없음 (lang_guide URL만 137개)")
# how many data.js entries carry any lang data field
print("  data.js keys containing 'lang':", sorted({k for x in arr for k in x if 'lang' in k}))
# visa restricted propagation
print("\nvisa_restricted_2026 표시 여부 in data.js:", sum(1 for x in arr if 'visa_restricted_2026' in x or 'visa' in json.dumps(x, ensure_ascii=False)))
# free_major / ai_departments / medical propagation
for sec in ['free_major_programs','ai_departments']:
    names=list(kb[sec]['schools'].keys()) if isinstance(kb[sec]['schools'],dict) else kb[sec]['schools']
    print(f"{sec}: {len(names)} schools; data.js에 해당 플래그 필드 존재? ", any(sec.split('_')[0] in k for x in arr for k in x))
print("medical_reqs: data.js 반영 필드 존재?", any('medical' in k for x in arr for k in x))
json.dump({'BA_sch':g1,'BA_period':g2,'BA_tuition':g3,'BA_ielts':g4,'MA_tuition':g5,'MA_sch':g6,'MA_period':g7,'JR_sch':g8,'JR_tuition':g9,'JR_period':g10}, open(r'backend\_gaps_audit.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
