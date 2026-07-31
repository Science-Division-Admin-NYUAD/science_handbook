#!/usr/bin/env python3
"""
Build the editable Division of Science handbook website.

The source of truth is the Markdown in content/*.md. The website and downloadable
PDF are both generated from those same files, so edits stay in sync.
"""

from __future__ import annotations

import os
import re
import shutil
import html
from pathlib import Path

import markdown
import yaml
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
SITE = ROOT / "site"
CSS = ASSETS / "css" / "site.css"
IMAGES = ASSETS / "images"
PDF_OUTPUT = SITE / "handbook.pdf"

SITE_TITLE = "Division of Science - New Joiners Handbook"
STYLE_VERSION = "20260728-mail-option-2"

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
FENCE_OPEN_RE = re.compile(r"^:::\s+(?P<classes>[\w\- ]+?)\s*$")
FENCE_CLOSE_RE = re.compile(r"^:::\s*$")
EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![\w-])")
INTRANET_URL = "https://intranet.nyuad.nyu.edu/"
INTRANET_RE = re.compile(r"(?<![\w-])((?:NYUAD\s+)?Intranet)(?![\w-])", re.IGNORECASE)

class ExternalLinkTargetTreeprocessor(Treeprocessor):
    def run(self, root):
        for link in root.iter("a"):
            href = link.get("href", "")
            if not href.startswith(("http://", "https://")):
                continue
            link.set("target", "_blank")
            rel_values = set((link.get("rel") or "").split())
            rel_values.update({"noopener", "noreferrer"})
            link.set("rel", " ".join(sorted(rel_values)))
        return root


class ExternalLinkTargetExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(
            ExternalLinkTargetTreeprocessor(md),
            "external_link_targets",
            15,
        )


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


def link_email_addresses(html_text: str) -> str:
    parts = re.split(r"(<[^>]+>)", html_text)
    linked: list[str] = []
    in_anchor = False

    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            tag = part.lower()
            if re.match(r"<a\b", tag):
                in_anchor = True
            elif re.match(r"</a\s*>", tag):
                in_anchor = False
            linked.append(part)
            continue

        if in_anchor:
            linked.append(part)
            continue

        linked.append(
            EMAIL_RE.sub(
                lambda match: (
                    f'<a class="email-copy" href="mailto:{match.group(1)}" '
                    f'data-email="{match.group(1)}" '
                    f'aria-label="Copy email address {match.group(1)}">{match.group(1)}</a>'
                ),
                part,
            )
        )

    return "".join(linked)


def link_intranet_mentions(html_text: str) -> str:
    parts = re.split(r"(<[^>]+>)", html_text)
    linked: list[str] = []
    in_anchor = False
    in_heading = False

    for part in parts:
        if part.startswith("<") and part.endswith(">"):
            tag = part.lower()
            if re.match(r"<a\b", tag):
                in_anchor = True
            elif re.match(r"</a\s*>", tag):
                in_anchor = False
            elif re.match(r"<h[1-6]\b", tag):
                in_heading = True
            elif re.match(r"</h[1-6]\s*>", tag):
                in_heading = False
            linked.append(part)
            continue

        if in_anchor or in_heading:
            linked.append(part)
            continue

        linked.append(
            INTRANET_RE.sub(
                lambda match: (
                    f'<a href="{INTRANET_URL}" target="_blank" '
                    f'rel="noopener noreferrer">{match.group(1)}</a>'
                ),
                part,
            )
        )

    return "".join(linked)


def render_markdown(body: str) -> tuple[str, list[dict[str, str]], list[dict]]:
    md = markdown.Markdown(
        extensions=["extra", "md_in_html", "sane_lists", "toc", ExternalLinkTargetExtension()],
        extension_configs={"toc": {"toc_depth": "2-3"}},
        output_format="html5",
    )
    html = link_intranet_mentions(link_email_addresses(md.convert(expand_fences(body))))
    toc_tree = clean_toc_tokens(md.toc_tokens)
    subsections = flatten_toc_tokens(toc_tree)
    return html, subsections, toc_tree


def clean_toc_tokens(tokens: list[dict]) -> list[dict]:
    return [
        {
            "id": token["id"],
            "name": token["name"],
            "children": clean_toc_tokens(token.get("children", [])),
        }
        for token in tokens
    ]


def flatten_toc_tokens(tokens: list[dict]) -> list[dict[str, str]]:
    items = []
    for token in tokens:
        items.append({"id": token["id"], "name": token["name"]})
        items.extend(flatten_toc_tokens(token.get("children", [])))
    return items


