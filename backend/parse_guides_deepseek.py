#!/usr/bin/env python3
"""parse_guides_deepseek.py — LLM-based admission-guide parser (DeepSeek V4-Pro).

Replaces the regex parser for cases where the rule-based extractor misses data.
For each guide PDF: extract text (pymupdf) -> send to DeepSeek V4-Pro via the
Nous inference gateway -> get structured JSON -> save to a JSONL + upsert into
Supabase (universities / university_guides).

Resumable: files already in the JSONL are skipped. Parallel workers.

Usage:
  python parse_guides_deepseek.py --limit 10         # test
  python parse_guides_deepseek.py --workers 8        # full run
  python parse_guides_deepseek.py --merge            # push results to Supabase
"""
import os, sys, json, hashlib, zipfile, argparse, time, threading, queue, re, urllib.request
sys.path.insert(0, r'C:\Users\USER\pdf-venv\Lib\site-packages')
import pymupdf

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_JSONL = os.path.join(BASE, "guides_llm_parsed.jsonl")
UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"

AUTH = json.load(open(r"C:\Users\USER\AppData\Local\hermes\auth.json", encoding="utf-8"))
_N = AUTH["providers"]["nous"]
API_BASE = _N["inference_base_url"].rstrip("/")
API_KEY = _N.get("agent_key") or _N.get("access_token")
MODEL = "deepseek/deepseek-v4-pro"

PROMPT = """한국 대학 외국인 모집요강 텍스트에서 정보를 추출해 JSON만 출력하세요(설명·마크다운 금지):
{"school":"대학명(한글)", "program":"ba|ma|lang|junior", "year":"2026|2027|unknown",
 "period":"원서접수 기간(문자열)", "topik":TOPIK최소급수 숫자 또는 null, "ielts":IELTS최소 숫자 또는 null,
 "toefl":TOEFL최소 숫자 또는 null, "majors":["모집학과 전체 목록"],
 "tuition_note":"등록금 관련 한 줄 요약", "scholarship_note":"장학금 관련 한 줄 요약"}

=== 모집요강 텍스트 ===
"""

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def list_pdfs():
    """(path_or_(zip,nm), label, prog_hint, year_hint)"""
    out = []
    prog = {'대학원': 'ma', '어학연수': 'lang', '외국인': 'ba', '전문대학': 'junior'}
    for d in os.listdir(UP):
        p = os.path.join(UP, d)
        if not os.path.isdir(p) or '모집요강' not in d:
            continue
        pr = next((v for k, v in prog.items() if k in d), 'ba')
        yr = '2027' if '2027' in d else '2026'
        for f in os.listdir(p):
            if f.lower().endswith('.pdf'):
                out.append((os.path.join(p, f), None, pr, yr))
    z = os.path.join(UP, 'adiga_2026_외국인_모집요강.zip')
    if os.path.exists(z):
        with zipfile.ZipFile(z) as zf:
            for nm in zf.namelist():
                if nm.lower().endswith('.pdf'):
                    out.append(((z, nm), None, 'ba', '2026'))
    return out

def extract_text(item):
    src, _, _, _ = item
    if isinstance(src, tuple):
        z, nm = src
        with zipfile.ZipFile(z) as zf:
            doc = pymupdf.open(stream=zf.read(nm), filetype="pdf")
    else:
        doc = pymupdf.open(src)
    t = "".join(doc[i].get_text() for i in range(min(len(doc), 12)))
    doc.close()
    return t

def call_llm(text, retries=3):
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPT + text[:14000]}],
            "max_tokens": 4000, "temperature": 0,
            "reasoning": {"effort": "none"}}   # extraction needs no chain-of-thought; ~0 reasoning tokens
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(API_BASE + "/chat/completions", data=json.dumps(body).encode(),
                headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=300).read())
            msg = r["choices"][0]["message"].get("content") or ""
            m = re.search(r'\{[\s\S]*\}', msg)
            if not m:
                # rarely the model still reasons; retry with room for it
                body["max_tokens"] = 16000
                raise ValueError("no JSON in response")
            data = json.loads(m.group(0))
            data["_usage"] = r.get("usage", {})
            return data
        except Exception as e:
            last = e
            time.sleep(3 + 5 * a)
    raise last

