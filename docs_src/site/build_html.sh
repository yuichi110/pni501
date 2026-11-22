#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${DRAWLIB_CMD:-}" ]; then
    if [ -f "uv.lock" ] && command -v uv &> /dev/null && uv run drawlib --version &> /dev/null; then
        DRAWLIB_CMD="uv run drawlib"
    elif command -v drawlib &> /dev/null; then
        DRAWLIB_CMD="drawlib"
    elif python3 -m drawlib --version &> /dev/null; then
        DRAWLIB_CMD="python3 -m drawlib"
    elif command -v uvx &> /dev/null; then
        DRAWLIB_CMD="uvx drawlib"
    else
        DRAWLIB_CMD="drawlib"
    fi
fi

echo "Building HTML site (docs_src/site/ -> docs/)..."
$DRAWLIB_CMD build html docs_src/site/ -o docs/
echo "www.pni501.com" > docs/CNAME
touch docs/.nojekyll
python3 "$REPO_ROOT/docs_src/inject_banner.py" "$REPO_ROOT/docs"
echo "HTML site build complete: docs/"
