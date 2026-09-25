import os, re
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
# 1) 전문대 폴더 - 외국인 여부 (파일명/내용으로 확인)
jr = os.path.join(GUIDER, "adiga_2026_전문대학_모집요강")
files = [f for f in os.listdir(jr) if f.lower().endswith('.pdf')]
print(f"전문대 폴더 PDF {len(files)}개 — 파일명에 외국인 여부:")
ext = {'외국인':0, '일반/기타':0, '불명':0}
for f in files[:60]:
    if '외국인' in f or 'foreign' in f.lower() or 'International' in f:
        ext['외국인'] += 1
    elif f.startswith('_'):
        ext['불명'] += 1
    else:
        ext['일반/기타'] += 1
print("  ", ext)
print("  외국인 키워드 파일 예:", [f for f in files if '외국인' in f][:5])
print("  일반 파일 예:", [f for f in files if '외국인' not in f and not f.startswith('_')][:8])
print()
# 2) 4년제 외국인 모집요강 폴더 확인 (앞서 비었음)
for d in ["adiga_2026_외국인_모집요강", "adiga_2027_외국인_모집요강"]:
    p = os.path.join(GUIDER, d)
    n = len([f for f in os.listdir(p) if f.lower().endswith(('.pdf','.hwp','.hml'))]) if os.path.isdir(p) else '폴더없음'
    print(f"{d}: {n}개")