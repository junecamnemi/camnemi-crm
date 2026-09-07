# -*- coding: utf-8 -*-
import fitz
p = "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/초당대_대학원_모집요강.pdf"
doc = fitz.open(p)
pg = doc[2]
words = pg.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
# print words sorted by y then x with coords
for w in sorted(words, key=lambda w: (round(w[1]), w[0])):
    print("%6.1f %6.1f  %s" % (w[0], w[1], w[4]))
