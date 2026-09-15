#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert hwp5proc XML → clean text WITH tables (markdown-ish), for astra parsing."""
import re, os, xml.etree.ElementTree as ET

SRC = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\체류민원.xml"
OUT = r"C:\Users\USER\camnemi-crm\backend\hikorea_manuals\체류민원_md.txt"

# The hwp5proc XML uses a namespace-less structure with <Table>/<Row>/<Cell>/<Text>
# Names may have prefixes; strip them for simplicity.
def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

out = []
def walk(elem, depth=0):
    t = strip_ns(elem.tag)
    if t == "Table":
        out.append("\n[TABLE]")
    elif t == "Row":
        out.append("\n| ")
    elif t == "Cell":
        pass
    elif t == "Text" or t == "Char":
        if elem.text:
            out.append(elem.text)
    for c in elem:
        walk(c, depth+1)
    if t == "Cell":
        out.append(" | ")
    if t == "Row":
        pass
    if t == "Table":
        out.append("\n[/TABLE]\n")

print("XML 파싱 중 (45MB, 시간 소요)...")
tree = ET.parse(SRC)
root = tree.getroot()
walk(root)
txt = "".join(out)
txt = re.sub(r"[ \t]{2,}", " ", txt)
txt = re.sub(r"\n{3,}", "\n\n", txt)
open(OUT, "w", encoding="utf-8").write(txt)
print("변환 길이:", len(txt))
print("테이블 마커:", txt.count("[TABLE]"))
open(r"C:\Users\USER\AppData\Local\Temp\man_preview.txt","w",encoding="utf-8").write(txt[:3000])
print("\n=== 미리보기 ===")
print(txt[:1200])
