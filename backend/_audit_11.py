import json, os, re
os.chdir(r"C:\Users\wisew\camnemi-crm")
arr=json.load(open(r'backend\_djs_parsed.json',encoding='utf-8'))
kb=json.load(open(r'backend\verified_kb.json',encoding='utf-8'))
D={x['n']:x for x in arr}
def norm(s): return re.sub(r'\(.*?\)','',s).replace('대학교','').replace('대학','').replace('대','').replace(' ','')
NORM={norm(k):v for k,v in D.items()}
def get(n): return D.get(n) or NORM.get(norm(n))
n=len(arr)
def tu(x,lvl):
    t=x.get('tuition')
    return isinstance(t,dict) and isinstance(t.get(lvl),dict) and t[lvl].get('min') is not None
print("data.js tuition coverage: ba=%d ma=%d lang=%d (of %d)"%(
 sum(1 for x in arr if tu(x,'ba')), sum(1 for x in arr if tu(x,'ma')), sum(1 for x in arr if tu(x,'lang')), n))
# LANG gap recount with norm match
LG=kb['lang_programs']['schools']
g=[k for k,v in LG.items() if v.get('tuition_range') and not (get(k) and tu(get(k),'lang'))]
print("LANG tuition KB有&djs無 (norm-matched):", len(g), g[:15])
gp=[k for k,v in LG.items() if v.get('period') and not (get(k) and get(k).get('lang_period'))]
print("LANG period: data.js has lang_period field?", any('lang_period' in x for x in arr), "| KB lang period 보유:", sum(1 for v in LG.values() if v.get('period')))
# MA gaps norm-matched
MA=kb['master']['schools']
g_ma_tu=[k for k,v in MA.items() if (v.get('tuition') or v.get('tuition_min')) and not (get(k) and tu(get(k),'ma'))]
print("MA tuition KB有&djs無 (norm):", len(g_ma_tu), g_ma_tu[:15])
SC=['scholarships','scholarships_categorized','scholarship','scholarship_curated']
g_ma_sc=[k for k,v in MA.items() if any(v.get(s) for s in SC) and not (get(k) and get(k).get('scholarships'))]
print("MA scholarship KB有&djs無 (norm):", len(g_ma_sc), g_ma_sc[:15])
BA=kb['schools']
g_ba_tu=[k for k,v in BA.items() if (v.get('tuition_semester') or v.get('tuition_min')) and not (get(k) and tu(get(k),'ba'))]
print("BA tuition KB有&djs無 (norm):", len(g_ba_tu))
print("  그중 KB값이 숫자파싱 불가 문자열:", sum(1 for k in g_ba_tu if isinstance(BA[k].get('tuition_semester'),str) and not re.match(r'^₩[\d,]+', BA[k]['tuition_semester'].strip())))
print("  sample KB strings:", [(k, BA[k].get('tuition_semester')) for k in g_ba_tu[:8]])
g_ba_sc=[k for k,v in BA.items() if any(v.get(s) for s in SC) and not (get(k) and get(k).get('scholarships'))]
print("BA scholarship KB有&djs無 (norm):", len(g_ba_sc), g_ba_sc)
JR=kb['junior']['schools']
g_jr_sc=[k for k,v in JR.items() if v.get('scholarships_categorized') and not (get(k) and get(k).get('scholarships'))]
print("JR scholarship KB有&djs無:", len(g_jr_sc))
g_jr_pd=[k for k,v in JR.items() if v.get('period') and not (get(k) and get(k).get('period'))]
print("JR period KB有&djs無:", len(g_jr_pd))
