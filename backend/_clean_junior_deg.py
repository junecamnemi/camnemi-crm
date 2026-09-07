# -*- coding: utf-8 -*-
"""Clean duplicate PDFs in the junior degree folder (keep one per school, prefer
real 요강 over 렌더), then build a manifest."""
import os, re, json, shutil

SAVEDIR = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project\adiga_2026_전문대학_모집요강"
files = [f for f in os.listdir(SAVEDIR) if f.endswith(".pdf")]

def school_key(fn):
    k = fn.replace(".pdf", "")
    k = re.sub(r"_전문학사_(모집요강|입학안내\(렌더\)|입학안내)", "", k)
    k = re.sub(r"_전문학사학위심화_모집요강", "", k)
    k = k.replace("대학교", "").replace("대학", "").replace("전문대", "").replace(" ", "")
    return k

# group by school
groups = {}
for f in files:
    groups.setdefault(school_key(f), []).append(f)

# keep best: prefer '모집요강'(real pdf) > '학위심화' > '렌더'; among same, biggest
removed = []
for k, flist in groups.items():
    if len(flist) <= 1: continue
    def rank(f):
        if "_전문학사_모집요강" in f: return 0
        if "_학위심화" in f: return 1
        if "렌더" in f: return 2
        return 1
    flist_sorted = sorted(flist, key=lambda f: (rank(f), -os.path.getsize(os.path.join(SAVEDIR,f))))
    keep = flist_sorted[0]
    for f in flist_sorted[1:]:
        os.remove(os.path.join(SAVEDIR, f))
        removed.append(f)

final = [f for f in os.listdir(SAVEDIR) if f.endswith(".pdf")]
print(f"중복 제거 {len(removed)}개 → 최종 {len(final)}개")
# rename renders to a consistent marker? keep as-is.

# build manifest
manifest = []
for f in sorted(final):
    manifest.append({"school": f.replace(".pdf","").replace("_전문학사_모집요강","").replace("_전문학사_입학안내(렌더)","").replace("_전문학사학위심화_모집요강",""), "file": f, "local": os.path.join(SAVEDIR,f), "kind": "render" if "렌더" in f else ("degree_심화" if "심화" in f else "요강")})
json.dump(manifest, open(r"C:\Users\USER\camnemi-crm\backend\junior_degree_pdfs.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"매니페스트 {len(manifest)}개 저장 (junior_degree_pdfs.json)")
