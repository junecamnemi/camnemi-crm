import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
kb = json.load(open('verified_kb.json', encoding='utf-8'))

def sample(d, name, n=1):
    print(f"--- {name}: {len(d)} schools ---")
    for i,(k,v) in enumerate(d.items()):
        if i>=n: break
        print(k, json.dumps(v, ensure_ascii=False)[:1500])
    # field frequency
    from collections import Counter
    c = Counter()
    for v in d.values():
        if isinstance(v, dict): c.update(v.keys())
        elif isinstance(v, list):
            for it in v:
                if isinstance(it, dict): c.update(it.keys())
    print("FIELDS:", c.most_common(40))
    print()

sample(kb['schools'], 'schools(BA)')
sample(kb['master']['schools'], 'master.schools')
sample(kb['junior']['schools'], 'junior.schools')
sample(kb['lang_programs']['schools'], 'lang_programs.schools')
print("medical_reqs:", json.dumps(kb['medical_reqs'], ensure_ascii=False)[:400])
print("ai_departments schools:", len(kb['ai_departments']['schools']))
print("free_major schools:", len(kb['free_major_programs']['schools']))
vr = kb['visa_restricted_2026']
print("visa degree_restricted:", len(vr['degree_restricted']), "lang_restricted:", len(vr['lang_restricted']))
print("selftest schools:", len(kb['selftest']['schools']))
print("guide:", len(kb['guide']))
