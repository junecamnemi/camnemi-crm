#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inspect the page-number links in collAjax response."""
import re

with open(r"C:\Users\USER\camnemi-crm\backend\_coll_raw_page1.txt", encoding="utf-8") as f:
    html = f.read()

# find all <a> tags containing just numbers (page links)
print("=== 숫자 링크 태그 ===")
for m in re.finditer(r"<a[^>]*>\s*(\d+)\s*</a>", html):
    full = html[max(0, m.start()-80):m.end()]
    print(re.sub(r"\s+", " ", full)[-140:])
    if m.start() > 5000:
        break

# Look at HTML around 'selectUniv' header/table - the page control is usually before/after
print("\n=== 'selectUniv' 첫 등장 주변 ===")
i = html.find('selectUniv')
print(re.sub(r"\s+", " ", html[max(0,i-200):i+100])[:300])
