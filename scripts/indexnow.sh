#!/usr/bin/env bash
# IndexNow submission for calculatemybmi.net.
# Usage: ./scripts/indexnow.sh
# Do not commit if you regenerate the key — the {key}.txt file at site root must match.
set -euo pipefail

KEY="acf3e63101ea3e40cc6b21d22b435929"
HOST="calculatemybmi.net"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

# Changed URLs in the P0 recovery batch. Edit this list per submission.
URLS=(
  "https://calculatemybmi.net/"
  "https://calculatemybmi.net/women-bmi-calculator/"
  "https://calculatemybmi.net/men-bmi-calculator/"
  "https://calculatemybmi.net/age-bmi-calculator/"
  "https://calculatemybmi.net/kids-bmi-calculator/"
  "https://calculatemybmi.net/ideal-weight/"
  "https://calculatemybmi.net/lean-body-mass/"
  "https://calculatemybmi.net/new-bmi-calculator/"
  "https://calculatemybmi.net/blog/"
  "https://calculatemybmi.net/blog/bmi-chart-women/"
  "https://calculatemybmi.net/blog/bmi-chart-men/"
  "https://calculatemybmi.net/blog/bmi-by-age/"
  "https://calculatemybmi.net/blog/bmi-categories/"
  "https://calculatemybmi.net/blog/bmi-formula/"
  "https://calculatemybmi.net/blog/healthy-bmi-range/"
  "https://calculatemybmi.net/blog/body-fat-vs-bmi/"
  "https://calculatemybmi.net/blog/bmi-and-metabolism/"
  "https://calculatemybmi.net/blog/bmi-and-health-risks/"
  "https://calculatemybmi.net/blog/how-to-lower-bmi/"
  "https://calculatemybmi.net/blog/what-is-bmi/"
  "https://calculatemybmi.net/blog/bmi-chart-explained/"
  "https://calculatemybmi.net/blog/bmi-for-athletes/"
  "https://calculatemybmi.net/blog/bmi-tracking-guide/"
  "https://calculatemybmi.net/blog/waist-to-height-ratio/"
  "https://calculatemybmi.net/blog/underweight-bmi-risks/"
  "https://calculatemybmi.net/blog/bmi-limitations/"
  "https://calculatemybmi.net/calculators/"
  "https://calculatemybmi.net/about/"
  "https://calculatemybmi.net/contact/"
)

# Build JSON payload
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
