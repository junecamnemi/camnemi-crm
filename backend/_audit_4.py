import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
c = json.load(open('consulting_db.json', encoding='utf-8'))
print("top keys:", [(k, (len(v) if isinstance(v,(dict,list)) else v)) for k,v in c.items()][:20])
def walk(o, p='', depth=0):
    if depth>2: return
    if isinstance(o, dict):
        for k,v in list(o.items())[:4]:
            print('  '*depth, p+'/'+k, type(v).__name__, len(v) if isinstance(v,(dict,list)) else str(v)[:50])
            walk(v, p+'/'+k, depth+1)
walk(c)
