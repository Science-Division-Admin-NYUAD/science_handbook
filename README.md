# Division of Science - New Joiners Handbook

This repository publishes the NYU Abu Dhabi Division of Science New Joiners
Handbook as an editable website.

The website source is the Markdown in `content/*.md`. Each major handbook
section has its own file, so future edits can be made by changing normal text
instead of replacing PDF page images.

## Main Files

- `content/*.md` - editable handbook text.
- `assets/css/site.css` - website styling.
- `build.py` - turns the Markdown files into the static website in `site/`.
- `assets/handbook.pdf` - reference copy of the June 2025 PDF.

## Build

Run:

```bash
python build.py
```

The output appears in `site/`.

## Editing

To update the handbook later:

1. Open the matching file in `content/`.
2. Edit the text.
3. Run `python build.py` to preview.
4. Commit the change and open a Pull Request.

The website is now the master copy. The reference PDF is kept only for download
and comparison unless a future PDF-generation step is added.
