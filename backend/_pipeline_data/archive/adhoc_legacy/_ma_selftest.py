import json, re

kb = json.load(open(r"C:\Users\wisew\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))

# 1) top-level selftest section
st = kb.get("selftest")
print("=== verified_kb['selftest'] 섹션 ===")
if isinstance(st, dict):
    print("  type: dict, keys:", list(st.keys())[:5])
    sc = st.get("schools") or st
    if isinstance(sc, dict):
        print(f"  schools 수: {len(sc)}")
        for k in list(sc)[:20]:
            print(f"    {k}: {json.dumps(sc[k], ensure_ascii=False)[:120]}")
elif isinstance(st, list):
    print(f"  list, {len(st)}개")
    for x in st[:20]:
        print("   ", json.dumps(x, ensure_ascii=False)[:120])

# 2) master entries mentioning 자체시험/자체 한국어 in any field
print("\n=== 석사(master) 텍스트에 '자체시험/자체 한국어' 언급 ===")
ma = kb["master"]["schools"]
hits = []
for k, v in ma.items():
    blob = json.dumps(v, ensure_ascii=False)
    if re.search(r"자체\s*(한국어)?\s*(시험|평가)|자체[가-힣]*시험|SU-TOPIK", blob):
        hits.append(k)
print(f"  언급 학교: {len(hits)}개")
for h in hits[:40]:
    print("   ", h)
