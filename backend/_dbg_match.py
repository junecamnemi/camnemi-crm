import json, re
d = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
kb = json.load(open("verified_kb.json", encoding="utf-8"))
ba = kb.get("schools", {})

def norm(s):
    s = re.sub(r"\[[^\]]+\]$", "", s)
    s = re.sub(r"\([^)]*\)$", "", s)
    return s.replace(" ", "")

# adiga 기본 URL과 매칭
adiga = {}
for cd, v in d.items():
    adiga[norm(v["name"])] = v

# verified_kb BA(재적 보유)와 대조
match = mismatch = noadiga = 0
mis_list = []
for name, v in ba.items():
    if not v.get("student_count"):
        continue
    n = norm(name)
    av = adiga.get(n)
    if not av:
        noadiga += 1
        continue
    a_enr = av["stats"]["enrolled_2025"]
    if a_enr is None:
        mismatch += 1
        mis_list.append(f"{name}: adiga 없음(kb {v['student_count']})")
    elif abs(a_enr - v["student_count"]) / max(v["student_count"], 1) < 0.05:
        match += 1
    else:
        mismatch += 1
        mis_list.append(f"{name}: kb {v['student_count']} vs adiga {a_enr}")

print(f"BA 재적 대조: 일치 {match} / 불일치+adiga_미확보 {mismatch} / adiga에 매칭실패 {noadiga}")
print("\n불일치 상세:")
for m in mis_list[:30]:
    print("  ", m)