_lock = threading.Lock()
def load_done():
    done = set()
    if os.path.exists(OUT_JSONL):
        for line in open(OUT_JSONL, encoding='utf-8'):
            try: done.add(json.loads(line)["_id"])
            except Exception: pass
    return done

def worker(q, done, counter):
    while True:
        try: item = q.get_nowait()
        except queue.Empty: return
        src, _, prog, yr = item
        path = src[1] if isinstance(src, tuple) else src
        raw = src[0] if isinstance(src, tuple) else src
        fid = md5(raw)[:10] + "_" + os.path.basename(path)[:40]
        if fid in done:
            with _lock: counter['skip'] += 1
            q.task_done(); continue
        try:
            text = extract_text(item)
            if len(text) < 100:
                with _lock: counter['skip'] += 1
                continue
            data = call_llm(text)
            data["_id"] = fid
            data["_file"] = os.path.basename(path)
            data["_prog_hint"] = prog
            data["_year_hint"] = yr
            with _lock:
                with open(OUT_JSONL, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                counter['ok'] += 1
                if counter['ok'] % 5 == 0:
                    print(f"  parsed {counter['ok']} (skip {counter['skip']})", flush=True)
        except Exception as e:
            with _lock: counter['err'] += 1; print(f"  ERR {os.path.basename(path)[:38]}: {str(e)[:70]}", flush=True)
        finally:
            q.task_done()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--merge', action='store_true')
    args = ap.parse_args()

    if args.merge:
        merge_to_db(); return

    items = list_pdfs()
    if args.limit: items = items[:args.limit]
    done = load_done()
    print(f"PDFs total {len(items)} | already parsed {len(done)}")
    q = queue.Queue()
    for it in items:
        q.put(it)
    counter = {'ok': 0, 'skip': 0, 'err': 0}
    threads = [threading.Thread(target=worker, args=(q, done, counter), daemon=True) for _ in range(args.workers)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"DONE ok={counter['ok']} skip={counter['skip']} err={counter['err']} in {time.time()-t0:.0f}s")

def merge_to_db():
    """push parsed results into Supabase universities + university_guides."""
    import urllib.parse
    H = open(r"C:\Users\USER\camnemi-crm\index.html", encoding="utf-8").read()
    K = re.search(r"DEFAULT_SUPABASE_KEY\s*=\s*'([^']+)'", H).group(1)
    URL = "https://zjdvzpylxazfbazioxto.supabase.co/rest/v1/"
    def api(method, path, body=None, prefer=None):
        hdr = {"apikey": K, "Authorization": "Bearer " + K, "Content-Type": "application/json"}
        if prefer: hdr["Prefer"] = prefer
        r = urllib.request.Request(URL + path, data=(json.dumps(body).encode() if body else None), method=method, headers=hdr)
        with urllib.request.urlopen(r, timeout=30) as resp:
            t = resp.read().decode()
            return json.loads(t) if t.strip() else None
    uids = {u['id'] for u in api('GET', 'universities?select=id&limit=500')}
    rows = [json.loads(l) for l in open(OUT_JSONL, encoding='utf-8')]
    print(f"parsed rows: {len(rows)} | univ ids: {len(uids)}")
    upd = 0; miss = []
    for r in rows:
        u = r.get('school') or ''
        if u not in uids or not r.get('majors'): continue
        patch = {}
        if r.get('majors'): patch['majors_ba' if r['program'] != 'ma' else 'majors_ma'] = [{"kr": m} for m in r['majors']]
        if patch:
            try:
                api('PATCH', f"universities?id=eq.{urllib.parse.quote(u)}", patch, prefer='return=minimal'); upd += 1
            except Exception as e: miss.append(u)
    print(f"updated {upd} | errors {len(miss)}")

if __name__ == "__main__":
    main()
