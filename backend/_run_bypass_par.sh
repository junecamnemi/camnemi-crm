#!/bin/bash
# Parallel runner: process bypass batches 01-16 through pro model, 4 concurrent.
cd /c/Users/USER/camnemi-crm
export PROMPT_FILE=backend/_bypass_prompt.md
export OUTDIR="$LOCALAPPDATA/Temp/bypass_pro"
mkdir -p "$OUTDIR"

run_one() {
  f="$1"
  base=$(basename "$f" .json)
  out="$OUTDIR/${base}_out.txt"
  if [ -f "$out" ] && [ -s "$out" ]; then echo "skip $base"; return; fi
  PROMPT="$(cat "$PROMPT_FILE")$(cat "$f")"
  timeout 1200 hermes chat -q "$PROMPT" -m "deepseek/deepseek-v4-pro-0813" --provider nous -t file > "$out" 2>&1
  echo "done $base ($(wc -c < "$out")b)"
}
export -f run_one

ls backend/_bypass_batches/bypass_*.json | grep -vE "bypass_00" | xargs -P 4 -I{} bash -c 'run_one "$@"' _ {}
echo "ALL DONE"
