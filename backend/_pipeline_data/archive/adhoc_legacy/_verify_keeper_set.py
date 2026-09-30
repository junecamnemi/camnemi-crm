# -*- coding: utf-8 -*-
"""Confirm the applied keeper set (adiga-style names) exists and the dupes are gone."""
import json, os
G = r"G:/공유 드라이브/Hermes/Camnemi/02_Crawling_Sheet/University_Project/guides"
man = json.load(open(os.path.join(G, "_library_manifest.json"), encoding="utf-8"))
act = [e["name"] for e in man["entries"] if not e.get("archived")]
checks = {
    "0000005_경북대학교[본교]_2027_외국인.pdf": True,
    "0000179_청주대학교[본교]_2027_외국인.pdf": True,
    "0000196_한동대학교[본교]_2027_외국인.pdf": True,
    "0000179_청주대학교_Cheongju University (CJU)_BA_2027.pdf": False,
    "0000196_한동대학교_Handong Global University (HGU)_BA_2027.pdf": False,
    "한세대학교_ba.pdf": True,
    "한세대학교[본교]_2027_외국인.pdf": True,
}
ok = True
for n, expect in checks.items():
    got = n in act
    flag = "OK " if got == expect else "BAD"
    if got != expect:
        ok = False
    print(f"{flag} active={got} (expected {expect})  {n}")
print("ALL AS EXPECTED" if ok else "MISMATCH")