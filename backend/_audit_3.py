import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
kb = json.load(open('verified_kb.json', encoding='utf-8'))

def nz(v):
    if v is None: return False
    if isinstance(v,(list,dict)): return len(v)>0
    if isinstance(v,str): return v.strip() not in ('','-','미정','없음','N/A')
    return True

def has(d, keys):
    return any(nz(d.get(k)) for k in keys)

TU = ['tuition_semester','tuition_min','tuition','tuition_range','foreign_tuition','tuition_per_college_semester']
SC = ['scholarships','scholarships_categorized','scholarship','scholarship_curated']
PE = ['period','foreign_period','period_2027','period_note']
TO = ['topik_req','foreign_topik']
IE = ['ielts_req']
MA = ['majors','majors_full','majors_sample','majors_ba','majors_ma','foreign_majors','n_majors']

levels = {
 'BA(schools)': kb['schools'],
 'MA(master)': kb['master']['schools'],
 'JUNIOR': kb['junior']['schools'],
 'LANG': kb['lang_programs']['schools'],
}
rows=[]
for name,d in levels.items():
    n=len(d)
    r={'level':name,'n':n}
    for lbl,ks in [('tuition',TU),('scholarship',SC),('period',PE),('topik_req',TO),('ielts_req',IE),('majors',MA)]:
        c=sum(1 for v in d.values() if isinstance(v,dict) and has(v,ks))
        r[lbl]=f"{c}/{n} ({c*100//n}%)"
    rows.append(r)
hdr=['level','n','tuition','scholarship','period','topik_req','ielts_req','majors']
print("=== 2. verified_kb field coverage ===")
print(" | ".join(h.ljust(16) for h in hdr))
for r in rows: print(" | ".join(str(r[h]).ljust(16) for h in hdr))

# missing lists (top few)
print("\n-- BA missing tuition:", [k for k,v in kb['schools'].items() if not has(v,TU)])
print("-- BA missing scholarship (count):", sum(1 for v in kb['schools'].values() if not has(v,SC)))
print("   sample:", [k for k,v in kb['schools'].items() if not has(v,SC)][:25])
print("-- MA missing scholarship:", [k for k,v in kb['master']['schools'].items() if not has(v,SC)][:30])
print("-- LANG missing period:", sum(1 for v in kb['lang_programs']['schools'].values() if not has(v,PE)))
print("-- LANG has topik/ielts:", sum(1 for v in kb['lang_programs']['schools'].values() if has(v,TO+IE)))
print("-- LANG has scholarship:", sum(1 for v in kb['lang_programs']['schools'].values() if has(v,SC)))
