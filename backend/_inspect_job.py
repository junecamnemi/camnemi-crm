import json
B = r"C:\Users\USER\camnemi-crm\backend"
d = json.load(open(B + r"\job_manual_kr.json", encoding="utf-8"))

tp = d["time_parttime"]
print("### 시간제취업")
print("기본원칙:", tp["basic_principle"])
print("대상:", tp["target"])
print("\n허용시간 행:")
for r in tp["allowed_hours"]:
    print("  ", json.dumps(r, ensure_ascii=False))
print("\nD-2 시작:", tp["start_by_status"].get("D-2"))
print("D-4 시작:", tp["start_by_status"].get("D-4"))
print("\n기간·장소 D-2:", tp["period_place"].get("D-2"))
print("기간·장소 D-4:", tp["period_place"].get("D-4"))
print("\n제한분야:", tp["restricted_fields"])
print("\n예외:", tp["exceptions"])
print("\n필요서류:", tp["required_docs"])
print("\n위반페널티:", tp["violation_penalty"])
