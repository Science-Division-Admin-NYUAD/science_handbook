#!/usr/bin/env python3
"""
Build the editable Division of Science handbook website.

The source of truth is the Markdown in content/*.md. The PDF in assets/ is kept
as a reference download, but the website itself is real text that can be edited,
linked, styled, and republished from these content files.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import markdown
import yaml


ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
SITE = ROOT / "site"
CSS = ASSETS / "css" / "site.css"
PDF = ASSETS / "handbook.pdf"
IMAGES = ASSETS / "images"

SITE_TITLE = "Division of Science - New Joiners Handbook"

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FENCE_OPEN_RE = re.compile(r"^:::\s+(?P<classes>[\w\- ]+?)\s*$")
FENCE_CLOSE_RE = re.compile(r"^:::\s*$")


def split_front_matter(text: str) -> tuple[dict, str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    return meta, text[match.end():]


def expand_fences(md_text: str) -> str:
    out: list[str] = []
    stack: list[str] = []
    for line in md_text.splitlines():
        opened = FENCE_OPEN_RE.match(line)
        if opened:
            classes = opened.group("classes").strip()
            stack.append(classes)
            out.append(f'<div class="{classes}" markdown="1">')
            continue
        if FENCE_CLOSE_RE.match(line) and stack:
            stack.pop()
            out.append("</div>")
            continue
        out.append(line)
    while stack:
        stack.pop()
        out.append("</div>")
    return "\n".join(out)


def render_markdown(body: str) -> tuple[str, list[dict[str, str]]]:
    md = markdown.Markdown(
        extensions=["extra", "md_in_html", "sane_lists", "toc"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
        output_format="html5",
    )
    html = md.convert(expand_fences(body))
    subsections = [{"id": token["id"], "name": token["name"]} for token in md.toc_tokens]
    return html, subsections


def load_sections() -> list[dict]:
    sections = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("order", 999)
        meta.setdefault("slug", path.stem)
        meta["source"] = path.name
        meta["html"], meta["subsections"] = render_markdown(body)
        sections.append(meta)
    return sorted(sections, key=lambda item: item["order"])


def nav_items(sections: list[dict]) -> list[dict]:
    return [section for section in sections if not section.get("cover")]


def page_filename(section: dict) -> str:
    return "index.html" if section.get("cover") else f"{section['slug']}.html"


def render_header(nav: list[dict], active_slug: str | None) -> str:
    links = "\n".join(
        f'''        <a href="{section['slug']}.html"{" class=\"active\"" if section["slug"] == active_slug else ""}>{section.get("nav_label") or section["title"]}</a>'''
        for section in nav
    )
    return f"""  <header class="topbar">
    <nav class="main-nav" aria-label="Main sections">
{links}
    </nav>
    <a class="download" href="handbook.pdf" download>Download PDF</a>
  </header>
"""


def render_cover(section: dict, nav: list[dict]) -> str:
    contents = "\n".join(render_contents_row(item) for item in nav)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{SITE_TITLE}</title>
  <link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
{render_header(nav, None)}
  <main class="cover">
    <section class="cover-hero" aria-labelledby="cover-title">
      <img src="assets/images/cover-page.jpg" alt="" aria-hidden="true">
      <h1 id="cover-title" class="sr-only">Welcome to the Division of Science: A handbook for new joiners</h1>
    </section>
    <section class="contents-page" aria-label="Contents">
      <div class="pdf-rule" aria-hidden="true"></div>
      <h2>Contents</h2>
{contents}
    </section>
  </main>
</body>
</html>
"""


def render_contents_row(section: dict) -> str:
    image = f"assets/images/contents-{section['slug']}.jpg"
    topics = "\n".join(
        f'''            <li><span>{topic[0]}</span><span>{topic[1]:02}</span></li>'''
        for topic in section.get("toc", [])
    )
    return f"""      <a class="contents-row" href="{section['slug']}.html">
        <img src="{image}" alt="">
        <div class="contents-copy">
          <h3>{section['title']}</h3>
          <ul>
{topics}
          </ul>
        </div>
      </a>"""


def render_topic_list(section: dict, limit: int | None = None) -> str:
    topics = section.get("toc", [])
    if limit:
        topics = topics[:limit]
    if not topics:
        return ""
    items = "\n".join(f"          <li>{topic[0]}</li>" for topic in topics)
    return f"""        <ul class="topic-list">
{items}
        </ul>"""


def render_section(section: dict, nav: list[dict]) -> str:
    toc = "\n".join(
        f'''      <a href="#{item['id']}">{item['name']}</a>'''
        for item in section.get("subsections", [])
        if item["name"] != section["title"]
    )
    toc_block = f"""    <aside class="page-toc" aria-label="On this page">
      <p>Section topics</p>
{toc}
    </aside>
""" if toc else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{section['title']} - Division of Science</title>
  <link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
{render_header(nav, section['slug'])}
  <main class="page-shell">
    <section class="page-title section-hero">
      <p class="eyebrow">Division of Science</p>
      <h1>{section['title']}</h1>
      {render_topic_list(section)}
    </section>
    <div class="content-layout">
{toc_block}
      <article class="article">
{section['html']}
      </article>
    </div>
  </main>
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
    sections = load_sections()
    nav = nav_items(sections)
    cover = next((section for section in sections if section.get("cover")), None)

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets" / "css").mkdir(parents=True)
    shutil.copy2(CSS, SITE / "assets" / "css" / "site.css")
    if IMAGES.exists():
        shutil.copytree(IMAGES, SITE / "assets" / "images")
    if PDF.exists():
        shutil.copy2(PDF, SITE / "handbook.pdf")

    for section in sections:
        html = render_cover(section, nav) if section.get("cover") else render_section(section, nav)
        (SITE / page_filename(section)).write_text(html, encoding="utf-8")
    (SITE / "404.html").write_text(render_redirect(), encoding="utf-8")

    print(f"  site: {len(sections)} pages -> {SITE}")
    if PDF.exists():
        print(f"  pdf : {SITE / 'handbook.pdf'}")


if __name__ == "__main__":
    build_site()
