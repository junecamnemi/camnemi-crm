#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build unified visa KB (사증발급 + 체류변경 connected) and wire it into the bot query."""
import json, os, datetime

B = r"C:\Users\USER\camnemi-crm\backend"
HM = os.path.join(B, "hikorea_manuals")

# sources
change = json.load(open(os.path.join(B, "visa_change_rules_kr.json"), encoding="utf-8"))
combined = json.load(open(os.path.join(HM, "사증_체류_통합분석_pro.json"), encoding="utf-8"))
ocr = json.load(open(os.path.join(HM, "사증민원_이미지페이지_OCR.json"), encoding="utf-8"))

kb = {
  "_meta": {
    "title": "한국 비자 통합 KB — 사증발급(해외) + 체류변경(국내) 연결",
    "source": "법무부 출입국·외국인정책본부 「사증민원 자격별 안내 매뉴얼」·「체류민원 자격별 안내 매뉴얼」 (2026.9)",
    "built": datetime.date.today().isoformat(),
    "caveat": "최종 판단은 출입국·외국인청(1345). 본 KB는 상담 참고용.",
    "flow": combined.get("flow_note", ""),
  },
  "flow": {
    "step1_sajeung": "해외 재외공관에서 사증(비자) 발급 — 자격별 서류 제출",
    "step2_entry": "입국 (장기체류자격은 외국인등록 대상)",
    "step3_domestic": "국내에서 체류자격 변경허가 / 체류기간 연장",
    "key_path": "D-4(어학) 사증 → 입국 → 국내에서 D-2(유학) 체류자격 변경 (이전 D-4 성적·출석·연수증명서 필요)",
  },
  "by_status": {},       # from combined pro analysis
  "change_matrix": change.get("changeable", {}),   # existing D-4/D-2/E-9/E-7 rules
  "income_requirements": change.get("income_requirements", {}),
  "photo_spec": ocr.get("279", ""),   # 외국인등록용 사진 규격 (OCR)
}

for x in combined.get("statuses", []):
    kb["by_status"][x["status"]] = {
        "sajeung_issuance": x.get("sajeung_issuance", {}),
        "domestic_change": x.get("domestic_change", {}),
        "connection": x.get("connection", ""),
    }

out = os.path.join(B, "visa_kb_kr.json")
json.dump(kb, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장:", out)
print("by_status:", list(kb["by_status"].keys()))
print("change_matrix:", list(kb["change_matrix"].keys()) if isinstance(kb["change_matrix"], dict) else kb["change_matrix"])
print("photo_spec:", len(kb["photo_spec"]), "자")
print("flow:", kb["flow"]["key_path"])
