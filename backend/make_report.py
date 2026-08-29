# -*- coding: utf-8 -*-
"""Build a visual recommendation report image (PNG) with school logos.

Composes school cards: logo + English name + rank + location + language req
+ tuition (USD) + apply window. Uses the _logos.json map and verified_kb.json.
"""
import json
import os
import math
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))
from en_output import en_name, en_region, logo, fmt_tuition_usd, en_lang, en_scholarship

from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\USER\camnemi-crm"
KB = json.load(open(os.path.join(BASE, "backend", "verified_kb.json"), encoding="utf-8"))

# ---- fonts ----
def F(size, bold=False):
    path = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(path, size)


def fit_text(dr, text, font, max_w):
    """Truncate text with ellipsis if it exceeds max_w pixels."""
    if not text:
        return text
    if dr.textlength(text, font=font) <= max_w:
        return text
    ell = "…"
    while text and dr.textlength(text + ell, font=font) > max_w:
        text = text[:-1]
    return text + ell


def wrap_text(dr, text, font, max_w, max_lines=2):
    """Wrap text to at most max_lines lines fitting max_w. Returns (line1, line2)."""
    if not text:
        return ("", "")
    if dr.textlength(text, font=font) <= max_w:
        return (text, "")
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if dr.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) <= max_lines:
        return (lines[0], lines[1] if len(lines) > 1 else "")
    # too long — hard truncate line 2 with ellipsis
    l1 = lines[0]
    rest = " ".join(lines[1:])
    return (l1, fit_text(dr, rest, font, max_w))

# ---- palette ----
NAVY = (13, 27, 62)
BLUE = (0, 92, 175)
LIGHT = (240, 245, 252)
GREY = (90, 100, 115)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)
GREEN = (20, 120, 60)

CARD_W, CARD_H = 720, 168
PAD = 24
GAP = 14


def short_scholarship(kr):
    """Return a compact English scholarship summary from the KB line."""
    en = en_scholarship(kr)
    if not en:
        return ""
    import re
    # Try to extract the single best (highest %) tier as a clean phrase.
    # Common pattern after translation: "TOPIK 5 -> 80% tuition off / TOPIK 6 -> 90% ..."
    tiers = re.split(r"\s*/\s*", en)
    best = None
    best_pct = 0
    for t in tiers:
        t = t.strip()
        m = re.search(r"(\d+)%", t)
        if not m:
            continue
        pct = int(m.group(1))
        # prefer the most actionable: highest % wins; tie -> longer/earlier
        if pct > best_pct or (pct == best_pct and best is None):
            best = t
            best_pct = pct
    if best:
        # shorten redundant "tuition off" tail
        return best[:80]
    return en[:80]


def scholarship_summary(d):
    """Pick the most student-relevant scholarship line from a KB entry.
    Returns (text, level_hint) — level_hint says which score unlocks it, if parseable."""
    sch = d.get("scholarships") or {}
    enroll = sch.get("enroll") or []
    if enroll:
        return short_scholarship(enroll[0])
    existing = sch.get("existing") or []
    if existing:
        return short_scholarship(existing[0])
    return ""

def load_logo(path):
    """Load & crop logo to a square, returns RGBA image or None."""
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        return None
    try:
        im = Image.open(full).convert("RGBA")
    except Exception:
        return None
    w, h = im.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    im = im.crop((left, top, left + s, top + s))
    # white background for transparent logos (e.g. svg-rendered png)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg

