#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ -z "${PNI_CMD:-}" ]; then
    if [ -f "uv.lock" ] && command -v uv &> /dev/null; then
        PNI_CMD="uv run pni"
        DRAWLIB_CMD="uv run drawlib"
    else
        PNI_CMD="pni"
        DRAWLIB_CMD="drawlib"
    fi
else
    DRAWLIB_CMD="${DRAWLIB_CMD:-drawlib}"
fi

echo "=== 1. Building Official Site (docs_src/site/ -> docs/) ==="
"$SCRIPT_DIR/site/build_html.sh"

echo "=== 2. Building Sample Reports (docs_src/reports/* -> docs/reports/*) ==="
if [ -d "docs_src/reports" ]; then
    for report_dir in docs_src/reports/*/; do
        [ -f "${report_dir}drawlib.toml" ] || continue
        slug="$(basename "$report_dir")"
        echo "  -> Compiling report '${slug}' (HTML + PDF)..."
        $PNI_CMD report build "$slug" \
            --src-dir "docs_src/reports/${slug}" \
            --output-dir "docs/reports/${slug}" \
            --html-output-dir "docs/reports/${slug}" \
            --link-check-root "docs" \
            -f pdf -f html
    done
fi

echo "=== 3. Verifying Portal Links (docs/) ==="
$DRAWLIB_CMD serve docs/ --check

echo "All portal builds and link checks passed!"
