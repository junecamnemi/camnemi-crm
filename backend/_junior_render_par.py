# -*- coding: utf-8 -*-
"""Parallel headless-Chrome render of remaining junior guide_urls (6 concurrent).
No LLM -> no rate limit."""
import json, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\USER\AppData\Local"), "Temp")

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","").replace("_전문학사학위심화","").replace("_전문학사_입학안내(렌더)","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

targets=[(n,v["guide_url"]) for n,v in js.items() if v.get("guide_url") and norm(n) not in have]
print(f"렌더 대상: {len(targets)}")

def render_one(args):
    n, u, idx = args
    outpdf = os.path.join(SAVEDIR, f"{n}_전문학사_입학안내(렌더).pdf")
    if os.path.exists(outpdf): return (n,"exists",0)
    prof = os.path.join(TMP, f"jpar_{idx}")
    try:
        r = subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--no-first-run",
            "--disable-extensions","--timeout=22000","--virtual-time-budget=6000",
            f"--user-data-dir={prof}","--print-to-pdf="+outpdf, u],
            capture_output=True, timeout=40)
        if os.path.exists(outpdf):
            sz=os.path.getsize(outpdf)
            if open(outpdf,'rb').read(4)==b"%PDF" and sz>30000:
                return (n,"ok",sz)
            os.remove(outpdf)
        return (n,"fail",0)
    except Exception:
        return (n,"err",0)
    finally:
        try: subprocess.run(["rm","-rf",prof],capture_output=True)
        except: pass

t0=time.time()
with ThreadPoolExecutor(max_workers=6) as ex:
    res=list(ex.map(render_one, [(n,u,i) for i,(n,u) in enumerate(targets)]))
ok=[r for r in res if r[1]=="ok"]
fail=[r for r in res if r[1] not in ("ok","exists")]
print(f"\n렌더 성공 {len(ok)}/ {len(targets)} ({(time.time()-t0)/60:.1f}분)")
for n,_,s in ok: print(f"  ✓ {n} ({s})")
print(f"실패 {len(fail)}")
json.dump({"ok":[r for r in res if r[1]=="ok"],"fail":[r[0] for r in fail]}, open(r"C:\Users\USER\camnemi-crm\backend\_junior_render_par.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
