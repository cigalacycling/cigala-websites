#!/bin/bash
# Fetch every page in retail/baseline-live-pages.json from an unpublished theme preview (curl keeps the preview cookie),
# then parse them with tools/parse_pages.py. Usage: tools/crawl_preview.sh THEME_ID OUTDIR
THEME=$1; OUT=$2; mkdir -p "$OUT/html"; JAR="$OUT/jar"
ROOT=$(cd "$(dirname "$0")/.." && pwd)
jq -r '.[].url' "$ROOT/retail/baseline-live-pages.json" > "$OUT/urls.txt"
i=0
while read -r u; do
  i=$((i+1)); f="$OUT/html/$(printf %04d $i).html"
  [ -s "$f" ] && continue
  sep='?'; [[ $u == *\?* ]] && sep='&'
  for t in 1 2 3 4; do
    code=$(curl -sSL -c "$JAR" -b "$JAR" -o "$f.tmp" -w "%{http_code}" "${u}${sep}preview_theme_id=${THEME}")
    [ "$code" = "429" ] && { sleep $((t*15)); continue; }
    break
  done
  echo "$u $code" >> "$OUT/status.txt"; mv "$f.tmp" "$f"; sleep 1
done < "$OUT/urls.txt"
echo done $i
