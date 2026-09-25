import json, os
os.chdir(r"C:\Users\wisew\camnemi-crm")
arr=json.load(open(r'backend\_djs_parsed.json',encoding='utf-8'))
kb=json.load(open(r'backend\verified_kb.json',encoding='utf-8'))
D={x['n']:x for x in arr}
for n in ['인하대학교','숙명여자대학교','광운대학교','고려대학교','성균관대학교']:
    x=D[n]
    print(n, 'data.js tuition=', json.dumps(x.get('tuition'), ensure_ascii=False)[:200])
    print('   KB BA tuition_semester=', kb['schools'].get(n,{}).get('tuition_semester'), '| KB MA tuition=', kb['master']['schools'].get(n,{}).get('tuition'), kb['master']['schools'].get(n,{}).get('tuition_min'))
print()
jr=[x for x in arr if x['type']=='junior'][:2]
for x in jr: print(x['n'], json.dumps(x.get('tuition'),ensure_ascii=False)[:150], '| req=',x.get('req'))
