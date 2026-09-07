# -*- coding: utf-8 -*-
"""Sync foreigner-guide status from verified_kb junior into data.js junior entries
(so the live site reflects 폐교/통합/exclude + foreigner-guide availability)."""
import json, re

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
content = open(r"C:\Users\USER\camnemi-crm\data.js", encoding="utf-8").read()
s = content.find("[")
d = 0
end = None
for i in range(s, len(content)):
    if content[i] == "[": d += 1
    elif content[i] == "]":
        d -= 1
        if d == 0: end = i+1; break
data = json.loads(content[s:end])

# build lookup: junior name -> data.js entry (match on name field variants)
def norm(x): return x.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
by_norm = {}
for u in data:
    if u.get("type")=="junior":
        for k in [u.get("n"), u.get("name"), u.get("name_ko"), u.get("school")]:
            if k: by_norm.setdefault(norm(k), u)

changed=0
for school, entry in js.items():
    sn = norm(school)
    u = by_norm.get(sn)
    if not u: continue
    fg = entry.get("foreign_guide")
    excl = entry.get("exclude_reason")
    # set/clear fields
    old_reason = u.get("exclude_reason")
    u["foreign_guide"] = fg
    if excl:
        u["excluded"] = True
        u["exclude_reason"] = excl
    else:
        u.pop("excluded", None)
        u.pop("exclude_reason", None)
    if u.get("foreign_guide") != fg or old_reason != excl:
        changed+=1

# serialize back preserving original structure
new_content = content[:s] + json.dumps(data, ensure_ascii=False) + content[end:]
# data.js is `var universities = [...];` style — ensure no newline break
open(r"C:\Users\USER\camnemi-crm\data.js","w",encoding="utf-8").write(new_content)
print(f"data.js junior 동기화: {changed}개 변경됨 (폐교·통합·외국인요강 상태)")
# verify
c2=open(r"C:\Users\USER\camnemi-crm\data.js",encoding="utf-8").read()
s2=c2.find('[');d=0
for i in range(s2,len(c2)):
    if c2[i]=='[':d+=1
    elif c2[i]==']':
        d-=1
        if d==0: data2=json.loads(c2[s2:i+1]);break
print("다시 파싱 OK, 총 엔트리:", len(data2))
