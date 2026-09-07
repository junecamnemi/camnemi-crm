# -*- coding: utf-8 -*-
import os, re
D = r"C:/Users/USER/camnemi-crm/_curation_tmp/medcat_dentalvet"
def clean(f):
    return re.sub(r"[ \t]+"," ",open(os.path.join(D,f),encoding="utf-8").read().replace("\x00"," "))
t=clean("경상국립대학교_2026_수의예과.txt")
# find indices of key body headings
for kw in ["5. 제출서류","4. 모집 단위 및 인원","모집 단위 및 인원","3. 지원자격","전형 및 선발","2. 전형일정"]:
    print(kw,[m.start() for m in re.finditer(re.escape(kw),t)])
