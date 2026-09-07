#!/bin/bash
declare -A U=(
[신경주대]="http://korean.gu.ac.kr/"
[신라대]="https://skli.silla.ac.kr/"
[신한대]="https://www.shinhan.ac.kr/kr/281/subview.do"
[아신대]="https://www.acts.ac.kr/design/contents10.asp?code=15151115&left=acts6_2"
[아주대]="http://www.ajou.ac.kr/iadmissions/korean/course.do"
[안양대]="https://www.anyang.ac.kr/main/academic/international-exchange.do"
[연세대]="https://www.yskli.com/course.php?mid=K01_02"
[영남대]="https://www.yu.ac.kr/kli/index.do"
[영남신학대]="http://langytus.tcubemnet.com/content/38"
[영산대]="https://klec.ysu.ac.kr/"
[예원예술대]="https://www.yewon.ac.kr/main/?menu=495"
[용인대]="https://language.yongin.ac.kr/"
[우석대]="http://www.woosuk.ac.kr/main/?menu=161"
)
for k in "${!U[@]}"; do
  url="${U[$k]}"
  out="${k}.html"
  code=$(curl -skL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36" --max-time 40 -o "$out" -w "%{http_code}|%{content_type}|%{size_download}" "$url" 2>/dev/null)
  echo "[$k] url=$url -> $code"
done
