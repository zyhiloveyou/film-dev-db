#!/bin/bash
# Fetch all Massive Dev Chart data via r.jina.ai (renders JS, bypasses Cloudflare).
# One request per film-select option value (exact names + wildcard prefixes).
set -u
OUT=/Users/zyh/Documents/harness/film-dev-db/sources/mdc_raw
mkdir -p "$OUT"
PROXY=http://127.0.0.1:7897
LOG=/Users/zyh/Documents/harness/film-dev-db/fetch_mdc.log

# Build option list (all non-empty values, exact as in the HTML, URL-encoded via python)
python3 - "$OUT" <<'PYEOF'
import html, json, os, re, sys, urllib.parse
raw = open('/tmp/mdc_main.html').read()
m = re.search(r'<select name="Film".*?</select>', raw, re.S)
vals = [v for v in re.findall(r'<option[^>]*value="([^"]*)"', m.group(0)) if v]
os.makedirs(sys.argv[1], exist_ok=True)
open('/tmp/mdc_queries.txt','w').write('\n'.join(vals))
print("options:", len(vals))
PYEOF

fetch_one() {
  local q="$1" idx="$2"
  local enc slug
  enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$q")
  slug=$(python3 -c "import re,sys; s=sys.argv[1]; s=re.sub(r'[^A-Za-z0-9]+','-',s).strip('-').lower(); print(s[:80])" "$q")
  local f="$OUT/${idx}_${slug}.md"
  [ -s "$f" ] && return 0
  for try in 1 2 3; do
    curl -s -x "$PROXY" --max-time 120 -H "x-no-cache: true" \
      "https://r.jina.ai/https://www.digitaltruth.com/devchart.php?Film=${enc}&Developer=&mdc=Search&TempUnits=C&TimeUnits=D" \
      -o "$f.tmp"
    if [ -s "$f.tmp" ] && grep -q '^|' "$f.tmp"; then
      mv "$f.tmp" "$f"
      echo "OK $idx $q ($(grep -c '^|' "$f") rows)" >> "$LOG"
      return 0
    fi
    echo "RETRY $try $idx $q" >> "$LOG"
    sleep 8
  done
  rm -f "$f.tmp"
  echo "FAIL $idx $q" >> "$LOG"
  return 1
}

i=0
while IFS= read -r q; do
  i=$((i+1))
  fetch_one "$q" "$i"
  sleep 3
done < /tmp/mdc_queries.txt
echo "DONE total=$i" >> "$LOG"
