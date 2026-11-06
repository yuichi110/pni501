#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "api_spring_clean_src" = "." ]; then
    cd "$SCRIPT_DIR"
else
    PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
    cd "$PARENT_DIR"
fi

if [ -z "${DRAWLIB_CMD:-}" ]; then
    if ( [ -f "uv.lock" ] || [ -f "../uv.lock" ] || [ -f "../../uv.lock" ] ) && command -v uv &> /dev/null && uv run drawlib --version &> /dev/null; then
        DRAWLIB_CMD="uv run drawlib"
    elif command -v drawlib &> /dev/null; then
        DRAWLIB_CMD="drawlib"
    elif python3 -m drawlib --version &> /dev/null; then
        DRAWLIB_CMD="python3 -m drawlib"
    elif python -m drawlib --version &> /dev/null; then
        DRAWLIB_CMD="python -m drawlib"
    elif command -v uv &> /dev/null && uv run drawlib --version &> /dev/null; then
        DRAWLIB_CMD="uv run drawlib"
    elif command -v uvx &> /dev/null; then
        DRAWLIB_CMD="uvx drawlib"
    else
        DRAWLIB_CMD="drawlib"
    fi
fi

if [ ! -d "api_spring_clean_html" ]; then
    echo "Output directory 'api_spring_clean_html' does not exist. Running build_html.sh first..."
    "$SCRIPT_DIR/build_html.sh"
fi

echo "Starting local preview server on http://localhost:8000 ..."
$DRAWLIB_CMD serve api_spring_clean_html/
