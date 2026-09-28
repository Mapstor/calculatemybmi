#!/usr/bin/env bash
# IndexNow submission for calculatemybmi.net. bash 3.2-safe (macOS default).
#
# Usage:
#   ./scripts/indexnow.sh                       submits every URL in sitemap.xml
#   ./scripts/indexnow.sh URL [URL ...]         submits the URLs you list
#   ./scripts/indexnow.sh --dry-run [URL ...]   prints the JSON body, does not POST
#
# No mapfile / readarray, no associative arrays, no ${var,,}/${var^^},
# no |& or &>>. Sitemap is parsed with sed + a plain while-read loop.
set -eu

KEY="acf3e63101ea3e40cc6b21d22b435929"
HOST="calculatemybmi.net"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

DRY_RUN=0
if [ $# -gt 0 ] && [ "$1" = "--dry-run" ]; then
  DRY_RUN=1
  shift
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITEMAP="${SCRIPT_DIR}/../sitemap.xml"

# URL list is a newline-delimited string; append with add_url.
URLS=""
add_url() {
  u="$1"
  # strip leading/trailing whitespace
  u="$(printf '%s' "$u" | sed -e 's/^ *//' -e 's/ *$//')"
  [ -z "$u" ] && return 0
  if [ -z "$URLS" ]; then
    URLS="$u"
  else
    URLS="$URLS
$u"
  fi
}

if [ $# -gt 0 ]; then
  for u in "$@"; do
    add_url "$u"
  done
else
  if [ ! -f "$SITEMAP" ]; then
    echo "sitemap.xml not found at $SITEMAP" >&2
    exit 1
  fi
  # Extract every <loc>...</loc> to a temp file, then read back.
  TMP="/tmp/indexnow_urls.$$"
  sed -n 's|.*<loc>\([^<]*\)</loc>.*|\1|p' "$SITEMAP" > "$TMP"
  while IFS= read -r line; do
    add_url "$line"
  done < "$TMP"
  rm -f "$TMP"
fi

if [ -z "$URLS" ]; then
  echo "No URLs to submit." >&2
  exit 1
fi

# Build JSON body via python3 — portable, no brittle shell quoting.
# python3 reads URLs on stdin, host/key/keyLocation from argv.
JSON="$(printf '%s\n' "$URLS" | python3 -c 'import sys, json; host, key, key_loc = sys.argv[1], sys.argv[2], sys.argv[3]; urls = [u for u in sys.stdin.read().splitlines() if u.strip()]; print(json.dumps({"host": host, "key": key, "keyLocation": key_loc, "urlList": urls}))' "$HOST" "$KEY" "$KEY_LOCATION")"

# Count URLs portably.
N="$(printf '%s\n' "$URLS" | grep -c .)"

if [ "$DRY_RUN" = "1" ]; then
  echo "URL count: $N"
  echo "JSON body:"
  echo "$JSON"
  exit 0
fi

echo "POSTing $N URLs to IndexNow..."
curl -sSf -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-raw "$JSON" \
  -w "\nHTTP %{http_code}\n"
