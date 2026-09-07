# -*- coding: utf-8 -*-
"""v2: parse scholarship_enroll/existing (which are descriptive strings like
'TOPIK 4급 이상 또는 KIIP... → 100%; ...IELTS 6.5 이상 → 100%; ...IELTS 5.5 → 30%')
into structured tiers for data.js, then rebuild data.js scholarships."""
import json, re, os

DATA = r"C:\Users\USER\camnemi-crm\data.js"
BASE = r"C:\Users\USER\camnemi-crm\backend"
CURATION_FILES = [
    "_curation_out_batch0.json", "_curation_out_batch1.json",
    "_curation_out_batch2.json", "_curation_out_batch3.json",
    "_curation_ma_out_batch0.json", "_curation_ma_out_batch1.json",
    # wave-2 (2026 BA)
    "_w2_out_batch0.json", "_w2_out_batch1.json", "_w2_out_batch2.json",
    "_w2_out_batch3.json", "_w2_out_batch4.json", "_w2_out_batch5.json",
    "_w2_out_batch6.json", "_w2_out_batch7.json", "_w2_out_batch8.json",
    "_w2_out_batch9.json",
]

def parse_ladder(text, level):
    """Parse descriptive scholarship (string OR list) into tier list.
    Handles patterns:
      'TOPIK 6급 100% / TOPIK 5급 80%'   (slash separator, direct %)
      'TOPIK 4급 → 100%'                  (arrow)
      'IELTS 5.5 이상 → 30%'               (arrow, long alt clauses)"""
    tiers = []
    if not text:
        return tiers
    if isinstance(text, list):
        text = "\n".join(str(x) for x in text)
    # normalize: strip spaces around slash, keep as-is
    # pattern A: 'TOPIK 6급 100%' or 'IELTS 6.5 100%' with optional 급/이상/만
    for m in re.finditer(r"(TOPIK|IELTS)\s*(?:\(IBT\)\s*)?(?:급\s*)?([\d.]+)[^%\d]{0,30}?(\d{1,3})\s*%", text):
        test, score, pct = m.group(1), m.group(2), m.group(3)
        try:
            sc = int(score) if "." not in score else float(score)
        except ValueError:
            continue
        if test == "TOPIK" and sc > 6:
            continue
        if test == "IELTS" and sc > 9:
            continue
        # dedupe by (test, score)
        if not any(t["score_type"] == test and t["score"] == sc for t in tiers):
            tiers.append({"score_type": test, "score": sc, "amount": f"{pct}%"})
    # pattern B: arrow-style 'TOPIK 3급→40%' with % possibly inside parens '(약 20%)'
    for m in re.finditer(r"(TOPIK|IELTS)\s*(?:\(IBT\)\s*)?(?:급\s*)?([\d.]+)[^→]{0,60}?→[^%]{0,40}?(?:약\s*)?(\d{1,3})\s*%", text):
        test, score, pct = m.group(1), m.group(2), m.group(3)
        try:
            sc = int(score) if "." not in score else float(score)
        except ValueError:
            continue
        if test == "TOPIK" and sc > 6:
            continue
        if test == "IELTS" and sc > 9:
            continue
        if not any(t["score_type"] == test and t["score"] == sc for t in tiers):
            tiers.append({"score_type": test, "score": sc, "amount": f"{pct}%"})
    # pattern C: combined alternatives 'TOPIK 3급 또는 IELTS 5.5 또는 TOEFL 53 이상 30%'
    # each score mention before NN% maps to that %
    for m in re.finditer(r"(TOPIK|IELTS)\s*(?:\(IBT\)\s*)?(?:급\s*)?([\d.]+)[^%]{0,80}?(?:이상\s*)?(\d{1,3})\s*%", text):
        test, score, pct = m.group(1), m.group(2), m.group(3)
        try:
            sc = int(score) if "." not in score else float(score)
        except ValueError:
            continue
        if test == "TOPIK" and sc > 6:
            continue
        if test == "IELTS" and sc > 9:
            continue
        if not any(t["score_type"] == test and t["score"] == sc for t in tiers):
            tiers.append({"score_type": test, "score": sc, "amount": f"{pct}%"})
    return tiers

content = open(DATA, encoding="utf-8").read()
start = content.find("[")
depth = 0
for i in range(start, len(content)):
    if content[i] == "[": depth += 1
    elif content[i] == "]":
        depth -= 1
        if depth == 0:
            end = i
            break
data = json.loads(content[start:end + 1])
dn = {u.get("n"): u for u in data}

SHORT2FULL = {
    "가톨릭대": "가톨릭대학교", "국민대": "국민대학교", "인제대": "인제대학교",
    "전주대": "전주대학교", "제주국제대": "제주국제대학교", "조선대": "조선대학교",
    "중부대": "중부대학교", "창신대": "창신대학교", "청주대": "청주대학교",
    "초당대": "초당대학교", "충북대": "충북대학교",
}

n_school = 0
n_replaced = 0
for cf in CURATION_FILES:
    fp = os.path.join(BASE, cf)
    if not os.path.exists(fp):
        continue
    for e in json.load(open(fp, encoding="utf-8")):
        short = e.get("school", "")
        name = re.sub(r"^\d+_", "", short).strip()
        full = SHORT2FULL.get(name, name)
        u = dn.get(full)
        if not u:
            continue
        is_ma = "ma_" in cf
        sch = u.get("scholarships") or []
        # remove auto-generated + any enroll/existing tiers entry that would conflict;
        # KEEP name-based entries without tiers (descriptive like '정착장학금 50만원')
        keep = []
        for s in sch:
            nm = s.get("name", "")
            if nm.startswith("입학장학금(TOPIK/IELTS)") or nm.startswith("재학 성적장학금"):
                continue
            if s.get("type") in ("enroll", "existing") and s.get("tiers"):
                continue  # old structured enroll/existing ladder -> replaced by curated
            keep.append(s)
        new_items = []
        for field, typ, label in (("scholarship_enroll", "enroll", "입학장학금(TOPIK/IELTS)"),
                                  ("scholarship_existing", "existing", "재학 성적장학금")):
            tiers = parse_ladder(e.get(field) or "", None)
            if tiers:
                new_items.append({
                    "name": label,
                    "level": "grad" if is_ma else "undergrad",
                    "type": typ,
                    "tiers": tiers,
                })
        if new_items:
            u["scholarships"] = keep + new_items
            n_school += 1
            n_replaced += len(new_items)

content_out = content[:start] + json.dumps(data, ensure_ascii=False, indent=2) + content[end + 1:]
open(DATA, "w", encoding="utf-8").write(content_out)
print(f"{n_school}개 학교 장학금 tiers 반영 ({n_replaced}개 항목)")
