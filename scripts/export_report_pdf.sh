#!/bin/sh
# Print landing/report.html to a PDF for submissions. Opens every "왜 이렇게 했나" answer first,
# since a closed <details> prints as a question without its answer. Needs a server on port 8765
# (the "landing" entry in .claude/launch.json) and Google Chrome.
set -e
cd "$(dirname "$0")/.."
out="${1:-docs/submission/report.pdf}"
sed 's/<details>/<details open>/g' landing/report.html > landing/_print.html
trap 'rm -f landing/_print.html' EXIT
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=10000 --print-to-pdf="$PWD/$out" "http://localhost:8765/_print.html" 2>/dev/null
echo "wrote $out"
