#!/usr/bin/env python3
"""parse_documents.py — DeepSeek parser for required application DOCUMENTS (제출서류).

Reads every collected guide PDF and extracts the required-document list per
university+track, including apostille/consular/translation requirements and any
country-specific differences. Writes documents_llm.jsonl.
"""
import os, sys, json, hashlib, zipfile, argparse, time, threading, queue, re, urllib.request
sys.path.insert(0, r'C:\Users\USER\pdf-venv\Lib\site-packages')
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "documents_llm.jsonl")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
AUTH = json.load(open(r"C:\Users\USER\AppData\Local\hermes\auth.json", encoding="utf-8"))
_N = AUTH["providers"]["nous"]
API = _N["inference_base_url"].rstrip("/")
KEY = _N.get("agent_key") or _N.get("access_token")
MODEL = "deepseek/deepseek-v4-pro"

PROMPT = """한국 대학 외국인 모집요강에서 **제출서류**를 추출해 JSON만 출력하세요(설명 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior",
 "documents":[{"name":"서류명(한글)","en":"English name","required":true,
   "note":"세부요건(아포스티유/영사확인/번역공증 등)","country_specific":"국가별 차이"}],
 "country_notes":"국가별 서류 차이 요약(없으면 "")"}
규칙:
- 입학원서·자기소개서 등 지원자가 작성하는 서류도 포함. 필수(required=true)/선택(false) 구분.
- 아포스티유·영사확인·번역공증·CHSI 등 인증 요건을 note에 명시.
- 서류 목록이 없으면 {"school":"...","documents":[]}

=== 모집요강 텍스트 ===
"""

def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def list_pdfs():
    out=[]; prog={'대학원':'ma','어학연수':'lang','외국인':'ba','전문대학':'junior'}
    for d in os.listdir(UP):
        p=os.path.join(UP,d)
        if not os.path.isdir(p) or '모집요강' not in d: continue
        pr=next((v for k,v in prog.items() if k in d),'ba')
        for f in os.listdir(p):
            if f.lower().endswith('.pdf'): out.append((os.path.join(p,f),pr))
    z=os.path.join(UP,'adiga_2026_외국인_모집요강.zip')
    if os.path.exists(z):
        with zipfile.ZipFile(z) as zf:
            for nm in zf.namelist():
                if nm.lower().endswith('.pdf'): out.append(((z,nm),'ba'))
    return out

def text_of(item):
    src,pr=item
    if isinstance(src,tuple):
        with zipfile.ZipFile(src[0]) as zf: doc=pymupdf.open(stream=zf.read(src[1]),filetype="pdf")
    else: doc=pymupdf.open(src)
    t="".join(doc[i].get_text() for i in range(min(len(doc),16)))
    doc.close(); return t

def call(text,retries=3):
    body={"model":MODEL,"messages":[{"role":"user","content":PROMPT+text[:15000]}],
          "max_tokens":4000,"temperature":0,"reasoning":{"effort":"none"}}
    last=None
    for a in range(retries):
        try:
            req=urllib.request.Request(API+"/chat/completions",data=json.dumps(body).encode(),
                headers={"Authorization":"Bearer "+KEY,"Content-Type":"application/json"})
            r=json.loads(urllib.request.urlopen(req,timeout=300).read())
            msg=r["choices"][0]["message"].get("content") or ""
            m=re.search(r'\{[\s\S]*\}',msg)
            if not m: body["max_tokens"]=16000; raise ValueError("no json")
            d=json.loads(m.group(0)); d["_usage"]=r.get("usage",{}); return d
        except Exception as e: last=e; time.sleep(3+5*a)
    raise last

_lock=threading.Lock()
def done_set():
    s=set()
    if os.path.exists(OUT):
        for l in open(OUT,encoding='utf-8'):
            try: s.add(json.loads(l)["_id"])
            except: pass
    return s

def worker(q,done,c):
    while True:
        try: item=q.get_nowait()
        except queue.Empty: return
        src,pr=item
        path=src[1] if isinstance(src,tuple) else src
        raw=src[0] if isinstance(src,tuple) else src
        fid=md5(raw)[:10]+"_"+os.path.basename(path)[:40]
        if fid in done:
            with _lock: c['skip']+=1
            q.task_done(); continue
        try:
            t=text_of(item)
            if len(t)<100:
                with _lock: c['skip']+=1
                continue
            d=call(t); d["_id"]=fid; d["_file"]=os.path.basename(path); d["_prog"]=pr
            with _lock:
                open(OUT,'a',encoding='utf-8').write(json.dumps(d,ensure_ascii=False)+"\n")
                c['ok']+=1
                if c['ok']%10==0: print(f"  parsed {c['ok']}",flush=True)
        except Exception as e:
            with _lock: c['err']+=1; print(f"  ERR {os.path.basename(path)[:36]}: {str(e)[:60]}",flush=True)
        finally: q.task_done()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--limit',type=int,default=0)
    a=ap.parse_args()
    items=list_pdfs()
    if a.limit: items=items[:a.limit]
    done=done_set()
    print(f"PDFs {len(items)} | done {len(done)}")
    q=queue.Queue()
    for it in items: q.put(it)
    c={'ok':0,'skip':0,'err':0}
    th=[threading.Thread(target=worker,args=(q,done,c),daemon=True) for _ in range(a.workers)]
    t0=time.time()
    for t in th: t.start()
    for t in th: t.join()
    print(f"DONE ok={c['ok']} skip={c['skip']} err={c['err']} in {time.time()-t0:.0f}s")

if __name__=='__main__': main()
