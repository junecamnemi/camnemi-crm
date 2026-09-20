import json
d = json.load(open("unvcd_index.json", encoding="utf-8"))["schools"]
# 제외 목록 상세
from collections import Counter
by_type = Counter()
detail = {"신학대": [], "교육대": [], "재적<2000": [], "미확보": []}
for cd, v in d.items():
    e = v["excluded"]
    if e == "신학대":
        detail["신학대"].append(v["name"]); by_type[(v["school_type"], "신학대")] += 1
    elif e == "교육대":
        detail["교육대"].append(v["name"]); by_type[(v["school_type"], "교육대")] += 1
    elif e:
        detail["재적<2000"].append(f"{v['name']}({e})"); by_type[(v["school_type"], "재적")] += 1
    elif v["stats"]["enrolled_2025"] is None:
        detail["미확보"].append(f"{v['name']} [{v['school_type']}]")

print("제외 유형×구분:", dict(by_type))
print("\n[신학대] (예외 확인: 성결대·한국기술교육대 등):")
print("  ", detail["신학대"])
print("\n[교육대]:")
print("  ", detail["교육대"])
print("\n[재적<2000 수명]:", len(detail["재적<2000"]))
print("\n[통계 미확보]:")
print("  ", detail["미확보"])
print("\n등록 유지:", sum(1 for v in d.values() if not v["excluded"]))