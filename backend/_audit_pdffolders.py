import os, json, re, sys
sys.path.insert(0, ".")
GUIDER = r"C:\Users\wisew\내 드라이브\02_Crawling_Sheet\University_Project"
folders = {
    "junior2026": os.path.join(GUIDER, "adiga_2026_전문대학_모집요강"),
    "junior2027": os.path.join(GUIDER, "adiga_2027_전문대학_모집요강"),
    "ba2026": os.path.join(GUIDER, "adiga_2026_외국인_모집요강"),
    "ba2027": os.path.join(GUIDER, "adiga_2027_외국인_모집요강"),
    "ma2027": os.path.join(GUIDER, "adiga_2027_대학원_모집요강"),
    "lang2027": os.path.join(GUIDER, "adiga_2027_어학연수_모집요강"),
}
for label, p in folders.items():
    if not os.path.isdir(p):
        print(f"{label}: 폴더 없음")
        continue
    files = [f for f in os.listdir(p) if f.lower().endswith(('.pdf','.hwp','.hml','.docx'))]
    print(f"{label}: PDF {len(files)}개")
    # 샘플 파일명
    for f in files[:5]:
        print(f"    {f}")