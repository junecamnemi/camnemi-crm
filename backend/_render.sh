#!/bin/bash
# usage: render.sh <outfile_abspath> <url>
CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
UDD="C:/Users/USER/AppData/Local/Temp/chrome_udd_r"
mkdir -p "$UDD"
"$CHROME" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --user-data-dir="$UDD" --virtual-time-budget=12000 --run-all-compositor-stages-before-draw \
  --print-to-pdf="$1" "$2" 2>/dev/null
echo "render_exit=$? out=$1"
