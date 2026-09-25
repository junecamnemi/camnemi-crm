#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trilingual (KO-EN-KM) dictionary-mapping translator using deepseek-v4-pro.

Data:
  KO-EN  : camnemi-topik/data/vocab-dict.js  (Camnemi TOPIK dict)
  EN-KM  : khmer/dictionary.csv              (175,805)
  KO-KM  : khmer/km_ko_dict.jsonl            (KO-KM-EN triples)
  pairs  : khmer_news/pairs/*.json           (kiripost EN-KM parallel)
"""
import json, os, re, csv, sys, itertools, urllib.request

K = r"C:\Users\wisew\khmer"; T = r"C:\Users\wisew\camnemi-topik"; N = r"C:\Users\wisew\khmer_news"
OUT = r"C:\Users\wisew\camnemi-crm\backend"

def load_ko_en():
    """vocab-dict.js -> {korean: english}"""
    d={}
    p=os.path.join(T,"data","vocab-dict.js")
    if not os.path.exists(p): return d
    t=open(p,encoding="utf-8").read()
    for m in re.finditer(r'\{[^{}]*?"k"\s*:\s*"([^"]+)"[^{}]*?"e"\s*:\s*"([^"]*)"', t):
        k,e = m.group(1).strip(), m.group(2).strip()
        if k and e: d.setdefault(k, e)
    return d

def load_en_km(limit=None):
    """dictionary.csv -> {english: khmer}"""
    d={}
    p=os.path.join(K,"dictionary.csv"); csv.field_size_limit(10**9)
    with open(p,encoding="utf-8",errors="ignore") as f:
        r=csv.DictReader(f)
        for i,row in enumerate(r):
            if limit and i>=limit: break
            w,km = (row.get("word") or "").strip(), (row.get("word_km") or "").strip()
            if w and km and w not in d: d[w]=km
    return d

def load_ko_km():
    """km_ko_dict.jsonl -> {korean: khmer}"""
    d={}
    p=os.path.join(K,"km_ko_dict.jsonl")
    if not os.path.exists(p): return d
    for line in open(p,encoding="utf-8"):
        try:
            o=json.loads(line)
            if o.get("ko") and o.get("km"): d[o["ko"].strip()]=o["km"].strip()
        except Exception: pass
    return d

def load_pairs():
    """kiripost pairs -> [(en,km)]"""
    out=[]
    pd=os.path.join(N,"pairs")
    if os.path.isdir(pd):
        for f in os.listdir(pd):
            if f.endswith(".json"):
                for x in json.load(open(os.path.join(pd,f),encoding="utf-8")):
                    if x.get("en") and x.get("km"): out.append((x["en"],x["km"]))
    return out

if __name__=="__main__":
    ke=load_ko_en(); ek=load_en_km(); kk=load_ko_km(); pr=load_pairs()
    print("■ 사전 로드")
    print("  KO-EN (Camnemi TOPIK):", len(ke))
    print("  EN-KM (dictionary.csv):", len(ek))
    print("  KO-KM (km_ko_dict):", len(kk))
    print("  EN-KM 병렬쌍 (kiripost):", len(pr))
    # save unified
    uni={"ko_en":ke, "ko_km":kk, "_meta":{"en_km_count":len(ek),"pairs":len(pr)}}
    json.dump(uni, open(os.path.join(OUT,"trilingual_dict_index.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n예시:")
    for k in list(ke)[:5]: print(f"   KO-EN: {k} → {ke[k]}")
    for k in list(kk)[:5]: print(f"   KO-KM: {k} → {kk[k]}")
    for w in ["hello","water","teacher"]: print(f"   EN-KM: {w} → {ek.get(w,'?')}")
