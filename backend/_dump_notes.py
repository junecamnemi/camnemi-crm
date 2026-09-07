#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump full master-guide entries for all IELTS5.5+DS candidates with raw notes, for manual review."""
import re
import json

DATA_FILE = r"C:\Users\USER\camnemi-crm\data.js"
MASTER = r"C:\Users\USER\camnemi-crm\backend\_guide_2027_master.json"
ADIGA = r"C:\Users\USER\camnemi-crm\backend\adiga2027_upload_map.json"

def load_datajs():
    with open(DATA_FILE, encoding="utf-8") as f:
        content = f.read()
    start = content.find("[")
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                return json.loads(content[start:i + 1])
    return []

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

univs = load_datajs()
master = load_json(MASTER)
adiga = load_json(ADIGA)

adiga_by_school = {}
for path, info in adiga.items():
    nm = info.get("name", "")
    if "외국인" in nm:
        m = re.match(r"^\d+_(.+?)_20\d+_외국인\.pdf$", nm)
        if m:
            adiga_by_school[m.group(1)] = info.get("viewLink")

master_by_school = {}
for item in master:
    master_by_school[item.get("school", "")] = item

DS_KW = ["data", "데이터", "빅데이터", "ai", "인공지능", "intelligence", "소프트웨어", "software",
         "컴퓨터", "computer", "통계", "statistics", "정보통신", "정보보호", "사이버", "ict",
         "산업공학", "industrial", "지능정보"]

def has_ds_major(u):
    texts = []
    for mm in (u.get("majors_ba") or []):
        texts.append(f"{mm.get('kr','')} {mm.get('en','')}".lower())
    if not texts:
        texts = [str(x).lower() for x in (u.get("majors") or [])]
    combined = " ".join(texts)
    return any(kw.lower() in combined for kw in DS_KW)

cands = []
for u in univs:
    req = u.get("req") or {}
    u_ielts = req.get("ielts")
    if u_ielts is not None:
        try:
            if float(u_ielts) > 5.5:
                continue
        except ValueError:
            pass
    if not has_ds_major(u):
        continue
    cands.append(u.get("n"))

print(f"후보 {len(cands)}개 학교의 마스터 원문 정보:\n")
for nm in sorted(cands):
    mi = master_by_school.get(nm)
    if not mi:
        print(f"### {nm}: (마스터 데이터 없음)")
        print()
        continue
    ad = adiga_by_school.get(nm)
    print(f"### {nm}")
    print(f"  ba_status: {mi.get('ba_status')}")
    print(f"  ba_title: {mi.get('ba_title')}")
    print(f"  ba_url: {mi.get('ba_url')}")
    print(f"  adiga_foreigner_link: {ad or '(없음)'}")
    print(f"  ba_note: {mi.get('ba_note') or '(없음)'}")
    print()
