import json, os, re
os.chdir(r"C:\Users\wisew\camnemi-crm")
txt=open('data.js',encoding='utf-8').read()
i=txt.find('[')
# bracket match
depth=0
for j in range(i,len(txt)):
    ch=txt[j]
    if ch=='[': depth+=1
    elif ch==']':
        depth-=1
        if depth==0: break
arr=json.loads(txt[i:j+1])
print("data.js UNIV_KNOWLEDGE entries:", len(arr))
from collections import Counter
print("type:", Counter(x.get('type') for x in arr))
keys=Counter()
for x in arr: keys.update(x.keys())
print("keys:", keys.most_common(60))
def nz(v):
    if v is None: return False
    if isinstance(v,(list,dict)): return len(v)>0
    if isinstance(v,str): return v.strip() not in ('','-')
    return True
n=len(arr)
def cov(fn,label):
    c=sum(1 for x in arr if fn(x))
    print(f"{label}: {c}/{n} ({round(c*100/n)}%)")
    return c
cov(lambda x: nz(x.get('scholarships')) or nz(x.get('sch')) or nz(x.get('scholarship')), 'scholarships(any)')
cov(lambda x: nz(x.get('period')) or nz(x.get('p')) or nz(x.get('apply')), 'period(any)')
def tuit(x):
    t=x.get('tuition')
    if not isinstance(t,dict): return nz(t)
    return any(isinstance(v,dict) and (v.get('min') or v.get('max')) for v in t.values())
cov(tuit,'tuition(ba|ma min/max)')
cov(lambda x: isinstance(x.get('tuition'),dict) and (x['tuition'].get('ba') or {}).get('min') is not None,'tuition.ba.min')
cov(lambda x: isinstance(x.get('tuition'),dict) and (x['tuition'].get('ma') or {}).get('min') is not None,'tuition.ma.min')
cov(lambda x: nz(x.get('t')),'t(topik)')
cov(lambda x: nz(x.get('i')),'i(ielts)')
cov(lambda x: nz(x.get('majors_ba')),'majors_ba')
json.dump([x.get('n') for x in arr], open(r'backend\_djs_names.json','w',encoding='utf-8'), ensure_ascii=False)
# save parsed for next step
json.dump(arr, open(r'backend\_djs_parsed.json','w',encoding='utf-8'), ensure_ascii=False)
print("\nSAMPLE full keys of one seoul univ:")
for x in arr:
    if x.get('n')=='중앙대학교':
        print(json.dumps({k:(v if not isinstance(v,(list,dict)) else (str(v)[:200])) for k,v in x.items()}, ensure_ascii=False, indent=1))
        break
