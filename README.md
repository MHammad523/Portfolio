# Muhammad Hammad — Portfolio

A from-scratch, custom-designed personal portfolio site (dark/light mode, SEO-optimized,
JSON-driven). No Bootstrap/template — hand-built CSS design system + vanilla JS.

## How to edit content

All content — bio, stats, skills, experience, the flagship AI chatbot project, portfolio
projects/images, contact info — lives in **`data/resume.json`**. To change anything on the
site (add a project, remove a skill, update a bullet point), edit that file, then rebuild:

```bash
python3 build.py
```

This regenerates `index.html` (plus `assets/img/og-card.png`, `robots.txt`, and
`sitemap.xml`) from the JSON. Requires Python 3 + Pillow (`pip install Pillow
--break-system-packages`).

**Why a build step instead of loading the JSON in the browser?** Baking the content into
real static HTML (rather than fetching + rendering with JavaScript) means the page is fully
readable with JS off, indexable by search engines immediately, and compatible with browser
reader-mode — none of which work reliably with pure client-side rendering.

## Preview locally

Browsers block `fetch`/relative asset loading oddities on `file://`, so serve it:

```bash
python3 -m http.server 8000
```

then open `http://localhost:8000`.

## Adding a new portfolio project

In `data/resume.json`, add an object to the relevant `experience[].projects` array:

```json
{
  "name": "Project Name",
  "filterKey": "ProjectName",
  "link": "https://example.com",
  "images": ["assets/img/portfolio/ProjectName/cover.jpg"],
  "modules": [{ "name": "Module", "description": ["What you built."] }]
}
```

Drop the images in `assets/img/portfolio/ProjectName/`, then run `python3 build.py`.
Projects with no `images` won't appear in the visual gallery but will still show up as a
"Also shipped" chip under the relevant role, so nothing in the JSON is silently dropped.

## Housekeeping (optional)

This folder still has unused leftovers from an earlier draft that reused the old
Bootstrap template — they're not linked from anything, so they don't affect the live site,
but you can delete them for a tidier folder:

- `assets/vendor/*` — every subfolder except `bootstrap-icons` (the only vendor asset the
  new design actually uses, for icons)
- `assets/css/custom.css`, `assets/css_original_reference.css`, `assets/vendor-readme.txt`
- `assets/js/main.js`

I can't delete files myself in this connected folder, so it's a manual cleanup if you want it.
