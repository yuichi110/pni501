# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Post-build top navigation banner (.demo-banner) injector for www.pni501.com portals.

Mirrors the Drawlib official portal banner so every page across the main documentation
site (`docs/{en,ja}/`) and every published sample report (`docs/reports/<slug>/`) shares
a compact, scalable top navigation bar linking directly to the User Guide, Sample Reports
Gallery, 55-Language Matrix, Release Notes, per-report PDF, PyPI, and GitHub.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CSS_MARKER = "/* PNI501 Official Top Banner */"

BANNER_CSS = """/* PNI501 Official Top Banner */
:root {
    --demo-banner-h: 38px;
}

html {
    scroll-padding-top: 52px;
}

.demo-banner {
    position: sticky;
    top: 0;
    z-index: 1050;
    min-height: var(--demo-banner-h);
    background: #0f172a;
    color: #f8fafc;
    border-bottom: 1px solid #334155;
    font-family: var(--rtd-font, "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
    font-size: 0.76rem;
    line-height: 1.4;
    padding: 0.38rem 1rem;
    display: flex;
    align-items: center;
}

.demo-banner-inner {
    width: 100%;
    max-width: 1440px;
    margin: 0 auto;
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.35rem 0.65rem;
}

.demo-banner-badge {
    display: inline-block;
    background: #4f46e5;
    color: #ffffff;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 0.12rem 0.44rem;
    border-radius: 4px;
    flex-shrink: 0;
}

.demo-banner-text {
    flex: 1 1 auto;
    min-width: 0;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.demo-banner code {
    background: rgba(255, 255, 255, 0.12);
    color: #f8fafc;
    padding: 0.06rem 0.3rem;
    border-radius: 4px;
    font-size: 0.82em;
}

.demo-banner a {
    color: #a5b4fc;
    font-weight: 600;
    text-decoration: none;
}

.demo-banner a:hover {
    color: #e0e7ff;
    text-decoration: underline;
}

.demo-banner-links {
    display: inline-flex;
    flex-wrap: nowrap;
    flex-shrink: 0;
    align-items: center;
    gap: 0.18rem 0.32rem;
}

.demo-banner-links a,
.demo-banner-links strong {
    white-space: nowrap;
}

.demo-banner-links strong {
    color: #ffffff;
}

.demo-banner-sep {
    color: #64748b;
}

@media (max-width: 1100px) {
    .demo-banner-text {
        display: none;
    }
}

@media (min-width: 769px) {
    .sidebar {
        top: var(--demo-banner-h);
        height: calc(100vh - var(--demo-banner-h));
    }
}

@media (max-width: 768px) {
    .demo-banner {
        position: static;
        padding: 0.5rem 1rem;
    }

    .demo-banner-inner {
        flex-wrap: wrap;
    }

    .demo-banner-text {
        display: inline;
        white-space: normal;
        overflow: visible;
    }

    .demo-banner-links {
        flex-wrap: wrap;
    }

    body:has(.sidebar) .demo-banner {
        margin-top: 60px;
    }

    body:has(.sidebar) .content-wrapper {
        margin-top: 0;
    }
}

@media print {
    .demo-banner {
        display: none !important;
    }
}
"""

_META_REFRESH_RE = re.compile(r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE)
_HTML_LANG_RE = re.compile(r'<html\b[^>]*\blang=["\']([^"\']+)["\']', re.IGNORECASE)
_BODY_OPEN_RE = re.compile(r"(<body\b[^>]*>)\r?\n?", re.IGNORECASE)
_EXISTING_BANNER_RE = re.compile(
    r'[ \t]*<div class="demo-banner"[\s\S]*?</div>\s*</div>\r?\n?',
)


def detect_portal_context(rel_parts: tuple[str, ...]) -> tuple[str, str | None]:
    """Identify the active portal section and optional report slug for an HTML page."""
    if not rel_parts:
        return "user_guide", None
    if rel_parts[0] == "reports" and len(rel_parts) >= 2:
        return "report", rel_parts[1]
    joined = "/".join(rel_parts)
    if joined.endswith("04_scoring_and_reports/sample_reports.html"):
        return "sample_reports", None
    if joined.endswith("05_languages_and_reference/supported_languages.html"):
        return "languages", None
    if joined.endswith("01_getting_started/release_notes.html"):
        return "release_notes", None
    return "user_guide", None


def should_skip_html(html_path: Path, content: str) -> bool:
    """Return True if the HTML file should not receive a top navigation banner."""
    if html_path.name == "404.html":
        return True
    if _META_REFRESH_RE.search(content):
        return True
    return not bool(_BODY_OPEN_RE.search(content))


def is_japanese_html(content: str) -> bool:
    """Return True if the document declares a Japanese locale in <html lang=...>."""
    match = _HTML_LANG_RE.search(content)
    return bool(match and match.group(1).strip().lower().startswith("ja"))


def _banner_text(portal_id: str, report_slug: str | None, is_ja: bool) -> str:
    """Return localized descriptive caption for the top banner."""
    if portal_id == "report" and report_slug:
        if is_ja:
            return f"Workflow v2 サンプルレポート（<code>{report_slug}</code>）— PNI501 &amp; Drawlib"
        return f"Live Workflow v2 Sample Report (<code>{report_slug}</code>) — PNI501 &amp; Drawlib"
    if portal_id == "sample_reports":
        if is_ja:
            return "Workflow v2 ライブ・サンプルレポートギャラリー（HTML / A4 PDF / SARIF）"
        return "Live Workflow v2 Sample Reports Gallery (HTML / A4 PDF / SARIF)"
    if portal_id == "languages":
        if is_ja:
            return "対応 55 言語ネイティブ Tree-sitter CST マトリクス（<code>v0.2.0</code>）"
        return "55-Language Native Tree-sitter CST Matrix (<code>v0.2.0</code>)"
    if portal_id == "release_notes":
        if is_ja:
            return "リリースノート・変更履歴（<code>v0.2.0</code>）"
        return "Release History &amp; Changelog (<code>v0.2.0</code>)"
    if is_ja:
        return "Drawlib で構築された PNI501 公式ドキュメント（<code>v0.2.0</code>）"
    return "Official Documentation (<code>v0.2.0</code>) built with Drawlib"