def draw_card(d, i):
    """Draw one school card onto a fresh image, return it."""
    card = Image.new("RGB", (CARD_W, CARD_H), WHITE)
    dr = ImageDraw.Draw(card)

    # left accent bar
    dr.rectangle([0, 0, 8, CARD_H], fill=BLUE)

    # logo
    lg = load_logo(d["logo"])
    box = 92
    if lg:
        lg = lg.resize((box, box), Image.LANCZOS)
        card.paste(lg, (PAD + 6, (CARD_H - box) // 2), lg)
    lx = PAD + 6 + box + 18

    # number badge
    dr.ellipse([lx - 4, 14, lx + 28, 42], fill=GOLD)
    dr.text((lx + 12 - 4, 16), str(i), font=F(18, True), fill=NAVY, anchor="mm")

    # name + rank (rank always shown separately so it's never truncated away)
    name = d["name"]
    rk = f"  #{d['rank']}" if d["rank"] not in (None, "-", "") else ""
    name_disp = fit_text(dr, name, F(20, True), max_w=360)
    dr.text((lx + 34, 14), name_disp, font=F(20, True), fill=NAVY)
    if rk:
        nw = dr.textlength(name_disp, font=F(20, True))
        dr.text((lx + 34 + nw + 6, 16), rk.strip(), font=F(16, True), fill=GOLD)

    # location
    dr.text((lx + 34, 44), d["loc"], font=F(14), fill=GREY)

    # language
    lang_disp = d["lang"] or ""
    if lang_disp:
        # keep within middle column (avoid touching right column)
        lang_disp = fit_text(dr, lang_disp, F(12), max_w=330)
        dr.text((lx + 34, 66), lang_disp, font=F(12), fill=BLUE)

    # scholarship (wraps to a 2nd line if needed)
    sch_disp = d["scholarship"] or "check 2027 guide"
    sch_disp = ("🎓 " + sch_disp).strip()
    line1, line2 = wrap_text(dr, sch_disp, F(12), max_w=330)
    dr.text((lx + 34, 86), line1, font=F(12), fill=GREEN)
    if line2:
        dr.text((lx + 34, 104), line2, font=F(12), fill=GREEN)

    # right: tuition + apply
    rx = CARD_W - PAD - 8
    dr.text((rx, 20), d["tuition"], font=F(19, True), fill=NAVY, anchor="ra")
    dr.text((rx - 2, 50), "per semester", font=F(12), fill=GREY, anchor="ra")
    if d["apply"]:
        apply_disp = fit_text(dr, d["apply"], F(12, True), max_w=200)
        dr.text((rx, 82), apply_disp, font=F(12, True), fill=(180, 60, 60), anchor="ra")
    dr.text((rx, 108), "APPLY", font=F(11), fill=GREY, anchor="ra")

    return card

def build_report(school_keys, title="University Recommendation"):
    """school_keys: list of (kb_name, rank_label) to include in order."""
    rows = []
    for i, name in enumerate(school_keys, 1):
        d = KB["schools"].get(name) or KB.get("junior", {}).get("schools", {}).get(name)
        if not d:
            continue
        tu = fmt_tuition_usd(d.get("tuition_semester") or d.get("tuition_min"))
        if not tu:
            tu = "confirm"
        lang = d.get("lang_req") or (
            f"TOPIK {d.get('topik_req')}" if d.get("topik_req") else "No strict requirement"
        )
        rows.append({
            "name": en_name(name),
            "rank": d.get("rank") if d.get("rank") not in ("-", "") else None,
            "loc": en_region(d.get("region") or d.get("loc")),
            "lang": en_lang(lang),
            "tuition": tu,
            "apply": d.get("period") or "",
            "scholarship": scholarship_summary(d),
            "logo": logo(name),
        })

    n = len(rows)
    H = 90 + n * (CARD_H + GAP) + 90
    W = CARD_W + 2 * PAD
    img = Image.new("RGB", (W, H), LIGHT)
    dr = ImageDraw.Draw(img)

    # header
    dr.rectangle([0, 0, W, 90], fill=NAVY)
    dr.text((PAD, 20), title, font=F(26, True), fill=WHITE)
    dr.text((PAD, 56), f"{n} schools  ·  Camnemi University Advisor", font=F(14), fill=(200, 210, 230))

    y = 90 + GAP
    for i, row in enumerate(rows, 1):
        card = draw_card(row, i)
        img.paste(card, (PAD, y))
        y += CARD_H + GAP

    dr.text((PAD, y + 8), "All English track · Foreigner admission · USD @1,400 KRW/$ (rounded up to $100)",
            font=F(13), fill=GREY)
    return img

if __name__ == "__main__":
    import sys
    # usage: python make_report.py [ielts] [title]
    # default example: IELTS 6.0 business/international
    ielts = sys.argv[1] if len(sys.argv) > 1 else "6.0"
    title = sys.argv[2] if len(sys.argv) > 2 else f"IELTS {ielts} · Business & International"

    if ielts == "5.5":
        picks = ["중앙대학교", "건국대학교", "인하대학교", "한국외국어대학교", "세종대학교", "가천대학교", "광운대학교", "한양대학교(ERICA)"]
    else:
        # IELTS 6.0 — business/international focused, by rank
        picks = ["서울대학교", "연세대학교", "경희대학교", "이화여자대학교", "중앙대학교", "건국대학교", "한국외국어대학교", "숙명여자대학교"]

    img = build_report(picks, title=title)
    out = os.path.join(BASE, "backend", f"report_ielts{ielts.replace('.', '_')}.png")
    img.save(out)
    print("saved:", out, img.size)