def load_sections() -> list[dict]:
    sections = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("order", 999)
        meta.setdefault("slug", path.stem)
        meta["source"] = path.name
        meta["html"], meta["subsections"], meta["toc_tree"] = render_markdown(body)
        sections.append(meta)
    return sorted(sections, key=lambda item: item["order"])


def nav_items(sections: list[dict]) -> list[dict]:
    return [section for section in sections if not section.get("cover")]


def page_filename(section: dict) -> str:
    return "index.html" if section.get("cover") else f"{section['slug']}.html"


def render_header(nav: list[dict], active_slug: str | None) -> str:
    contents_class = ' class="active"' if active_slug is None else ""
    contents_link = f'''        <a href="index.html"{contents_class}>Contents</a>'''
    section_links = "\n".join(
        f'''        <a href="{section['slug']}.html"{' class="active"' if section["slug"] == active_slug else ""}>{section.get("nav_label") or section["title"]}</a>'''
        for section in nav
    )
    links = "\n".join([contents_link, section_links])
    return f"""  <header class="topbar">
    <input class="menu-toggle" type="checkbox" id="main-menu-toggle" aria-hidden="true">
    <label class="menu-button" for="main-menu-toggle" aria-label="Open main menu">
      <span></span>
      <span></span>
      <span></span>
    </label>
    <nav class="main-nav" aria-label="Main sections">
{links}
    </nav>
    <a class="download" href="handbook.pdf" download>Prefer a PDF? Download it here</a>
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
  <link rel="stylesheet" href="assets/css/site.css?v={STYLE_VERSION}">
</head>
<body>
{render_header(nav, None)}
  <main class="cover">
    <section class="cover-hero" aria-labelledby="cover-title">
      <img src="assets/images/cover-page.jpg?v={STYLE_VERSION}" alt="" aria-hidden="true">
      <div class="cover-title-panel">
        <h1 id="cover-title">Welcome to the Division of Science</h1>
        <p>A handbook for new joiners</p>
      </div>
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
    contents_title = section.get("contents_title") or section["title"]
    topics = "\n".join(
        f'''            <li{topic_class_attr(topic)}><span>{topic[0]}</span><span>{topic[1]:02}</span></li>'''
        for topic in section.get("toc", [])
    )
    return f"""      <a class="contents-row" href="{section['slug']}.html">
        <img src="{image}" alt="">
        <div class="contents-copy">
          <h3>{contents_title}</h3>
          <ul>
{topics}
          </ul>
        </div>
      </a>"""


def topic_anchor_lookup(section: dict) -> dict[str, str]:
    return {
        normalize_heading(item["name"]): item["id"]
        for item in section.get("subsections", [])
    }


def render_topic_list(section: dict, limit: int | None = None) -> str:
    topics = section.get("toc", [])
    if limit:
        topics = topics[:limit]
    if not topics:
        return ""
    anchors = topic_anchor_lookup(section)
    items = []
    for topic in topics:
        label = topic[0]
        anchor = anchors.get(normalize_heading(label))
        label_html = f'<a href="#{anchor}">{label}</a>' if anchor else label
        items.append(f"          <li{topic_class_attr(topic)}>{label_html}</li>")
    items_html = "\n".join(items)
    return f"""        <ul class="topic-list">
{items_html}
        </ul>"""


def normalize_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(text).lower()).strip()


def topic_class_name(topic: list) -> str:
    if len(topic) < 3:
        return ""
    kind = re.sub(r"[^a-z0-9_-]+", "-", str(topic[2]).lower()).strip("-")
    return f"topic-{kind}" if kind else ""


def topic_class_attr(topic: list) -> str:
    class_name = topic_class_name(topic)
    return f' class="{class_name}"' if class_name else ""


def render_section_topic_links(section: dict) -> str:
    subsection_ids = topic_anchor_lookup(section)
    heading_tree = topic_heading_tree_lookup(section)
    subtopic_labels = subtopic_display_label_lookup(section)
    groups = []
    for topic in section.get("toc", []):
        if topic_class_name(topic) == "topic-subtopic":
            continue
        label = topic[0]
        anchor = subsection_ids.get(normalize_heading(label))
        if not anchor:
            continue
        children = heading_tree.get(normalize_heading(label), {}).get("children", [])
        subtopic_links = "\n".join(
            f'''        <a class="toc-subtopic" href="#{html.escape(child["id"], quote=True)}">{html.escape(subtopic_labels.get(normalize_heading(child["name"]), html.unescape(child["name"])))}</a>'''
            for child in children
        )
        has_subtopics = bool(subtopic_links)
        expanded_attr = ' aria-expanded="false"' if has_subtopics else ""
        subtopics = f"""
      <div class="toc-subtopics">
{subtopic_links}
      </div>""" if has_subtopics else ""
        groups.append(f'''      <div class="toc-group">
        <a class="toc-main" href="#{html.escape(anchor, quote=True)}"{expanded_attr}>{html.escape(label)}</a>{subtopics}
      </div>''')
    return "\n".join(groups)


def topic_heading_tree_lookup(section: dict) -> dict[str, dict]:
    return {
        normalize_heading(item["name"]): item
        for item in section.get("toc_tree", [])
    }


def subtopic_display_label_lookup(section: dict) -> dict[str, str]:
    return {
        normalize_heading(topic[0]): str(topic[3])
        for topic in section.get("toc", [])
        if topic_class_name(topic) == "topic-subtopic" and len(topic) >= 4
    }


def render_section_title(section: dict) -> str:
    lines = section.get("title_lines")
    if lines:
        line_html = "\n".join(
            f'        <span class="title-line">{html.escape(str(line))}</span>'
            for line in lines
        )
        return f"""      <h1 class="stacked-title">
{line_html}
      </h1>"""
    return f"      <h1>{html.escape(section['title'])}</h1>"


def render_active_topic_script(enabled: bool) -> str:
    if not enabled:
        return ""
    return """  <script>
    (() => {
      const headings = Array.from(document.querySelectorAll(".article h2[id], .article h3[id]"));
      const links = Array.from(document.querySelectorAll('.page-toc a[href^="#"], .topic-list a[href^="#"]'));
      const groups = Array.from(document.querySelectorAll(".page-toc .toc-group"));
      if (!headings.length || !links.length) return;
      const manuallyClosed = new Set();
      let lockedTarget = "";
      let releaseTimer = 0;

      const groupedLinks = new Map();
      links.forEach((link) => {
        const id = decodeURIComponent(link.hash.slice(1));
        if (!groupedLinks.has(id)) groupedLinks.set(id, []);
        groupedLinks.get(id).push(link);
      });

      const groupKey = (group) => {
        const mainLink = group && group.querySelector(".toc-main[href]");
        return mainLink ? decodeURIComponent(mainLink.hash.slice(1)) : "";
      };

      const setGroupExpanded = (group, expanded) => {
        if (!group) return;
        group.classList.toggle("is-expanded", expanded);
        const toggle = group.querySelector(".toc-main[aria-expanded]");
        if (toggle) toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      };

      const setActive = (id) => {
        links.forEach((link) => {
          link.classList.remove("is-active");
          link.removeAttribute("aria-current");
        });
        groups.forEach((group) => {
          setGroupExpanded(group, false);
        });

        const activeLinks = groupedLinks.get(id) || [];
        activeLinks.forEach((link) => {
          link.classList.add("is-active");
          link.setAttribute("aria-current", "true");
        });

        const sidebarLink = activeLinks.find((link) => link.closest(".page-toc"));
        const activeGroup = sidebarLink && sidebarLink.closest(".toc-group");
        if (activeGroup && !manuallyClosed.has(groupKey(activeGroup))) {
          setGroupExpanded(activeGroup, true);
        }
      };

      const currentHeadingId = () => {
        const marker = window.scrollY + 120;
        let active = headings[0].id;
        headings.forEach((heading) => {
          if (heading.offsetTop <= marker) active = heading.id;
        });
        return active;
      };

      let ticking = false;
      const update = () => {
        setActive(lockedTarget || currentHeadingId());
        ticking = false;
      };

      window.addEventListener("scroll", () => {
        if (lockedTarget) {
          window.clearTimeout(releaseTimer);
          releaseTimer = window.setTimeout(() => {
            lockedTarget = "";
            update();
          }, 180);
        }
        if (!ticking) {
          window.requestAnimationFrame(update);
          ticking = true;
        }
      }, { passive: true });
      window.addEventListener("resize", update);
      links.forEach((link) => {
        link.addEventListener("click", (event) => {
          const id = decodeURIComponent(link.hash.slice(1));
          const sidebarGroup = link.closest(".page-toc .toc-group");
          const isMainToggle = link.classList.contains("toc-main") && link.hasAttribute("aria-expanded");

          if (isMainToggle && sidebarGroup && sidebarGroup.classList.contains("is-expanded")) {
            event.preventDefault();
            lockedTarget = "";
            window.clearTimeout(releaseTimer);
            manuallyClosed.add(groupKey(sidebarGroup));
            setGroupExpanded(sidebarGroup, false);
            link.classList.add("is-active");
            link.setAttribute("aria-current", "true");
            return;
          }

          if (sidebarGroup) manuallyClosed.delete(groupKey(sidebarGroup));
          lockedTarget = id;
          window.clearTimeout(releaseTimer);
          releaseTimer = window.setTimeout(() => {
            lockedTarget = "";
            update();
          }, 900);
          setActive(id);
        });
      });

      if (window.location.hash) {
        setActive(decodeURIComponent(window.location.hash.slice(1)));
      }
      update();
    })();
  </script>
