# -*- coding: utf-8 -*-
"""Full list of Korean pharmacy colleges (from 대한약사회 kpanet.or.kr) for verification.
We already confirmed 5 (서울/연세/고려세종/인제 recruiting; 성균관 excluded).
Remaining ~32 need foreigner-admission verification."""
import json

# 대한약사회 공식 37개 약학대학
all_pharm = [
 "가천대학교","가톨릭대학교","건국대학교","경상국립대학교","경성대학교","경희대학교",
 "계명대학교","고려대학교(세종)","광주대학교","국립강릉원주대학교","국립부경대학교","국립순천대학교",
 "국립안동대학교","국립전남대학교","국립충남대학교","국립충북대학교","동국대학교","동덕여자대학교",
 "부산대학교","삼육대학교","서울대학교","성균관대학교","숙명여자대학교","아주대학교",
 "연세대학교","영남대학교","우석대학교","원광대학교","이화여자대학교","인제대학교",
 "인하대학교","전북대학교","조선대학교","중앙대학교","충북대학교","한양대학교",
 "동국대학교","국립한국교통대학교"
]
all_pharm = sorted(set(all_pharm))

# already verified (in KB recruiting)
already = {"고려대학교(세종)","서울대학교","성균관대학교","연세대학교","인제대학교"}
to_check = [s for s in all_pharm if s not in already]
print(f"전국 약대: {len(all_pharm)} | 이미 검증: {len(already)} | 검증 필요: {len(to_check)}")
print("검증 필요:", to_check)

# batches of 5 for parallel dispatch
B=5
for i in range(0, len(to_check), B):
    batch = to_check[i:i+B]
    json.dump(batch, open(rf"C:\Users\USER\camnemi-crm\backend\_pharm_batch{i//B}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  batch{i//B}: {', '.join(batch)}")
