# -*- coding: utf-8 -*-
"""Split remaining 48 MA schools: prioritize major universities. Create small batches (3 each)
for the priority group (retry foreigner-only grad guide collection)."""
import json, os

remaining = [
 "경북대학교","단국대학교","영남대학교","한남대학교","한동대학교","한림대학교","홍익대학교",
 "강남대학교","덕성여자대학교","동의대학교","배재대학교","한서대학교","동신대학교","영산대학교",
 "나사렛대학교","신한대학교","우석대학교","안양대학교","목원대학교","백석대학교","김천대학교",
 "대진대학교","신경주대학교","위덕대학교","용인대학교","예원예술대학교","송원대학교","세한대학교",
 "경성대학교","한신대학교","서원대학교","호서대학교","경동대학교","경운대학교","가톨릭관동대학교",
 "성공회대학교","아신대학교","강서대학교","호원대학교","고신대학교","광신대학교","국립한국교통대학교",
 "국립한밭대학교","금강대학교","대신대학교","목포가톨릭대학교","영산선학대학교","예수대학교"
]

# batches of 3
B=3
for i in range(0, len(remaining), B):
    b = remaining[i:i+B]
    json.dump(b, open(rf"C:\Users\USER\camnemi-crm\backend\_ma_retry_batch{i//B}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(remaining)}개 → {len(range(0,len(remaining),B))} 배치 (각 {B}개)")
for i in range(0, len(remaining), B):
    print(f"  batch{i//B}: {', '.join(remaining[i:i+B])}")
