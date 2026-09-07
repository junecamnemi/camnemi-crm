# -*- coding: utf-8 -*-
import json, io

RES = [
{"school":"가야대학교","status":"not_found","url":"","title":"","note":"No official 어학당/한국어교육원 2027 schedule found via search"},
{"school":"가천대학교","status":"2026_or_older","url":"https://oia.gachon.ac.kr/international/a/m/klecInfo.do","title":"가천대학교 한국어교육센터","note":"Official KLEC info page shows no 2027 정규과정 schedule"},
{"school":"가톨릭관동대학교","status":"2026_or_older","url":"http://www.cku.ac.kr/oia/5520/subview.do","title":"가톨릭관동대학교 한국어교육원 Admission Guide","note":"Official page shows no 2027 schedule"},
{"school":"가톨릭꽃동네대학교","status":"not_found","url":"","title":"","note":"Only 2027 degree admission plan found; no 어학당/한국어교육원 schedule"},
{"school":"가톨릭대학교","status":"2026_or_older","url":"https://kli.catholic.ac.kr/kli/index.do","title":"가톨릭대학교 한국어교육원","note":"KLEC index shows 2026학년도 정규과정; 학사일정 page no 2027 dates"},
{"school":"감리교신학대학교","status":"not_found","url":"","title":"","note":"No 어학당/한국어교육원 found; only degree admission & 평생교육원 KIIP"},
{"school":"강남대학교","status":"not_found","url":"","title":"","note":"No official 한국어학당/어학원 2027 schedule found via search"},
{"school":"강서대학교","status":"not_found","url":"","title":"","note":"No 어학당/한국어교육원 found; only degree admission info"},
{"school":"강원대학교","status":"unknown_year","url":"https://oiaknu.kangwon.ac.kr/oiaknu/language/korean/guide-chuncheon01.do","title":"강원대학교 국제교류처 한국어연수과정 Application","note":"Official guide page but no 2027 dates shown"},
{"school":"건국대학교","status":"unknown_year","url":"https://kli.konkuk.ac.kr/bbs/kli/4236/1200013/artclView.do?layout=unknown","title":"건국대 언어교육원 EAP(D4-7) 모집 안내","note":"2027 봄/여름 EAP(영어) 일정 published; 한국어 정규과정 2027 schedule not confirmed"},
{"school":"건양대학교","status":"2026_or_older","url":"https://interedu.konyang.ac.kr/interedu/sub02_03_01.do","title":"건양대 한국어교육센터 교육목적 및 일정","note":"Generic term schedule (2월말/5월중순/8월말/11월중순), no 2027 dates; notices 2026"},
{"school":"경기대학교","status":"2026_or_older","url":"https://www.kyonggi.ac.kr/IOIE/contents.do?key=1494","title":"경기대 국제교육원 한국어과정 모집요강","note":"Brochures labeled 2026 (Korean/Chinese/English/Vietnamese); no 2027 version"},
]

path = r"C:/Users/USER/camnemi-crm/backend/_lang_batches/lang_batch_01_result.json"
with io.open(path, "w", encoding="utf-8") as f:
    json.dump(RES, f, ensure_ascii=False, indent=1)
print("written", len(RES))
