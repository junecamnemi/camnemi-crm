#!/bin/bash
# usage: pdf.sh out.pdf URL
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --user-data-dir="$LOCALAPPDATA/Temp/chrome_pdf_$$" \
  --print-to-pdf="$(cygpath -w "$1")" "$2" 2>/dev/null
rm -rf "$LOCALAPPDATA/Temp/chrome_pdf_$$"
