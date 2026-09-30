import json
BS = chr(92)
c = open(r"C:\Users\wisew\camnemi-crm\data.js", encoding="utf-8").read()
s = c.find("["); d=0
for i in range(s, len(c)):
    if c[i]=="[": d+=1
    elif c[i]=="]":
        d-=1
        if d==0: data=json.loads(c[s:i+1]); break
print("main array OK:", len(data))
marker = "window.UNIV_SPECIAL = "
i = c.find(marker)
seg = c[i+len(marker):]
d=0; in_str=False; esc=False
sp=None
for k,ch in enumerate(seg):
    if in_str:
        if esc: esc=False
        elif ch==BS: esc=True
        elif ch=='"': in_str=False
    else:
        if ch=='"': in_str=True
        elif ch=="{": d+=1
        elif ch=="}":
            d-=1
            if d==0:
                sp=json.loads(seg[:k+1]); break
print("UNIV_SPECIAL keys:", list(sp.keys()))
print("  visa degree:", len(sp["visa_restricted_2026"]["degree_restricted"]),
      "| lang:", len(sp["visa_restricted_2026"]["lang_restricted"]))
print("  free_major schools:", len(sp["free_major_programs"].get("schools",{})))
print("  ai_departments:", len(sp["ai_departments"].get("schools",{})))
print("  medical_reqs:", list(sp["medical_reqs"].keys()))
print("entries with visa_restricted flag:", sum(1 for u in data if u.get("visa_restricted")))
print("entries with lang_bypass:", sum(1 for u in data if u.get("lang_bypass")))
print("entries with scholarships:", sum(1 for u in data if u.get("scholarships")))
print("entries with period:", sum(1 for u in data if u.get("period")))