"""


def render_email_copy_script() -> str:
    return """  <script>
    (() => {
      const emailLinks = Array.from(document.querySelectorAll(".email-copy[data-email]"));
      if (!emailLinks.length) return;

      const toast = document.createElement("div");
      toast.className = "copy-toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);

      let toastTimer = 0;

      const fallbackCopy = (text) => {
        const field = document.createElement("textarea");
        field.value = text;
        field.setAttribute("readonly", "");
        field.style.position = "fixed";
        field.style.left = "-9999px";
        document.body.appendChild(field);
        field.select();
        document.execCommand("copy");
        field.remove();
      };

      const copyText = async (text) => {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text);
          return;
        }
        fallbackCopy(text);
      };

      const showToast = (link) => {
        const rect = link.getBoundingClientRect();
        toast.textContent = "Copied";
        toast.classList.add("is-visible");

        const left = Math.min(
          window.innerWidth - toast.offsetWidth - 12,
          Math.max(12, rect.left + rect.width / 2 - toast.offsetWidth / 2)
        );
        const top = Math.max(12, rect.top - toast.offsetHeight - 8);
        toast.style.left = `${left}px`;
        toast.style.top = `${top}px`;

        window.clearTimeout(toastTimer);
        toastTimer = window.setTimeout(() => {
          toast.classList.remove("is-visible");
        }, 1200);
      };

      document.querySelectorAll(".program-card").forEach((card) => {
        const cardEmails = Array.from(card.querySelectorAll(".email-copy[data-email]"));
        const emails = cardEmails.map((link) => link.dataset.email).filter(Boolean);
        if (emails.length < 2) return;

        card.classList.add("has-copy-all");
        const title = card.querySelector("h4")?.textContent?.trim() || "this program";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "copy-all-emails";
        button.title = `Copy all email addresses for ${title}`;
        button.setAttribute("aria-label", `Copy all email addresses for ${title}`);
        button.addEventListener("click", async () => {
          try {
            await copyText(emails.join("\\n"));
            showToast(button);
          } catch {
            return;
          }
        });
        card.appendChild(button);
      });

      emailLinks.forEach((link) => {
        link.addEventListener("click", async (event) => {
          event.preventDefault();
          const email = link.dataset.email || link.textContent.trim();
          try {
            await copyText(email);
            showToast(link);
          } catch {
            window.location.href = link.href;
          }
        });
      });
    })();
  </script>
