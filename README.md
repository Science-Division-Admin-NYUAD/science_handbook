# Division of Science - New Joiners Handbook

This repository publishes the NYU Abu Dhabi Division of Science New Joiners
Handbook as an editable website.

The website and downloadable PDF are both generated from the Markdown in
`content/*.md`. Each major handbook section has its own file, so future edits
can be made by changing normal text instead of replacing PDF page images.

## Main Files

- `content/*.md` - editable handbook text.
- `assets/css/site.css` - website styling.
- `build.py` - turns the Markdown files into the static website and generated PDF in `site/`.
- `assets/handbook.pdf` - old reference copy of the June 2025 PDF; it is not used for the download button.

## Build

Run:

```bash
python build.py
```

The website output appears in `site/`. On GitHub, the workflow also generates
the styled downloadable PDF at `site/handbook.pdf`. Local builds skip the PDF if
the required styled PDF engine is unavailable, rather than creating a poor
fallback PDF. A browser-checkable print layout is always generated at
`site/handbook-print.html`.

## Editing

To update the handbook later:

1. Open the matching file in `content/`.
2. Edit the text.
3. Run `python build.py` to preview.
4. Commit the change and open a Pull Request.

The website is now the master copy. The PDF download is regenerated from the
same editable content during the GitHub build.
