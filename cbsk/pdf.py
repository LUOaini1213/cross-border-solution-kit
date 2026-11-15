"""Markdown -> HTML (pandoc) -> PDF (headless Chromium via Playwright). Optional: the build skips the PDF
with a message when either tool is missing, and the tests do not depend on it."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CSS = Path(__file__).resolve().parent / "assets" / "proposal.css"
PANDOC_FALLBACK = r"D:\ProgramData\anaconda3\Library\bin\pandoc.exe"


def find_pandoc() -> str | None:
    for cand in (os.environ.get("PANDOC"), shutil.which("pandoc"), PANDOC_FALLBACK):
        if cand and Path(cand).exists():
            return cand
    return None


def markdown_to_html(markdown: str, title: str) -> str:
    pandoc = find_pandoc()
    if pandoc is None:
        raise RuntimeError("pandoc not found (set PANDOC or put pandoc on PATH)")
    proc = subprocess.run([pandoc, "-f", "gfm", "-t", "html5", "--standalone", "--metadata", f"pagetitle={title}",
                           f"--include-in-header={CSS}"], input=markdown.encode("utf-8"), capture_output=True, check=True)
    return proc.stdout.decode("utf-8")


def html_to_pdf(html: str, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright  # optional dependency
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "proposal.html"
        src.write_text(html, encoding="utf-8", newline="\n")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(src.as_uri(), wait_until="load")
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                page.pdf(path=str(pdf_path), format="A4", print_background=True,
                         margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
                         display_header_footer=True, header_template="<span></span>",
                         footer_template='<div style="font-size:7pt;width:100%;text-align:center;color:#667">'
                                         '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
            finally:
                browser.close()


def build_pdf(md_en: str, md_zh: str, title: str, pdf_path: Path) -> str:
    """Combined bilingual PDF (English, then Chinese on a new page). Returns a status message."""
    try:
        html = markdown_to_html(md_en + '\n\n<div class="pagebreak"></div>\n\n' + md_zh, title)
        html_to_pdf(html, pdf_path)
        return f"wrote {pdf_path.name}"
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"PDF skipped ({type(exc).__name__}: {exc})"
