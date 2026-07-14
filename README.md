# Division of Science - New Joiners Handbook

This repository publishes the NYU Abu Dhabi Division of Science New Joiners
Handbook as an online PDF viewer.

The live website is built directly from the official June 2025 PDF. Each page
shown on the website is a rendered image of the matching PDF page, and the
Download PDF button points to the same PDF.

## Files

- `assets/handbook.pdf` - the official handbook PDF used for download.
- `assets/pdf-pages/` - rendered page images used by the website.
- `build.py` - creates the `site/` folder for GitHub Pages.

## Build

Run:

```bash
python build.py
```

The output appears in `site/`. GitHub Actions runs the same build and publishes
the result to GitHub Pages.

## Updating Later

When a new handbook PDF is ready:

1. Replace `assets/handbook.pdf`.
2. Replace the page images in `assets/pdf-pages/` with renders from the new PDF.
3. Run `python build.py`.
4. Commit and push the changes through a Pull Request.
