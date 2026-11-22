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
    else
        DRAWLIB_CMD="drawlib"
    fi
fi

echo "Extracting standalone diagram images (docs_src/site/ -> docs_images/)..."
$DRAWLIB_CMD build image docs_src/site/ -o docs_images/
echo "Image extraction complete: docs_images/"
