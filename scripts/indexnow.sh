#!/usr/bin/env bash
# IndexNow submission for calculatemybmi.net.
# Usage:
#   ./scripts/indexnow.sh                    -> submits every URL in sitemap.xml
#   ./scripts/indexnow.sh URL [URL ...]      -> submits the URLs you list
set -euo pipefail

KEY="acf3e63101ea3e40cc6b21d22b435929"
HOST="calculatemybmi.net"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

if [ $# -gt 0 ]; then
  URLS=("$@")
else
  # Pull URLs from sitemap.xml (grep <loc>...</loc>)
  mapfile -t URLS < <(grep -oE '<loc>[^<]+</loc>' "$(dirname "$0")/../sitemap.xml" | sed -E 's,</?loc>,,g')
fi

if [ ${#URLS[@]} -eq 0 ]; then
  echo "No URLs to submit." >&2
  exit 1
fi

URL_LIST=$(printf '"%s",' "${URLS[@]}")
URL_LIST="[${URL_LIST%,}]"
JSON=$(cat <<EOF
{"host":"${HOST}","key":"${KEY}","keyLocation":"${KEY_LOCATION}","urlList":${URL_LIST}}
EOF
)

echo "POSTing ${#URLS[@]} URLs to IndexNow..."
curl -sSf -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$JSON" \
  -w "\nHTTP %{http_code}\n"
