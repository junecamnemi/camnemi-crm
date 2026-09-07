# -*- coding: utf-8 -*-
"""Headless-Chrome render remaining junior colleges' guide_url to PDF (no LLM).
Fallback when no direct 요강 PDF is downloadable but the admission page has info."""
import json, os, subprocess, time

KB = json.load(open(r"C:\Users\USER\camnemi-crm\backend\verified_kb.json", encoding="utf-8"))
js = KB["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TMP = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\USER\AppData\Local"), "Temp")

def norm(s): return s.replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have = set(norm(os.path.splitext(f)[0].replace("_전문학사_모집요강","").replace("_전문학사학위심화","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf"))

targets=[(n,v["guide_url"]) for n,v in js.items() if v.get("guide_url") and norm(n) not in have]
print(f"렌더 대상: {len(targets)}")

def render(url, outpdf, idx):
    prof = os.path.join(TMP, f"jrender_{idx}")
    try:
        r = subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--no-first-run",
            "--disable-extensions","--timeout=25000","--virtual-time-budget=7000",
            f"--user-data-dir={prof}","--print-to-pdf="+outpdf, url],
            capture_output=True, timeout=45)
        if os.path.exists(outpdf):
            sz=os.path.getsize(outpdf)
            head=open(outpdf,'rb').read(4)
            return sz, head==b"%PDF"
        return 0, False
    except Exception as e:
        return 0, False
    finally:
        try: subprocess.run(["rm","-rf",prof])
        except: pass

ok=[]; fail=[]
for i,(n,u) in enumerate(targets):
    sn=norm(n)
    if sn in have: continue
    outpdf = os.path.join(SAVEDIR, f"{n}_전문학사_입학안내(렌더).pdf")
    if os.path.exists(outpdf): have.add(sn); continue
    sz, isp = render(u, outpdf, i)
    if isp and sz>30000:
        ok.append((n,sz)); have.add(sn)
    else:
        if os.path.exists(outpdf): os.remove(outpdf)
        fail.append(n)
    time.sleep(0.5)

print(f"\n렌더 성공: {len(ok)}")
for n,s in ok: print(f"  ✓ {n} ({s})")
print(f"\n실패: {len(fail)}")
print(" ", fail)
json.dump({"ok":ok,"fail":fail}, open(r"C:\Users\USER\camnemi-crm\backend\_junior_render.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
