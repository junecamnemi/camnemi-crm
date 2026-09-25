import os, re, json
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
# 외국인/ 하위폴더와 상위 폴더 모두 포함 전수 스캔
print("=== 1) adiga_*_외국인_모집요강 (하위 포함) ===")
for d in sorted(os.listdir(GUIDER)):
    if "외국인" not in d: continue
    p = os.path.join(GUIDER, d)
    if not os.path.isdir(p): continue
    # 재귀 파일
    nf = 0; subs=[]
    for root, dirs, files in os.walk(p):
        pdfs = [f for f in files if f.lower().endswith(('.pdf','.hwp','.hwpx','.hml'))]
        if pdfs:
            subs.append((os.path.relpath(root,p), len(pdfs)))
            nf += len(pdfs)
    print(f"  {d}: 총 {nf}개 | 하위 {subs}")

print()
print("=== 2) 파일명 규칙 샘플 ===")
base = os.path.join(GUIDER, "adiga_2026_외국인_모집요강", "외국인")
files = sorted(os.listdir(base))
for f in files[:8]:
    print("   ", f)
print("   ...")
print("   file count:", len(files))

print()
print("=== 3) 전문대 외국인 요강 별도 폴더? ===")
for d in sorted(os.listdir(GUIDER)):
    if "전문" in d or "junior" in d.lower():
        p = os.path.join(GUIDER, d)
        if os.path.isdir(p):
            allf=[]
            for root,dd,ff in os.walk(p):
                allf += [os.path.join(root,f) for f in ff if f.lower().endswith(('.pdf','.hwp','.hwpx')) and '외국인' in f]
            print(f"  {d}: 외국인 언급 파일 {len(allf)}개")