def render_banner_html(
    portal_id: str,
    report_slug: str | None,
    is_ja: bool,
    rel_parts: tuple[str, ...],
    docs_root: Path,
) -> str:
    """Render the .demo-banner HTML block for a specific HTML page under docs/."""
    lang = "ja" if is_ja else "en"
    rel_to_docs = "../" * (len(rel_parts) - 1)
    banner_text = _banner_text(portal_id, report_slug, is_ja)

    nav_items: list[tuple[str, str, str]] = [
        (
            "user_guide",
            "User Guide",
            f"{rel_to_docs}ja/index.html" if is_ja else f"{rel_to_docs}en/index.html",
        ),
        (
            "sample_reports",
            "Sample Reports",
            f"{rel_to_docs}{lang}/04_scoring_and_reports/sample_reports.html",
        ),
        (
            "languages",
            "55 Languages",
            f"{rel_to_docs}{lang}/05_languages_and_reference/supported_languages.html",
        ),
        (
            "release_notes",
            "Release Notes",
            f"{rel_to_docs}{lang}/01_getting_started/release_notes.html",
        ),
    ]

    link_items: list[str] = []
    for pid, label, href in nav_items:
        if pid == portal_id:
            link_items.append(f"<strong>{label}</strong>")
        else:
            link_items.append(f'<a href="{href}">{label}</a>')

    if portal_id == "report" and report_slug:
        lang_pdf = f"reports/{report_slug}/{report_slug}_{lang}.pdf"
        default_pdf = f"reports/{report_slug}/{report_slug}.pdf"
        if (docs_root / lang_pdf).is_file():
            link_items.append(f'<a href="{rel_to_docs}{lang_pdf}">PDF ({lang.upper()})</a>')
        elif (docs_root / default_pdf).is_file():
            link_items.append(f'<a href="{rel_to_docs}{default_pdf}">PDF</a>')

    link_items.append(
        '<a href="https://pypi.org/project/pni501/" target="_blank" rel="noopener noreferrer">PyPI ↗</a>'
    )
    link_items.append(
        '<a href="https://github.com/yuichi110/pni501" target="_blank" rel="noopener noreferrer">GitHub ↗</a>'
    )

    sep = '\n                <span class="demo-banner-sep">·</span>\n                '
    joined_links = sep.join(link_items)

    return (
        '    <div class="demo-banner" role="region" aria-label="Portal Navigation">\n'
        '        <div class="demo-banner-inner">\n'
        '            <span class="demo-banner-badge">PNI501 OFFICIAL</span>\n'
        '            <span class="demo-banner-text">\n'
        f"                {banner_text}\n"
        "            </span>\n"
        '            <span class="demo-banner-links">\n'
        f"                {joined_links}\n"
        "            </span>\n"
        "        </div>\n"
        "    </div>\n"
    )


def inject_banner_into_html(html_path: Path, docs_root: Path) -> bool:
    """Idempotently inject or refresh .demo-banner inside an HTML file."""
    content = html_path.read_text(encoding="utf-8")
    if should_skip_html(html_path, content):
        return False

    rel_parts = html_path.relative_to(docs_root).parts
    portal_id, report_slug = detect_portal_context(rel_parts)
    is_ja = is_japanese_html(content)
    banner_html = render_banner_html(portal_id, report_slug, is_ja, rel_parts, docs_root)

    if _EXISTING_BANNER_RE.search(content):
        updated = _EXISTING_BANNER_RE.sub(banner_html, content, count=1)
    else:
        updated = _BODY_OPEN_RE.sub(rf"\g<1>\n{banner_html}", content, count=1)

    if updated != content:
        html_path.write_text(updated, encoding="utf-8")
    return True


def inject_banner_into_css(css_path: Path) -> bool:
    """Idempotently append or refresh .demo-banner rules in a style.css file."""
    content = css_path.read_text(encoding="utf-8")
    css_block = BANNER_CSS.strip() + "\n"
    if CSS_MARKER in content:
        prefix = content.split(CSS_MARKER, maxsplit=1)[0].rstrip()
        updated = f"{prefix}\n\n{css_block}"
    else:
        updated = f"{content.rstrip()}\n\n{css_block}"

    if updated != content:
        css_path.write_text(updated, encoding="utf-8")
    return True


def inject_portal_banners(docs_root: Path) -> tuple[int, int]:
    """Inject .demo-banner HTML and CSS across all pages and reports under docs_root."""
    if not docs_root.exists():
        return 0, 0

    html_count = 0
    for html_path in sorted(docs_root.rglob("*.html")):
        if inject_banner_into_html(html_path, docs_root):
            html_count += 1

    css_count = 0
    for css_path in sorted(docs_root.rglob("style.css")):
        if inject_banner_into_css(css_path):
            css_count += 1

    return html_count, css_count


def main() -> None:
    """CLI entrypoint for injecting top portal banners into docs/."""
    docs_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "docs"
    html_count, css_count = inject_portal_banners(docs_root)
    print(f"Injected PNI501 portal banner into {html_count} HTML file(s) and {css_count} style.css file(s) in {docs_root.name}/.")


if __name__ == "__main__":
    main()
