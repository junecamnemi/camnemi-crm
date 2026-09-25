import os, re, json
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"

# 인벤토리: 폴더별 외국인 요강 전수
def count(root):
    n=0; exts=set()
    if not os.path.isdir(root): return 0, set()
    for r,dd,ff in os.walk(root):
        for f in ff:
            if f.lower().endswith(('.pdf','.hwp','.hwpx','.hml')):
                n+=1; exts.add(f.split('.')[-1].lower())
    return n, exts

print("=== 📁 외국인 요강 인벤토리 ===")
inv = [
    ("adiga_2026_외국인_모집요강/외국인", "4년제 2026 외국인"),
    ("adiga_2027_외국인_모집요강/외국인", "4년제 2027 외국인"),
    ("adiga_2027_외국인_모집요강/재외국민", "재외국민 (별도)"),
    ("adiga_2027_외국인_모집요강/own_site", "자체사이트 2027 BA 외국인"),
    ("adiga_2026_전문대학_모집요강", "전문대 (외국인만 필터)"),
]
for rel, label in inv:
    p = os.path.join(GUIDER, rel)
    n, exts = count(p)
    print(f"  {label:30s} {n:4d}개  ({sorted(exts)})")

# 전문대에서 외국인만
jr = os.path.join(GUIDER, "adiga_2026_전문대학_모집요강")
jr_foreign = [f for f in os.listdir(jr) if '외국인' in f and f.lower().endswith('.pdf')]
print(f"\n전문대 외국인 전용: {len(jr_foreign)}개")

# 총합
total = 0
for rel, label in inv:
    p = os.path.join(GUIDER, rel)
    n,_ = count(p)
    total += n
print(f"\n외국인(재외국민 제외) 요강 총계: (4년제 2026+2027 외국인) ")