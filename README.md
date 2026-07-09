# Division of Science — New Joiners Handbook

[![Build handbook (site + PDF)](https://github.com/Science-Division-Admin-NYUAD/science_handbook/actions/workflows/build.yml/badge.svg)](https://github.com/Science-Division-Admin-NYUAD/science_handbook/actions/workflows/build.yml)

The badge above shows the status of the most recent build: **green** means the website and PDF built and published successfully, **red** means the last build failed (click it to see why).

This repository holds the **NYU Abu Dhabi Division of Science "New Joiners Handbook"**.

The handbook is written once, in plain text files, and is automatically turned into **two things**:

1. **A website** — published with GitHub Pages.
2. **A PDF** — a print-ready copy that looks like the original booklet. A **Download PDF** link appears on every page of the website.

You never edit the website or the PDF directly. You edit the text files, and a robot (a "GitHub Action") rebuilds both for you every time a change is approved.

---

## Table of contents

- [Who this guide is for](#who-this-guide-is-for)
- [How the whole thing works (the big picture)](#how-the-whole-thing-works-the-big-picture)
- [Part 1 — Create a GitHub account](#part-1--create-a-github-account)
- [Part 2 — The easy way to edit (in your web browser)](#part-2--the-easy-way-to-edit-in-your-web-browser)
- [Part 3 — A worked example: making a real edit](#part-3--a-worked-example-making-a-real-edit)
- [Part 4 — How the automatic build & publish works](#part-4--how-the-automatic-build--publish-works)
- [Part 5 — The full local setup (clone, commit, push)](#part-5--the-full-local-setup-clone-commit-push)
- [Part 6 — Writing content: the formatting cheat sheet](#part-6--writing-content-the-formatting-cheat-sheet)
- [What's in this repository](#whats-in-this-repository)
- [Getting help](#getting-help)

---

## Who this guide is for

You. Even if you have **never used GitHub, never written a line of code, and have never heard of "Markdown"**, this guide will get you editing the handbook safely. Read it top to bottom the first time. After that you'll only need Parts 2–3 for day-to-day edits.

A few words you'll see a lot:

| Word | Plain-English meaning |
|------|----------------------|
| **Repository** (or "repo") | The folder that holds all the handbook's files. You're looking at it now. |
| **Markdown** | A simple way of writing text where you use symbols like `#` for a heading. That's it. |
| **Commit** | Saving a change, with a short note describing what you changed. |
| **Branch** | A safe, separate copy of the files where you make changes without affecting the live handbook. |
| **Pull Request** (or "PR") | Asking for your changes to be reviewed and added to the live handbook. |
| **GitHub Action** | The robot that automatically rebuilds the website and PDF. |

---

## How the whole thing works (the big picture)

```
        You edit these                    A robot builds these
   ┌────────────────────────┐        ┌──────────────────────────────┐
   │  content/*.md           │        │  A website (GitHub Pages)     │
   │  (the handbook text,    │  ───▶  │  A handbook.pdf (download)    │
   │   written in Markdown)  │        │                               │
   └────────────────────────┘        └──────────────────────────────┘
             ▲                                      ▲
             │ you change the words                 │ happens automatically
             │                                      │ every time a change is
        (Parts 2–5)                                 │ approved (Part 4)
```

The words of the handbook live in the **`content/`** folder as `.md` (Markdown) files — one file per major section. The look (colours, fonts, the teal cover, the section dividers) is handled for you by a stylesheet, so you only ever deal with words.

---

## Part 1 — Create a GitHub account

*(Skip this if you already have a GitHub account and access to this repository.)*

1. Go to **https://github.com** and click **Sign up**.
2. Enter your **email address** (use your `@nyu.edu` email), a **password**, and a **username** (for example `jdoe-nyuad`).
3. Solve the puzzle to prove you're human, then click **Create account**.
4. GitHub will email you a **code**. Type it in to verify your email.
5. When asked about a plan, the **Free** plan is all you need.
6. Finally, **tell the handbook's maintainer your GitHub username** and ask them to invite you to this repository. You'll receive an email invitation — click **Accept**. Without this step you can read the handbook but not edit it.

> **Tip:** Turn on two-factor authentication (GitHub → Settings → Password and authentication) — NYU security policies generally require it.

---

## Part 2 — The easy way to edit (in your web browser)

For small text changes (fixing a typo, updating an email address, changing a paragraph) you do **not** need to install anything. You can do it all on the GitHub website.

1. Open this repository on **github.com**.
2. Click the **`content`** folder.
3. Click the file for the section you want to change — for example **`10-welcome.md`** for "Welcome to the Division". *(The number at the start just controls the order of sections.)*
4. Click the **pencil ✏️ icon** (top right of the file) — "Edit this file".
5. Make your change in the text box.
6. Scroll to the bottom to the **"Commit changes"** box:
   - In the first line, write a short description, e.g. *"Fix Dean's email address"*.
   - Choose **"Create a new branch for this commit and start a pull request."** (This keeps the live handbook safe.)
   - Click **Propose changes**, then on the next screen click **Create pull request**.
7. That's it. The maintainer will review and approve it, and the website and PDF update automatically.

Continue to Part 3 for a full worked example.

---

## Part 3 — A worked example: making a real edit

Let's say **a new administrator, "Sara Ahmed", joins and we need to add her to "Meet Your Administrators."**

**Step 1 — Find the right place.** Administrators are in the "Welcome to the Division" section, so open **`content/10-welcome.md`** and scroll to the `## Meet Your Administrators` heading.

**Step 2 — Look at how an existing person is written.** Each person is a small block that looks like this:

```markdown
::: person
#### Holly Spence
Administrative Coordinator
<span class="email">hs4100@nyu.edu</span>
:::
```

- `::: person` and the closing `:::` mark the start and end of one person's card. **Always keep them as a matching pair.**
- `#### Holly Spence` is the person's **name** (the four `#` symbols make it the name style).
- The next line is their **title**.
- The `<span class="email">…</span>` line makes the email address show in the brand colour.

**Step 3 — Add the new person.** Copy an existing block and change the details. Put it just before the final `:::` that closes the whole grid:

```markdown
::: person
#### Sara Ahmed
Administrative Coordinator
<span class="email">sa9999@nyu.edu</span>
:::
```

**Step 4 — Save it.** In the browser, use the **Commit changes** box (Part 2, step 6) with a message like *"Add Sara Ahmed to administrators"*. If you're working locally, see Part 5.

**Step 5 — Done.** Once your Pull Request is approved, Sara automatically appears on both the website and in the PDF. You did not touch any design or code.

> **The golden rule:** every `:::` that opens a block must have a matching `:::` that closes it. If something looks broken after your edit, a missing `:::` is the usual cause.

---

## Part 4 — How the automatic build & publish works

You don't run anything by hand. A GitHub Action (defined in `.github/workflows/build.yml`) does it for you:

- **When you open a Pull Request**, the robot builds the website *and* the PDF to make sure your change doesn't break anything. If you see a green ✅ next to your PR, all is well. A red ❌ means something needs fixing — click **Details** to see what.
- **When your Pull Request is merged into the `main` branch**, the robot rebuilds everything and **publishes the website to GitHub Pages**. The PDF is rebuilt at the same time and lives at `…/handbook.pdf`, which is what the **Download PDF** button links to.

**Where is the live website?** After the first successful publish, the address is shown under **Settings → Pages** in the repository (it looks like `https://<org-or-username>.github.io/<repo-name>/`). You may need a maintainer to switch Pages on once: **Settings → Pages → Build and deployment → Source → GitHub Actions.**

**Roughly how long?** A couple of minutes after a PR is merged. Watch progress in the **Actions** tab.

You can also download the built PDF from any PR: open the **Actions** run for your PR and look under **Artifacts** for **`handbook-pdf`**.

---

## Part 5 — The full local setup (clone, commit, push)

Use this if you prefer to edit on your own computer, or you're making larger changes and want to preview them before proposing them. If the browser method in Part 2 covers your needs, you can skip this part.

### Option A (recommended for beginners): GitHub Desktop — no typing commands

1. Download **GitHub Desktop** from https://desktop.github.com and install it.
2. Open it and **sign in** with your GitHub account.
3. Go to **File → Clone repository**, pick this repository from the list, choose a folder on your computer, and click **Clone**. ("Cloning" just means downloading your own copy.)
4. In the top bar, click **Current branch → New branch**, name it something like `update-dean-note`, and click **Create branch**. *(Always make a branch; never edit `main` directly.)*
5. Click **"Open in your editor"** (or just open the files in the cloned folder) and edit the `.md` files in `content/`.
6. Back in GitHub Desktop you'll see your changes listed. At the bottom left, type a short **Summary** (your commit message) and click **Commit to `update-dean-note`**.
7. Click **Push origin** (top bar) to upload your commit.
8. Click **Create Pull Request** — this opens your browser to finish. Then follow Part 2, step 6–7.

### Option B: the command line (Git)

First install Git from https://git-scm.com/downloads. Then, in a terminal (PowerShell on Windows, Terminal on Mac):

```bash
# 1. Clone (download) the repository — do this once.
git clone https://github.com/<org-or-username>/<repo-name>.git
cd <repo-name>

# 2. Make a new branch for your change (never edit main directly).
git checkout -b update-dean-note

# 3. …edit files in the content/ folder with any text editor…

# 4. See what you changed.
git status

# 5. Stage and commit your changes with a short message.
git add .
git commit -m "Update the Dean's welcome note"

# 6. Push your branch up to GitHub.
git push -u origin update-dean-note
```

The `git push` command prints a link — open it to create your Pull Request, then follow Part 2, steps 6–7.

### Previewing on your computer (optional)

If you want to see the website and PDF before proposing changes:

```bash
# One-time: install the build tools (needs Python 3).
pip install -r requirements.txt

# Build the website only (fast) — open site/index.html in your browser.
python build.py --no-pdf

# Build the website AND the PDF (site/handbook.pdf).
python build.py
```

Building the **PDF** locally needs a few extra system libraries used by WeasyPrint. On most machines the website preview (`--no-pdf`) is enough — the PDF is always built correctly by the robot anyway. (If you do want local PDFs: on macOS `brew install pango`, on Ubuntu `sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0`.)

---

## Part 6 — Writing content: the formatting cheat sheet

Everything in `content/*.md` is **Markdown**. Here is everything you need.

### Headings (these control the look, so use the right level)

```markdown
## Teaching                 → big teal section title
### Academic Programs       → bold teal sub-heading (ALL CAPS look)
#### Foundations of Science → smaller teal heading
##### Welcome to the Division → the small label at the very top of a section
```

### Everyday text

```markdown
Normal paragraph text — just type it.

**bold text**   and   *italic text*

A bulleted list:
- first item
- second item

A numbered list:
1. first step
2. second step

A link: [NYUAD Intranet](https://www.nyu.edu/abu-dhabi)
```

### Special building blocks (the `:::` blocks)

These create the magazine-style features. Each one **opens** with `::: name` and **closes** with a plain `:::`.

**A pull-quote (the teal highlighted quote):**

```markdown
::: quote
Every science student completes a Capstone research project in their fourth year.
:::
```

**A grid of cards** (used for programs, software, email groups):

```markdown
::: cards
::: card
#### Biology
- Biomedical Research
- Genome Science
:::
::: card
#### Chemistry
- Materials Science
- Soft Matter
:::
:::
```

**A grid of people:**

```markdown
::: people-grid
::: person
#### Eve Johnston
Associate Dean of Administration and Planning
<span class="email">ej21@nyu.edu</span>
:::
:::
```

**A note / warning box:**

```markdown
::: note
NOTE: Students should never work alone in laboratories.
:::
```

### The section header (front matter)

At the very top of each `content/*.md` file, between two `---` lines, is some settings the build uses. **You normally don't need to change this**, but if you rename a section title or add an item to the section's contents list, this is where it lives:

```yaml
---
order: 1                       # position of this section in the handbook
title: "Welcome to the Division"
nav_label: "Welcome"           # short name shown in the top menu
slug: welcome                  # the page's web address (welcome.html)
hero: hero-welcome.png         # the large photo for this section
toc:                           # the contents list shown on the divider page
  - ["Welcome From the Dean of Science", 5]
  - ["Teaching", 7]
---
```

Keep the `---` lines and the indentation exactly as they are.

### Adding a photo

1. Put your image file in the **`assets/images/`** folder (use a simple name, e.g. `hero-events.png`).
2. Reference it in the text like this:

```markdown
![Short description of the photo](assets/images/hero-events.png){.hero-img}
```

The `{.hero-img}` part makes it a full-width banner image.

---

## What's in this repository

```
science_handbook/
├── content/                ← THE TEXT YOU EDIT (one Markdown file per section)
│   ├── 00-cover.md
│   ├── 10-welcome.md
│   ├── 20-joining.md
│   ├── 30-life-division.md
│   ├── 40-communication.md
│   ├── 50-life-nyuad.md
│   └── 60-life-uae.md
├── assets/
│   ├── css/handbook.css    ← the brand styling (colours, fonts, layout)
│   └── images/             ← photos used in the handbook
├── templates/              ← page layouts (rarely need changing)
│   ├── page.html.j2        ← a website page
│   └── print.html.j2       ← the PDF layout
├── build.py                ← the script that builds the site + PDF
├── requirements.txt        ← the tools build.py needs
├── .github/workflows/
│   └── build.yml           ← the robot that auto-builds & publishes
└── README.md               ← this guide
```

As an editor you will spend ~99% of your time in **`content/`** and occasionally add a photo to **`assets/images/`**. Everything else is machinery that just works.

---

## Getting help

- **My edit broke the build (red ❌ on my PR).** Nine times out of ten it's a `:::` block that was opened but not closed, or a missing `---` in the front matter. Re-read your change and check the pairs match. Still stuck? Comment on your Pull Request and tag the maintainer.
- **I don't see my change on the website.** Changes only go live after your Pull Request is **merged** into `main`, then it takes a minute or two. Check the **Actions** tab for progress.
- **I'm not sure my wording is right.** That's fine — open the Pull Request anyway. Nothing goes live until it's reviewed and approved, so you can't break the published handbook.

Welcome aboard, and thank you for helping keep the handbook accurate and up to date!
