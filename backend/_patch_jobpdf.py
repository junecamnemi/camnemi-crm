import re
p = r"C:\Users\USER\camnemi-crm\backend\_job_pdf.py"
c = open(p, encoding="utf-8").read()
c = c.replace('KR="korea"; KRB="korea"  # pymupdf builtin CJK (no 13MB embed)',
              'KR=r"C:\\Windows\\Fonts\\malgun.ttf"; KRB=r"C:\\Windows\\Fonts\\malgunbd.ttf"')
if 'insert_font(fontname="KR",fontfile=KR)' not in c:
    c = c.replace('def newpage(cover=False):\n    pg=d.new_page(width=595,height=842); ',
                  'def newpage(cover=False):\n    pg=d.new_page(width=595,height=842); pg.insert_font(fontname="KR",fontfile=KR); pg.insert_font(fontname="KRB",fontfile=KRB); ')
c = re.sub(r"d\.save\(out[^)]*\)",
           "import sys\ntry:\n    d.subset_fonts()\nexcept Exception as e:\n    print('subset skip', e)\nd.save(out, garbage=4, deflate=True)", c)
open(p, "w", encoding="utf-8").write(c)
print("patched:", "insert_font" in c, "| subset:", "subset_fonts" in c)
