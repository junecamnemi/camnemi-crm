#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure dictionary coverage: token hit-rate across all sources + gap analysis."""
import json, os, re, csv, sys, collections
K=r"C:\Users\wisew\khmer"; T=r"C:\Users\wisew\camnemi-topik"; N=r"C:\Users\wisew\khmer_news"; B=r"C:\Users\wisew\camnemi-crm\backend"

def load_all():
    ko_en={}; 
    p=os.path.join(T,"data","vocab-dict.js")
    if os.path.exists(p):
        t=open(p,encoding="utf-8").read()
        for m in re.finditer(r'\{[^{}]*?"k"\s*:\s*"([^"]+)"[^{}]*?"e"\s*:\s*"([^"]*)"', t):
            k,e=m.group(1).strip(),m.group(2).strip()
            if k and e and len(k)<30: ko_en.setdefault(k,e)
    ko_km={}
    p=os.path.join(K,"km_ko_dict.jsonl")
    for line in open(p,encoding="utf-8"):
        try:
            o=json.loads(line)
            if o.get("ko") and o.get("km"): ko_km[o["ko"].strip()]=o["km"].strip()
        except Exception: pass
    en_km={}
    p=os.path.join(K,"dictionary.csv"); csv.field_size_limit(10**9)
    with open(p,encoding="utf-8",errors="ignore") as f:
        for row in csv.DictReader(f):
            w,km=(row.get("word") or "").strip(),(row.get("word_km") or "").strip()
            if w and km: en_km.setdefault(w,km); en_km.setdefault(w.lower(),km)
    pairs=[]
    pd=os.path.join(N,"pairs")
    if os.path.isdir(pd):
        for f in os.listdir(pd):
            if f.endswith(".json"):
                for x in json.load(open(os.path.join(pd,f),encoding="utf-8")):
                    if x.get("en") and x.get("km"): pairs.append((x["en"],x["km"]))
    return ko_en, ko_km, en_km, pairs

def ko_stems(w):
    """crude Korean stem variants for coverage boost."""
    v={w}
    for suf in ["하다","되다","이다","습니다","ㅂ니다","았다","었다","겠다","니다","세요","십니다","합니다","했다","한다","한","하는","된","되는","ㅁ","기"]:
        if w.endswith(suf) and len(w)>len(suf): v.add(w[:-len(suf)]+"다")
    return v

if __name__=="__main__":
    ko_en, ko_km, en_km, pairs = load_all()
    print("■ 사전 크기")
    print("  KO-EN:", len(ko_en), "| KO-KM:", len(ko_km), "| EN-KM:", len(en_km), "| 병렬쌍:", len(pairs))

    # coverage test on KO corpus (use km_ko_dict ko + vocab ex) and EN corpus (kiripost en)
    ko_tokens = collections.Counter()
    for k in list(ko_en)+list(ko_km):
        for t in re.findall(r"[가-힣]{2,}", k): ko_tokens[t]+=1
    en_tokens = collections.Counter()
    for en,km in pairs:
        for t in re.findall(r"[A-Za-z]{3,}", en.lower()): en_tokens[t]+=1
    print(f"\n■ 테스트 토큰: KO {len(ko_tokens)}종 / EN {len(en_tokens)}종")

    ko_hit = sum(1 for t in ko_tokens if t in ko_km or t in ko_en or any(s in ko_km or s in ko_en for s in ko_stems(t)))
    en_hit = sum(1 for t in en_tokens if t in en_km)
    print(f"  KO 토큰 히트: {ko_hit}/{len(ko_tokens)} = {ko_hit*100//max(1,len(ko_tokens))}%")
    print(f"  EN 토큰 히트: {en_hit}/{len(en_tokens)} = {en_hit*100//max(1,len(en_tokens))}%")

    # KO→KM 직결 커버리지
    ko_km_direct = sum(1 for t in ko_tokens if t in ko_km)
    print(f"\n  KO→KM 직결: {ko_km_direct}/{len(ko_tokens)} = {ko_km_direct*100//max(1,len(ko_tokens))}%")
    print(f"  KO→EN 경유: {sum(1 for t in ko_tokens if t in ko_en)}")
    # missing samples
    miss=[t for t in ko_tokens if t not in ko_km and t not in ko_en][:12]
    print(f"\n  KO 미커버 샘플: {miss}")
    miss_en=[t for t in en_tokens if t not in en_km][:12]
    print(f"  EN 미커버 샘플: {miss_en}")
    json.dump({"ko_en":len(ko_en),"ko_km":len(ko_km),"en_km":len(en_km),"pairs":len(pairs),
               "ko_hit":ko_hit,"ko_total":len(ko_tokens),"en_hit":en_hit,"en_total":len(en_tokens)},
              open(os.path.join(B,"coverage_baseline.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
