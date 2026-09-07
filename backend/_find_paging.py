#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find pagination mechanism in collAjax response."""
import re

with open(r"C:\Users\USER\camnemi-crm\backend\_coll_raw_page1.txt", encoding="utf-8") as f:
    html = f.read()

# Page numbers 1-9 found as <a>1</a>... find their link/href context
for m in re.finditer(r"<a[^>]*>\s*(\d+)\s*</a>", html):
    tag = m.group(0)
    ctx = html[max(0, m.start()-150):m.end()+50]
    if "page" in ctx.lower():
        print("PAGE-TAG CTX:", re.sub(r"\s+", " ", ctx)[:200])
        break

# find any 'javascript:' or 'fn(' links near page numbers
for m in re.finditer(r'href="(javascript:[^"]*)"', html):
    print("JS HREF:", m.group(1)[:120])
    if m.start() > html.find('pagination'):
        break

# find the pagination HTML block
idx = html.find('pagination')
if idx > 0:
    # find a block like <ul class="pagination">
    pidx = html.rfind('<ul', 0, idx)
    print("\nPAGINATION UL:", html[pidx:pidx+800].replace("\n"," ")[:800])
