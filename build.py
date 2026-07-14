#!/usr/bin/env python3
"""
Build the Division of Science handbook website from the official PDF.

The website is intentionally a faithful PDF viewer: each visible page is a
rendered image of the June 2025 handbook PDF, and the download link points to
the same source PDF. This keeps the website from drifting away from the PDF.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
PDF = ASSETS / "handbook.pdf"
PAGES = ASSETS / "pdf-pages"
SITE = ROOT / "site"

def page_files() -> list[Path]:
    pages = sorted(PAGES.glob("page-*.jpg"))
    if not pages:
        raise SystemExit("No rendered PDF pages found in assets/pdf-pages.")
    return pages


def render_index(pages: list[Path]) -> str:
    page_count = len(pages)
    page_markup = "\n".join(
        f'''      <section class="pdf-page" id="page-{i}">
        <div class="page-label">Page {i} of {page_count}</div>
        <img src="assets/pdf-pages/{page.name}" alt="Handbook page {i}">
      </section>'''
        for i, page in enumerate(pages, 1)
    )
    jump_links = "\n".join(
        f'        <a href="#page-{i}">{i}</a>' for i in range(1, page_count + 1)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Division of Science - New Joiners Handbook</title>
  <style>
    :root {{
      --teal: #0091b3;
      --ink: #1f2933;
      --muted: #697386;
      --page: #ffffff;
      --bg: #eef3f6;
      --rule: #d9e2e8;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.4;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 12px 20px;
      background: var(--teal);
      color: white;
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.18);
    }}
    .title {{
      min-width: 0;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    .actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
    }}
    .actions a {{
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 7px 12px;
      border-radius: 4px;
      background: white;
      color: #007a95;
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
    }}
    .viewer {{
      width: min(100%, 1060px);
      margin: 0 auto;
      padding: 24px 18px 42px;
    }}
    .page-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 0 auto 22px;
      padding: 12px;
      background: var(--page);
      border: 1px solid var(--rule);
    }}
    .page-nav a {{
      width: 32px;
      height: 30px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: var(--teal);
      border: 1px solid var(--rule);
      border-radius: 3px;
      font-size: 12px;
      font-weight: 700;
      text-decoration: none;
    }}
    .pdf-page {{
      margin: 0 auto 28px;
      background: var(--page);
      box-shadow: 0 2px 14px rgba(20, 35, 45, 0.18);
    }}
    .page-label {{
      padding: 8px 12px;
      color: var(--muted);
      border-bottom: 1px solid var(--rule);
      font-size: 12px;
      font-weight: 700;
    }}
    .pdf-page img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .footer {{
      padding: 22px;
      color: var(--muted);
      text-align: center;
      font-size: 13px;
    }}
    @media (max-width: 640px) {{
      .topbar {{
        align-items: flex-start;
        flex-direction: column;
      }}
      .actions {{
        width: 100%;
      }}
      .actions a {{
        width: 100%;
        justify-content: center;
      }}
      .viewer {{
        padding-inline: 8px;
      }}
    }}
    @media print {{
      body {{ background: white; }}
      .topbar, .page-nav, .page-label, .footer {{ display: none; }}
      .viewer {{ width: 100%; padding: 0; }}
      .pdf-page {{
        margin: 0;
        box-shadow: none;
        page-break-after: always;
      }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="title">Division of Science - New Joiners Handbook</div>
    <div class="actions">
      <a href="handbook.pdf" download>Download PDF</a>
    </div>
  </header>
  <main class="viewer">
    <nav class="page-nav" aria-label="PDF pages">
{jump_links}
    </nav>
{page_markup}
  </main>
  <footer class="footer">Division of Science - New Joiners Handbook</footer>
</body>
</html>
"""


def render_redirect() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=index.html">
  <title>Redirecting</title>
</head>
<body>
  <p><a href="index.html">Open the handbook</a></p>
</body>
</html>
"""


def build_site() -> None:
    pages = page_files()
    if not PDF.exists():
        raise SystemExit("Missing assets/handbook.pdf.")

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets" / "pdf-pages").mkdir(parents=True)

    shutil.copy2(PDF, SITE / "handbook.pdf")
    for page in pages:
        shutil.copy2(page, SITE / "assets" / "pdf-pages" / page.name)

    (SITE / "index.html").write_text(render_index(pages), encoding="utf-8")
    (SITE / "404.html").write_text(render_redirect(), encoding="utf-8")

    print(f"  site: {len(pages)} PDF pages -> {SITE}")
    print(f"  pdf : {SITE / 'handbook.pdf'}")


if __name__ == "__main__":
    build_site()
