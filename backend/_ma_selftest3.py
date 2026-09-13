import json, re

kb = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
ma = kb["master"]["schools"]
v = ma.get("조선대학교", {})
print("조선대 석사 키 목록:", list(v.keys()))
for f, val in v.items():
    s = json.dumps(val, ensure_ascii=False)
    if re.search(r"자체\s*(한국어)?\s*(시험|평가)|SU-TOPIK|자체시험", s):
        # locate the sentence
        m = re.search(r".{0,80}자체\s*(한국어)?\s*(시험|평가).{0,120}", s)
        print(f"  [{f}] ...{m.group(0) if m else val}...")
# is 조선대 in the BA selftest 101?
st = kb.get("selftest", {}).get("schools", {})
print("\n조선대 학부 selftest 포함:", "조선대학교" in st)
