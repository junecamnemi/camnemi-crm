#!/bin/bash
# Parallel runner for missing-bypass batches using --query-file (avoids arg-list-too-long).
cd /c/Users/USER/camnemi-crm
export PROMPT_FILE=backend/_bypass_prompt.md
export OUTDIR="$LOCALAPPDATA/Temp/bypass_mis"
mkdir -p "$OUTDIR"

run_one() {
  f="$1"; base=$(basename "$f" .json)
  out="$OUTDIR/${base}_out.txt"
  if [ -f "$out" ] && [ -s "$out" ] && [ "$(wc -c < "$out")" -gt 500 ]; then echo "skip $base"; return; fi
  q="$OUTDIR/${base}_query.txt"
  cat "$PROMPT_FILE" "$f" > "$q"
  timeout 1200 hermes chat --query-file "$q" -m "deepseek/deepseek-v4-pro-0813" --provider nous -t file > "$out" 2>&1
  echo "done $base ($(wc -c < "$out")b)"
}
export -f run_one
ls backend/_bypass_mis_batches/mis_*.json | xargs -P 4 -I{} bash -c 'run_one "$@"' _ {}
echo "ALL DONE"
