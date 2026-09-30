import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = json.load(open('consulting_db.json', encoding='utf-8'))
kb = json.load(open('verified_kb.json', encoding='utf-8'))
S=c['schools']
def nz(v):
    if v is None: return False
    if isinstance(v,(list,dict)): return len(v)>0
    if isinstance(v,str): return v.strip() not in ('','-','미정','없음','N/A','not_checked','unknown')
    return True
def has(d,ks): return any(nz(d.get(k)) for k in ks)
print("=== 3b. consulting_db coverage (correct keys) ===")
hdr=['level','n','tuition','scholarship','period','topik','ielts','majors']
print(" | ".join(h.ljust(14) for h in hdr))
for lvl in ['BA','MA','전문학사','어학연수']:
    progs=[s['programs'][lvl] for s in S.values() if lvl in s.get('programs',{})]
    n=len(progs); row=[lvl,str(n)]
    for ks in [['tuition','tuition_max'],['scholarship'],['period'],['topik'],['ielts'],['majors','n_majors']]:
        k=sum(1 for p in progs if has(p,ks))
        row.append(f"{k}/{n} ({round(k*100/n)}%)")
    print(" | ".join(x.ljust(14) for x in row))

# KB vs CDB per-field diff for BA scholarship & MA tuition & ielts
KBs=kb['schools']; KBm=kb['master']['schools']; KBj=kb['junior']['schools']
def kbhas(v,ks): return has(v,ks)
SCkb=['scholarships','scholarships_categorized','scholarship','scholarship_curated']
loss_ba_sc=[k for k,v in KBs.items() if kbhas(v,SCkb) and not nz(S.get(k,{}).get('programs',{}).get('BA',{}).get('scholarship'))]
print("\n[LOSS] BA: KB has scholarship but CDB empty:", len(loss_ba_sc))
print("  sample:", loss_ba_sc[:20])
loss_ma_tu=[k for k,v in KBm.items() if kbhas(v,['tuition','tuition_min','tuition_semester']) and not nz(S.get(k,{}).get('programs',{}).get('MA',{}).get('tuition'))]
print("[LOSS] MA: KB has tuition but CDB empty:", len(loss_ma_tu), loss_ma_tu[:15])
loss_ma_sc=[k for k,v in KBm.items() if kbhas(v,SCkb) and not nz(S.get(k,{}).get('programs',{}).get('MA',{}).get('scholarship'))]
print("[LOSS] MA scholarship:", len(loss_ma_sc), loss_ma_sc[:15])
loss_j_sc=[k for k,v in KBj.items() if kbhas(v,SCkb) and not nz(S.get(k,{}).get('programs',{}).get('전문학사',{}).get('scholarship'))]
print("[LOSS] 전문학사 scholarship:", len(loss_j_sc), loss_j_sc[:15])
# ielts
loss_ba_ie=[k for k,v in KBs.items() if nz(v.get('ielts_req')) and not nz(S.get(k,{}).get('programs',{}).get('BA',{}).get('ielts'))]
print("[LOSS] BA ielts:", len(loss_ba_ie))
# school set diff
print("\nKB union schools:", len(set(KBs)|set(KBm)|set(KBj)|set(kb['lang_programs']['schools'])), "CDB:", len(S))
print("in KB not in CDB:", len((set(KBs)|set(KBm)|set(KBj))-set(S)), list((set(KBs)|set(KBm)|set(KBj))-set(S))[:10])
print("lang names not in CDB:", len(set(kb['lang_programs']['schools'])-set(S)))
