# -*- coding: utf-8 -*-
"""Deep-scan script for junior colleges whose foreigner admission is not_checked.
For each, probe the official admission/guide page for foreigner(외국인/유학생) track.
Classifies: obtained(외국인 전형 확인) / no_public_guide / closed / merged.
This is the automated weekday complement to manual verification.
Runs many schools with light HTTP; logs a pending list for prioritized curation.
"""
import json, os, re, subprocess, time, urllib.parse

KB_PATH = r"C:\Users\USER\camnemi-crm\backend\verified_kb.json"
kb = json.load(open(KB_PATH, encoding="utf-8"))
jr = kb["junior"]["schools"]
SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"

# candidates: not_checked/missing that have a guide_url
cands = []
for n, v in jr.items():
    if v.get("foreign_guide", "missing") in ("not_checked", "missing") and v.get("guide_url"):
        cands.append((n, v["guide_url"]))

print(f"딥-스캔 후보: {len(cands)}개 (not_checked + guide_url 보유)")

def norm(s): return re.sub(r"\[.*?\]","",s).replace("대학교","").replace("대학","").replace("전문대","").replace(" ","")
have_files = set(norm(os.path.splitext(f)[0].replace("_전문학사_외국인모집요강","")) for f in os.listdir(SAVEDIR) if f.endswith(".pdf") and "_외국인모집요강" in f)

def curl(url, timeout=15):
    try:
        return subprocess.run(["curl","-sL","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120","--max-time",str(timeout),url],capture_output=True).stdout
    except: return b""

# Fast HTTP pass: does the guide_url (or its depth-1 pages) mention 외국인/유학?
FKEY = re.compile(r'외국인|유학|순수외국인|international|foreign|\bD-2\b|\bD2\b', re.I)

results = {}
for n, u in cands:
    sn = norm(n)
    # already have a foreigner or degree pdf?
    if any(f in sn or sn in f for f in have_files):
        results[n] = "have_pdf_on_disk"
        continue
    html = curl(u)
    if not html:
        results[n] = "unreachable"
        continue
    txt = html.decode("utf-8","ignore")
    hits = len(FKEY.findall(txt))
    # collect foreigner-related links for follow-up
    flinks = re.findall(r'href="([^"]*(?:외국인|유학|foreign|intl|international)[^"]*)"', txt, re.I)
    results[n] = {"hits": hits, "flinks": flinks[:5], "has_pdf_link": "모집요강" in txt or bool(re.search(r'\.pdf', txt, re.I))}
    time.sleep(0.2)

# save report
report = {"note": "딥-스캔: not_checked 전문대 guide_url에서 외국인/유학 언급 탐색 (2026-09-06)",
          "results": results}
json.dump(report, open(r"C:\Users\USER\camnemi-crm\backend\_junior_deep_scan_daily.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

n_have = sum(1 for v in results.values() if v=="have_pdf_on_disk")
n_unreach = sum(1 for v in results.values() if v=="unreachable")
n_hit = sum(1 for v in results.values() if isinstance(v,dict) and v.get("hits",0)>0)
n_nohit = sum(1 for v in results.values() if isinstance(v,dict) and v.get("hits",0)==0)
print(f"디스크 PDF 보유: {n_have} | 연결불가: {n_unreach} | 외국인 언급 {n_hit} | 미언급 {n_nohit}")

# Write a prioritized pending file: schools with foreigner mention but no curated foreign_guide
pending = []
for n, v in results.items():
    if isinstance(v, dict) and v.get("hits",0) >= 2:
        pending.append({"school": n, "hits": v["hits"], "flinks": v.get("flinks",[])})
pending.sort(key=lambda x:-x["hits"])
json.dump(pending, open(r"C:\Users\USER\camnemi-crm\backend\_junior_foreign_pending.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"우선 큐레이션 대상(외국인 언급 2+): {len(pending)}개")