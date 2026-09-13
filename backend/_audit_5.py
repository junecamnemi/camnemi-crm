import json, os
from collections import Counter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = json.load(open('consulting_db.json', encoding='utf-8'))
kb = json.load(open('verified_kb.json', encoding='utf-8'))
print("levels meta:", c['meta']['levels'])
S=c['schools']
lvlcount=Counter()
fields=Counter(); fperlvl={}
for sn,s in S.items():
    for lvl,p in s.get('programs',{}).items():
        lvlcount[lvl]+=1
        fperlvl.setdefault(lvl,Counter()).update(p.keys() if isinstance(p,dict) else [])
print("schools:", len(S))
print("programs per level:", dict(lvlcount))
for lvl,cc in fperlvl.items():
    print(f"\n[{lvl}] n={lvlcount[lvl]} fields:", cc.most_common(30))
# sample program
sn=list(S)[0]
print("\nSAMPLE:", json.dumps(S[sn], ensure_ascii=False)[:1200])

def nz(v):
    if v is None: return False
    if isinstance(v,(list,dict)): return len(v)>0
    if isinstance(v,str): return v.strip() not in ('','-','미정','없음','N/A')
    return True
def has(d,ks): return any(nz(d.get(k)) for k in ks)
TU=['tuition','tuition_semester','tuition_min','tuition_range','foreign_tuition']
SC=['scholarships','scholarships_categorized','scholarship','scholarship_curated']
PE=['period','foreign_period','period_note']
TO=['topik_req','foreign_topik']; IE=['ielts_req']
MA=['majors','majors_full','majors_sample','majors_ba','majors_ma','foreign_majors','n_majors']
print("\n=== 3. consulting_db coverage ===")
hdr=['level','n','tuition','scholarship','period','topik','ielts','majors']
print(" | ".join(h.ljust(14) for h in hdr))
for lvl in lvlcount:
    progs=[s['programs'][lvl] for s in S.values() if lvl in s.get('programs',{})]
    n=len(progs); row=[lvl,str(n)]
    for ks in [TU,SC,PE,TO,IE,MA]:
        k=sum(1 for p in progs if isinstance(p,dict) and has(p,ks))
        row.append(f"{k}/{n} ({k*100//n}%)")
    print(" | ".join(x.ljust(14) for x in row))
