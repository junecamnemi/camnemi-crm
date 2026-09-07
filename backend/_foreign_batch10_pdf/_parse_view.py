#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
h=open('_chsu_view_dom.html',encoding='utf-8',errors='replace').read()
for m in re.finditer(r'fileDownLoad\(this,(\d+),(\d+)\)',h):
    print("NTCE=",m.group(1),"ATCH=",m.group(2))
for m in re.finditer(r'pdfFileDownLoad\([^)]*\)',h):
    print("pdf:",m.group(0)[:200])
i=h.find('1장(한글).pdf')
print("file found at",i)
seg=h[max(0,i-2000):i+200]
for m in re.finditer(r'id="(?:atchSeq|ntceSntncNo)\^?\d*"[^>]*value="(\d+)"',seg):
    pass
# print onclick and inputs right before file name
m=re.findall(r'fileDownLoad\(this,(\d+),(\d+)\)[\s\S]{0,300}',h)
for a in m[:5]:
    print("call:",a[0],a[1])
