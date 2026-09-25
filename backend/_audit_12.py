import json, os, re
os.chdir(r"C:\Users\wisew\camnemi-crm")
arr=json.load(open(r'backend\_djs_parsed.json',encoding='utf-8'))
def tu(x,l):
    t=x.get('tuition'); return isinstance(t,dict) and isinstance(t.get(l),dict) and t[l].get('min') is not None
u=[x for x in arr if x['type']=='univ']; j=[x for x in arr if x['type']=='junior']
print("univ(190): ba_tuition=%d ma_tuition=%d lang_tuition=%d sch=%d period=%d topik=%d ielts=%d"%(
 sum(tu(x,'ba') for x in u),sum(tu(x,'ma') for x in u),sum(tu(x,'lang') for x in u),
 sum(1 for x in u if x.get('scholarships')),sum(1 for x in u if x.get('period')),
 sum(1 for x in u if x.get('t') is not None),sum(1 for x in u if x.get('i') is not None)))
print("junior(126): ba_tuition=%d lang_tuition=%d sch=%d period=%d topik(req)=%d"%(
 sum(tu(x,'ba') for x in j),sum(tu(x,'lang') for x in j),
 sum(1 for x in j if x.get('scholarships')),sum(1 for x in j if x.get('period')),
 sum(1 for x in j if (x.get('req') or {}).get('topik') is not None)))
