#!/usr/bin/env python3
"""
Build the Division of Science "New Joiners Handbook" as:
  1. A static website  -> site/*.html   (deployed to GitHub Pages)
  2. A print-ready PDF  -> site/handbook.pdf (generated with WeasyPrint)

Both outputs are generated from the SAME Markdown sources in content/ and the
SAME brand stylesheet in assets/css/handbook.css, so the website and the PDF
stay in sync automatically.

Usage:
    python build.py            # build site + PDF
    python build.py --no-pdf   # build site only (fast; skips WeasyPrint)
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
TEMPLATES = ROOT / "templates"
SITE = ROOT / "site"

SITE_TITLE = "Division of Science — New Joiners Handbook"
PDF_NAME = "handbook.pdf"

# GitHub repo + workflow used for the build-status badge on the website.
REPO = "Science-Division-Admin-NYUAD/science_handbook"
WORKFLOW_FILE = "build.yml"
BADGE_IMG = f"https://github.com/{REPO}/actions/workflows/{WORKFLOW_FILE}/badge.svg"
BADGE_LINK = f"https://github.com/{REPO}/actions/workflows/{WORKFLOW_FILE}"

# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# A line that opens a container block:  ::: classnames
FENCE_OPEN_RE = re.compile(r"^:::\s+(?P<classes>[\w\- ]+?)\s*$")
# A line that closes the most recent container block:  :::
FENCE_CLOSE_RE = re.compile(r"^:::\s*$")


def split_front_matter(text: str):
    """Return (metadata dict, body markdown)."""
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return meta, body


def expand_fences(md_text: str) -> str:
    """Convert `::: classes ... :::` blocks into <div class="classes"> wrappers.

    Nesting is supported via a simple stack. `md_in_html` lets Markdown keep
    parsing the content inside the div (thanks to markdown="1").
    """
    out, stack = [], []
    for line in md_text.splitlines():
        mo = FENCE_OPEN_RE.match(line)
        if mo:
            classes = mo.group("classes").strip()
            stack.append(classes)
            out.append(f'<div class="{classes}" markdown="1">')
            continue
        if FENCE_CLOSE_RE.match(line) and stack:
            stack.pop()
            out.append("</div>")
            continue
        out.append(line)
    # close any accidentally-open blocks
    while stack:
        stack.pop()
        out.append("</div>")
    return "\n".join(out)


def render_markdown(body: str) -> str:
    body = expand_fences(body)
    md = markdown.Markdown(
        extensions=[
            "extra",         # tables, fenced code, attr_list, def lists...
            "md_in_html",    # parse markdown inside our <div> wrappers
            "sane_lists",
            "smarty",        # curly quotes / dashes, like the print original
        ],
        output_format="html5",
    )
    return md.convert(body)


# ---------------------------------------------------------------------------
# Load content
# ---------------------------------------------------------------------------

def load_sections():
    sections = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("order", 999)
        meta.setdefault("slug", path.stem)
        meta["html"] = render_markdown(body)
        meta["source"] = path.name
        sections.append(meta)
    sections.sort(key=lambda s: s["order"])
    return sections


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def jinja_env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )


def build_site(sections):
    env = jinja_env()
    page_tpl = env.get_template("page.html.j2")

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    shutil.copytree(ASSETS, SITE / "assets")

    # nav = every non-cover section
    nav = [s for s in sections if not s.get("cover")]
    cover = next((s for s in sections if s.get("cover")), None)

    for s in sections:
        target = "index.html" if s.get("cover") else f"{s['slug']}.html"
        html = page_tpl.render(
            site_title=SITE_TITLE,
            page=s,
            nav=nav,
            cover=cover,
            pdf_name=PDF_NAME,
            badge_img=BADGE_IMG,
            badge_link=BADGE_LINK,
            mode="screen",
        )
        (SITE / target).write_text(html, encoding="utf-8")
    print(f"  site: {len(sections)} pages -> {SITE}")


def build_pdf(sections):
    from weasyprint import HTML  # imported lazily so --no-pdf needs no wheel

    env = jinja_env()
    print_tpl = env.get_template("print.html.j2")
    html = print_tpl.render(site_title=SITE_TITLE, sections=sections)
    # Render relative to SITE so assets/ resolves for both HTML and PDF.
    out = SITE / PDF_NAME
    HTML(string=html, base_url=str(SITE)).write_pdf(str(out))
    print(f"  pdf : {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true", help="skip PDF generation")
    args = ap.parse_args()

    sections = load_sections()
    build_site(sections)
    if not args.no_pdf:
        build_pdf(sections)
    print("Done.")


if __name__ == "__main__":
    main()