"""


def render_section(section: dict, nav: list[dict]) -> str:
    toc = render_section_topic_links(section)
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
  <link rel="stylesheet" href="assets/css/site.css?v={STYLE_VERSION}">
</head>
<body>
{render_header(nav, section['slug'])}
  <main class="page-shell">
    <section class="page-title section-hero">
{render_section_title(section)}
      {render_topic_list(section)}
    </section>
    <div class="content-layout">
{toc_block}
      <article class="article">
{section['html']}
      </article>
    </div>
  </main>
{render_active_topic_script(bool(toc))}
{render_email_copy_script()}
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


def render_pdf_html(sections: list[dict], nav: list[dict]) -> str:
    site_css = CSS.read_text(encoding="utf-8")
    contents = "\n".join(render_contents_row(item) for item in nav)
    section_blocks = "\n".join(
        f"""  <main class="page-shell pdf-section">
    <section class="page-title section-hero">
{render_section_title(section)}
    </section>
    <div class="content-layout">
      <article class="article">
{section['html']}
      </article>
    </div>
  </main>"""
        for section in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{SITE_TITLE}</title>
  <style>
{site_css}

    @page {{
      size: A4;
      margin: 10mm;
      @bottom-right {{
        content: counter(page);
        color: #6f6475;
        font-size: 8pt;
      }}
    }}

    body {{
      margin: 0;
      background: #fff;
    }}

    .topbar,
    .download,
    .page-toc,
    .topic-list,
    .copy-toast,
    .copy-all-emails {{
      display: none !important;
    }}

    .cover {{
      width: 100%;
      max-width: none;
      margin: 0;
      padding: 0;
      background: #fff;
    }}

    .pdf-cover-page {{
      page-break-after: always;
    }}

    .cover-hero {{
      min-height: 150mm;
      margin: 0 0 10mm;
      page-break-inside: avoid;
    }}

    .contents-page {{
      width: 100%;
      max-width: none;
      margin: 0;
      padding: 0;
      border: 0;
      box-shadow: none;
      page-break-before: always;
    }}

    .contents-row {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .pdf-section {{
      width: 100%;
      max-width: none;
      margin: 0;
      padding: 0;
      page-break-before: always;
      background: #fff;
    }}

    .page-title {{
      width: 100%;
      max-width: none;
      min-height: 44mm;
      margin: 0 0 8mm;
      padding: 14mm 12mm;
      border-radius: 0;
      page-break-after: avoid;
    }}

    .page-title h1 {{
      font-size: 28pt;
    }}

    .content-layout {{
      display: block;
      width: 100%;
      max-width: none;
      margin: 0;
    }}

    .article {{
      width: 100%;
      max-width: none;
      padding: 12mm;
      border-top: 2pt solid var(--teal);
      box-shadow: none;
      background: #fff;
      page-break-before: avoid;
    }}

    .article h2,
    .article h3,
    .article h4 {{
      page-break-after: avoid;
    }}

    .cards,
    .people-grid,
    .program-row,
    .card,
    .person,
    .dean-feature,
    .campus-essential,
    .quote,
    .note {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .program-heads {{
      display: block;
    }}

    .program-row {{
      grid-template-columns: 42px repeat(2, minmax(0, 1fr));
      margin-bottom: 10px;
    }}

    .dean-feature {{
      grid-template-columns: 120px minmax(0, 1fr);
    }}

    .dean-photo-frame {{
      width: 120px;
    }}

    .email-copy::after {{
      display: none;
    }}

    .campus-essentials {{
      border-top: 1px solid rgba(75, 54, 92, 0.2);
    }}

    .campus-essential {{
      grid-template-columns: 34px minmax(110px, 0.3fr) minmax(0, 1fr);
    }}

    @media print {{
      .article h2 {{
        font-size: 22pt;
      }}
    }}
  </style>
</head>
<body>
  <main class="cover pdf-cover-page">
    <section class="cover-hero" aria-labelledby="cover-title">
      <img src="assets/images/cover-page.jpg?v={STYLE_VERSION}" alt="" aria-hidden="true">
      <div class="cover-title-panel">
        <h1 id="cover-title">Welcome to the Division of Science</h1>
        <p>A handbook for new joiners</p>
      </div>
    </section>
    <section class="contents-page" aria-label="Contents">
      <div class="pdf-rule" aria-hidden="true"></div>
      <h2>Contents</h2>
{contents}
    </section>
  </main>
{section_blocks}
</body>
</html>
"""


def build_pdf(sections: list[dict], nav: list[dict]) -> None:
    try:
        from weasyprint import HTML

        HTML(string=render_pdf_html(sections, nav), base_url=str(SITE)).write_pdf(PDF_OUTPUT)
        return
    except Exception as error:
        message = (
            "The styled PDF generator could not run. "
            "No fallback PDF was created, because fallback PDFs do not match the website."
        )
        if os.environ.get("CI"):
            raise RuntimeError(message) from error
        print(f"  pdf : {message} ({error.__class__.__name__})")


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

    for section in sections:
        html = render_cover(section, nav) if section.get("cover") else render_section(section, nav)
        (SITE / page_filename(section)).write_text(html, encoding="utf-8")
    (SITE / "404.html").write_text(render_redirect(), encoding="utf-8")
    (SITE / "handbook-print.html").write_text(render_pdf_html(sections, nav), encoding="utf-8")
    build_pdf(sections, nav)

    print(f"  site: {len(sections)} pages -> {SITE}")
    if PDF_OUTPUT.exists():
        print(f"  pdf : {PDF_OUTPUT}")
    else:
        print("  pdf : not generated locally")


if __name__ == "__main__":
    build_site()
