import json, os, re
os.chdir(r"C:\Users\wisew\camnemi-crm")
kb=json.load(open(r'backend\verified_kb.json',encoding='utf-8'))
arr=json.load(open(r'backend\_djs_parsed.json',encoding='utf-8'))
D={x['n']:x for x in arr}
MA=kb['master']['schools']; LG=kb['lang_programs']['schools']; BA=kb['schools']
def norm(s): return re.sub(r'\(.*?\)','',s).replace('대학교','').replace('대학','').replace('대','').replace(' ','')
# duplicate-ish keys in MA
short=[k for k in MA if k not in D]
print("MA short-name keys and their long twin in MA?:")
for k in short:
    twins=[k2 for k2 in MA if k2!=k and norm(k2)==norm(k)]
    dj=[k2 for k2 in D if norm(k2)==norm(k)]
    print(f"  {k}: MA twin={twins} data.js match={dj}")
print()
lgshort=[k for k in LG if k not in D]
matched=sum(1 for k in lgshort if any(norm(k2)==norm(k) for k2 in D))
print(f"LANG keys not exact in data.js: {len(lgshort)}, of which normalized-match exists: {matched}")
print("LANG truly unknown to data.js:", [k for k in lgshort if not any(norm(k2)==norm(k) for k2 in D)][:20])
# BA short
print("\nBA keys not in data.js:", [k for k in BA if k not in D])
# lang_guide count vs LANG KB
lg_guide=sum(1 for x in arr if x.get('lang_guide'))
print("data.js lang_guide entries:", lg_guide, "| KB lang schools:", len(LG))
# junior in data.js: has scholarships key?
jr_djs=[x for x in arr if x.get('type')=='junior']
print("junior data.js entries:", len(jr_djs), "with scholarships:", sum(1 for x in jr_djs if x.get('scholarships')), "with period:", sum(1 for x in jr_djs if x.get('period')))
univ_djs=[x for x in arr if x.get('type')=='univ']
print("univ data.js entries:", len(univ_djs), "with scholarships:", sum(1 for x in univ_djs if x.get('scholarships')), "with period:", sum(1 for x in univ_djs if x.get('period')))
print("univ not in KB BA:", [x['n'] for x in univ_djs if x['n'] not in BA][:40], len([x for x in univ_djs if x['n'] not in BA]))
# data.js mtime vs kb mtime
import datetime
for f in ['backend/verified_kb.json','backend/consulting_db.json','data.js']:
    print(f, datetime.datetime.fromtimestamp(os.path.getmtime(f)))
