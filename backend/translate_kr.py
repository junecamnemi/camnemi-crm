#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dictionary-mapping trilingual translator (KO/EN/KM) using deepseek-v4-pro.

Pipeline: build lookup index from dictionaries, retrieve candidate mappings for the
input tokens, then let deepseek-v4-pro perform the mapping/disambiguation.

Usage:
  python translate_kr.py --to km "안녕하세요, 만나서 반갑습니다"
  python translate_kr.py --to en "감사합니다"
  python translate_kr.py --to km --from en "The school is closed today."
"""
import json, os, re, csv, sys, argparse, urllib.request

K = r"C:\Users\wisew\khmer"; T = r"C:\Users\wisew\camnemi-topik"; B = r"C:\Users\wisew\camnemi-crm\backend"

def _auth():
    for p in [r"C:\Users\wisew\AppData\Local\hermes\shared\nous_auth.json", r"C:\Users\wisew\AppData\Local\hermes\auth.json"]:
        if not os.path.exists(p): continue
        d = json.load(open(p, encoding="utf-8"))
        if d.get("access_token"): return d.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", d["access_token"]
        n = (d.get("providers") or {}).get("nous") or {}
        if n.get("agent_key"): return n.get("inference_base_url") or "https://inference-api.nousresearch.com/v1", n["agent_key"]
    raise SystemExit("no auth")
BASE, KEY = _auth(); MODEL = "deepseek/deepseek-v4-pro"

_CACHE = {}
def load_dicts():
    if _CACHE: return _CACHE
    ko_en = {}
    p = os.path.join(T,"data","vocab-dict.js")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        for m in re.finditer(r'\{[^{}]*?"k"\s*:\s*"([^"]+)"[^{}]*?"e"\s*:\s*"([^"]*)"', t):
            k,e = m.group(1).strip(), m.group(2).strip()
            if k and e and len(k)<30: ko_en.setdefault(k, e)
    ko_km = {}
    p = os.path.join(K,"km_ko_dict.jsonl")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                o=json.loads(line)
                if o.get("ko") and o.get("km"): ko_km[o["ko"].strip()]=o["km"].strip()
            except Exception: pass
    en_km = {}
    p = os.path.join(K,"dictionary.csv"); csv.field_size_limit(10**9)
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                w,km = (row.get("word") or "").strip(), (row.get("word_km") or "").strip()
                if w and km:
                    en_km[w]=km
                    en_km.setdefault(w.lower(), km)
    _CACHE.update({"ko_en":ko_en, "ko_km":ko_km, "en_km":en_km})
    return _CACHE

def lookup_all(text):
    d = load_dicts()
    toks = re.findall(r"[가-힣]{2,}|[A-Za-z]{2,}", text)
    hits=[]
    for t in set(toks):
        if t in d["ko_km"]: hits.append(f"{t} → [KM] {d['ko_km'][t]}")
        if t in d["ko_en"]: hits.append(f"{t} → [EN] {d['ko_en'][t]}")
        if t in d["en_km"]: hits.append(f"{t} → [KM] {d['en_km'][t]}")
        elif t.lower() in d["en_km"]: hits.append(f"{t} → [KM] {d['en_km'][t.lower()]}")
    return hits[:60]

PROMPT = """너는 한국어·영어·크메르어 번역기다. [사전 후보]를 참고하되 문맥에 맞게 자연스럽게 번역하라.
사전에 없는 단어는 문맥으로 처리. 크메르어는 반드시 크메르 문자(ភាសាខ្មែរ)로 출력.
출력 형식: JSON만
{"translation":"번역문","target":"<KM|EN>","notes":"간단 설명(선택)","used_dict":[{"term":"","translation":""}]}

[사전 후보]
<<HITS>>

[번역 방향] <<SRC>> → <<TGT>>
[원문] <<TEXT>>
"""
def translate(text, to="km", frm="ko"):
    hits = lookup_all(text)
    prompt = PROMPT.replace("<<HITS>>", "\n".join(hits) if hits else "(없음)").replace("<<SRC>>", frm.upper()).replace("<<TGT>>", to.upper()).replace("<<TEXT>>", text)
    body={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":24000}
    req=urllib.request.Request(BASE.rstrip("/")+"/chat/completions",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read())
    m=d["choices"][0]["message"]; c=(m.get("content") or "")+"\n"+(m.get("reasoning") or "")
    depth=0; start=None
    for i,ch in enumerate(c):
        if ch=="{":
            if depth==0: start=i
            depth+=1
        elif ch=="}":
            depth-=1
            if depth==0 and start is not None:
                try:
                    o=json.loads(c[start:i+1])
                    if o.get("translation"): return o, hits
                except Exception: pass
                start=None
    return {"translation":"(실패)","raw":c[:300]}, hits

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("--to",default="km"); ap.add_argument("--from",dest="frm",default="ko")
    a=ap.parse_args()
    d=load_dicts()
    print(f"[사전] KO-EN {len(d['ko_en'])} / KO-KM {len(d['ko_km'])} / EN-KM {len(d['en_km'])}")
    o,hits = translate(a.text, a.to, a.frm)
    print(f"\n[번역] {a.frm.upper()} → {a.to.upper()}")
    print("  원문:", a.text)
    print("  결과:", o.get("translation"))
    if o.get("notes"): print("  설명:", o["notes"])
    if o.get("used_dict"): print("  사용사전:", json.dumps(o["used_dict"], ensure_ascii=False)[:300])
    print(f"  (사전후보 {len(hits)}개)")
