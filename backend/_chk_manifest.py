import csv, os
from collections import Counter

BASE = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
for y, rel in [("2027", "adiga_2027_외국인_모집요강/download_manifest.csv"),
               ("2026", "adiga_2026_외국인_모집요강/download_manifest.csv")]:
    path = os.path.join(BASE, rel)
    if not os.path.exists(path):
        print(y, "manifest 없음"); continue
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    dt = Counter(r.get("doc_type","") for r in rows)
    print(f"=== {y} manifest 총 {len(rows)}행 | doc_type 분포 ===")
    print("  ", dict(dt))
    fg = [r for r in rows if r.get("doc_type","")=="외국인" and r.get("saved_as")]
    print(f"  외국인 + saved_as 보유: {len(fg)}")
    if fg:
        print("  예:", fg[0].get("saved_as"), "| fileId", fg[0].get("fileId"))
    ok = [r for r in rows if r.get("doc_type","")=="외국인" and str(r.get("ok",""))=="True"]
    print(f"  외국인 ok(다운로드 성공): {len(ok)}")
    print()