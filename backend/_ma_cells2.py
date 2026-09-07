# -*- coding: utf-8 -*-
import fitz
p = "C:/Users/USER/내 드라이브/02_Crawling_Sheet/University_Project/adiga_2026_대학원_모집요강/청주대_대학원_모집요강.pdf"
doc = fitz.open(p)
pg = doc[0]
words = pg.get_text("words")
for w in sorted(words, key=lambda w: (round(w[1]), w[0])):
    print("%6.1f %6.1f  %s" % (w[0], w[1], w[4]))
