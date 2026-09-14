import pymupdf, re, os, glob

UP = r"C:\Users\USER\내 드라이브\02_Crawling_Sheet\University_Project"
cands = glob.glob(os.path.join(UP, "**", "*경운대학교[본교]_2026_외국인*.pdf"), recursive=True) or \
        glob.glob(os.path.join(UP, "**", "*경운대*외국인*.pdf"), recursive=True)
print("찾은 파일:", cands)
if cands:
    src = cands[0]
    d = pymupdf.open(src)
    print(f"원본: {os.path.getsize(src)/1024/1024:.1f} MB, {len(d)}페이지")
    # page text + which pages mention 외국인/등록금/장학/전형
    for i in range(len(d)):
        t = d[i].get_text()
        head = re.sub(r"\s+", " ", t)[:80]
        print(f"  p{i+1}: {head}")
    d.close()
