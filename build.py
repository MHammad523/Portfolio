#!/usr/bin/env python3
"""
build.py — generates index.html from data/resume.json.

WHY A BUILD STEP: content is baked into real, static, semantic HTML (not
injected by JavaScript after a fetch) so the page is fully readable with
JS off, indexable by search engines, and compatible with browser "reader
mode". Run this script again any time you edit data/resume.json:

    python3 build.py

Requires: Python 3 + Pillow (`pip install Pillow --break-system-packages`)
Pillow is only used to read image dimensions (for width/height attributes,
which prevents layout shift) and to (re)generate the social-share card.
"""
import json
import html
import os
import datetime

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "resume.json")
OUT_PATH = os.path.join(ROOT, "index.html")
SITE_URL = "https://mhammad523.github.io/"  # update if you deploy elsewhere

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

_dim_cache = {}


def esc(value):
    return html.escape(str(value), quote=True)


def month_year(ym):
    if not ym:
        return "Present"
    parts = str(ym).split("-")
    if len(parts) == 1:
        return parts[0]
    y, m = parts
    try:
        return f"{MONTHS[int(m) - 1]} {y}"
    except (ValueError, IndexError):
        return ym


def img_dims(rel_path):
    if rel_path in _dim_cache:
        return _dim_cache[rel_path]
    if not HAVE_PIL:
        return None, None
    full = os.path.join(ROOT, rel_path)
    try:
        with Image.open(full) as im:
            _dim_cache[rel_path] = im.size
            return im.size
    except Exception:
        _dim_cache[rel_path] = (None, None)
        return None, None


def img_tag(src, alt, cls="", loading="lazy", extra=""):
    w, h = img_dims(src)
    dims = f' width="{w}" height="{h}"' if w and h else ""
    cls_attr = f' class="{cls}"' if cls else ""
    return f'<img src="{esc(src)}" alt="{esc(alt)}"{cls_attr}{dims} loading="{loading}" decoding="async"{extra}>'


def slugify(name):
    return "".join(c if c.isalnum() else "-" for c in name).strip("-")


# --------------------------------------------------------------------------
# Section builders
# --------------------------------------------------------------------------

def build_head(data):
    basics = data["basics"]
    title = f"{basics['name']} — {' / '.join(basics['title'])}"
    description = basics["summary"][:157].rstrip() + ("…" if len(basics["summary"]) > 157 else "")
    og_image = SITE_URL.rstrip("/") + "/assets/img/og-card.png"

    social_same_as = list(basics.get("social", {}).values())
    ld_json = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": basics["name"],
        "url": SITE_URL,
        "email": "mailto:" + basics["email"],
        "jobTitle": basics["title"][0] if basics.get("title") else "",
        "description": basics["summary"],
        "address": {"@type": "PostalAddress", "addressLocality": basics.get("location", "")},
        "sameAs": social_same_as,
        "knowsAbout": basics.get("heroTaglines", [])
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<script>
  /* Set theme before first paint to avoid a flash of the wrong theme. */
  (function() {{
    try {{
      var saved = localStorage.getItem('theme');
      var theme = saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
      document.documentElement.setAttribute('data-theme', theme);
    }} catch (e) {{ document.documentElement.setAttribute('data-theme', 'dark'); }}
  }})();
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="keywords" content="{esc(', '.join(basics.get('title', []) + basics.get('heroTaglines', [])))}">
<meta name="author" content="{esc(basics['name'])}">
<link rel="canonical" href="{esc(SITE_URL)}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#7c5cff">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(basics['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{esc(og_image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{esc(SITE_URL)}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(og_image)}">

<!-- Favicons -->
<link rel="icon" href="assets/img/favicon.ico">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">

<link href="assets/vendor/bootstrap-icons/bootstrap-icons.css" rel="stylesheet">
<link href="assets/css/style.css" rel="stylesheet">

<script type="application/ld+json">{json.dumps(ld_json, ensure_ascii=False)}</script>
</head>"""


def build_header(data):
    basics = data["basics"]
    social_icons = {
        "github": "bi-github", "behance": "bi-behance", "linkedin": "bi-linkedin",
        "twitter": "bi-twitter-x", "instagram": "bi-instagram", "facebook": "bi-facebook"
    }
    social_html = ""
    for key, url in basics.get("social", {}).items():
        icon = social_icons.get(key.lower(), "bi-link-45deg")
        social_html += f'<a class="icon-btn" href="{esc(url)}" target="_blank" rel="noopener" aria-label="{esc(key.title())}"><i class="bi {icon}" aria-hidden="true"></i></a>\n'

    name_parts = basics["name"].split(" ")
    first_initial = name_parts[0][0].lower()
    last_name_lower = name_parts[-1].lower()

    return f"""<header class="site-header">
  <div class="container header-inner">
    <a href="#top" class="brand">{esc(first_initial)}<span class="brand-dot">.</span>{esc(last_name_lower)}<span class="brand-dot">.</span>dev</a>
    <nav class="main-nav" aria-label="Primary">
      <ul>
        <li><a href="#about" class="nav-link">About</a></li>
        <li><a href="#skills" class="nav-link">Skills</a></li>
        <li><a href="#experience" class="nav-link">Experience</a></li>
        <li><a href="#work" class="nav-link">Work</a></li>
        <li><a href="#contact" class="nav-link">Contact</a></li>
      </ul>
    </nav>
    <div class="header-actions">
      {social_html}
      <button id="theme-toggle" class="icon-btn" aria-label="Switch theme" type="button"><i class="bi bi-sun" aria-hidden="true"></i></button>
      <button id="nav-toggle" class="icon-btn nav-toggle" aria-label="Toggle menu" aria-expanded="false" type="button"><i class="bi bi-list" aria-hidden="true"></i></button>
    </div>
  </div>
</header>"""


def build_hero(data):
    basics = data["basics"]
    name_parts = basics["name"].split(" ", 1)
    tag_items = basics.get("heroTaglines", [])
    tag_json = json.dumps(tag_items, ensure_ascii=False)

    return f"""<section id="hero" class="hero" aria-label="Introduction">
  <div class="container hero-inner">
    <p class="eyebrow reveal">Hi, I'm</p>
    <h1 class="hero-name reveal">{esc(name_parts[0])} <span class="grad-text">{esc(name_parts[1] if len(name_parts) > 1 else "")}</span></h1>
    <p class="hero-role reveal reveal-delay-1">I'm a <span id="typed-role" class="typed-role" data-items='{tag_json}'></span></p>
    <p class="hero-bio reveal reveal-delay-2">{esc(basics["summary"])}</p>
    <div class="hero-cta reveal reveal-delay-2">
      <a href="#contact" class="btn btn-primary">Get in touch <i class="bi bi-arrow-right" aria-hidden="true"></i></a>
      <a href="MHammadResume.pdf" class="btn btn-ghost" download>Download Resume <i class="bi bi-download" aria-hidden="true"></i></a>
    </div>
  </div>
  <a href="#about" class="scroll-cue" aria-label="Scroll to content"><i class="bi bi-mouse" aria-hidden="true"></i></a>
</section>"""


def build_about(data):
    basics = data["basics"]
    facts = []
    if basics.get("yearsExperience"):
        facts.append(("bi-briefcase", "Experience", f"{basics['yearsExperience']}+ years", None))
    if basics.get("location"):
        facts.append(("bi-geo-alt", "Based in", basics["location"], None))
    if basics.get("email"):
        facts.append(("bi-envelope", "Email", basics["email"], "mailto:" + basics["email"]))
    facts.append(("bi-lightning-charge", "Availability", "Available for freelance" if basics.get("freelanceAvailable") else "Not currently available", None))

    facts_html = ""
    for icon, label, value, link in facts:
        inner = f'<a href="{esc(link)}">{esc(value)}</a>' if link else esc(value)
        facts_html += f'<li><i class="bi {icon}" aria-hidden="true"></i><div><strong>{esc(label)}</strong><span>{inner}</span></div></li>\n'

    return f"""<section id="about" class="section about" aria-labelledby="about-title">
  <div class="container about-grid">
    <div class="about-media reveal">
      <div class="photo-frame">
        {img_tag("assets/img/profile-img.jpg", "Portrait of " + basics["name"], loading="eager")}
      </div>
    </div>
    <div class="about-copy reveal reveal-delay-1">
      <p class="eyebrow">About Me</p>
      <h2 id="about-title">Turning complex problems into <span class="grad-text">clean, reliable software</span>.</h2>
      <p>{esc(basics["summary"])}</p>
      <ul class="about-facts">
        {facts_html}
      </ul>
    </div>
  </div>
</section>"""


def build_stats(data):
    cards = ""
    for fact in data.get("facts", []):
        cards += f"""<div class="stat-card reveal">
      <i class="bi {esc(fact['icon'])}" aria-hidden="true"></i>
      <span class="stat-num" data-count="{esc(fact['value'])}">0</span>
      <p><strong>{esc(fact['label'])}</strong> — {esc(fact.get('description', ''))}</p>
    </div>"""
    return f"""<section class="section stats" aria-label="Career highlights">
  <div class="container stats-grid">
    {cards}
  </div>
</section>"""


def build_skills(data):
    rings = ""
    for bar in data.get("skillBars", []):
        rings += f"""<div class="ring-card reveal">
      <div class="ring" data-val="{bar['percent']}" style="--val:0">
        <span>{bar['percent']}%</span>
      </div>
      <p>{esc(bar['name'])}</p>
    </div>"""

    categories = {
        "web": "Web & Frameworks",
        "languages": "Languages",
        "databases": "Databases",
        "ai_ml": "AI / Machine Learning"
    }
    chip_groups = ""
    for key, label in categories.items():
        items = data.get("skills", {}).get(key, [])
        if not items:
            continue
        chips = "".join(f'<span class="chip">{esc(i)}</span>' for i in items)
        chip_groups += f"""<div class="chip-group reveal">
      <h3>{esc(label)}</h3>
      <div class="chips">{chips}</div>
    </div>"""

    return f"""<section id="skills" class="section skills" aria-labelledby="skills-title">
  <div class="container">
    <p class="eyebrow">Skills</p>
    <h2 id="skills-title">My <span class="grad-text">Toolbox</span></h2>
    <div class="skills-rings">
      {rings}
    </div>
    <div class="skill-categories">
      {chip_groups}
    </div>
  </div>
</section>"""


def build_flagship(fp):
    chips = "".join(f'<span class="tech-chip">{esc(t)}</span>' for t in fp.get("technologies", []))
    details = ""
    for d in fp.get("details", []):
        details += f"""<div class="detail-card">
        <div class="detail-area"><i class="bi bi-check-circle-fill" aria-hidden="true"></i>{esc(d['area'])}</div>
        <p>{esc(d['description'])}</p>
      </div>"""
    return f"""<div class="spotlight">
      <div class="spotlight-inner">
        <div class="spotlight-head">
          <div class="icon-badge"><i class="bi {esc(fp.get('icon', 'bi-star-fill'))}" aria-hidden="true"></i></div>
          <div>
            <div class="spotlight-tag">Flagship Project</div>
            <h3>{esc(fp['name'])}</h3>
          </div>
        </div>
        <p class="spotlight-summary">{esc(fp['summary'])}</p>
        <div class="spotlight-chips">{chips}</div>
        <div class="spotlight-details">{details}</div>
      </div>
    </div>"""


def build_experience(data):
    items = ""
    for exp in data.get("experience", []):
        is_current = exp.get("current")
        cr = exp.get("currentRole")
        dot_class = " is-current" if is_current else ""

        if is_current and cr:
            dates = f"{month_year(cr['start'])} — Present"
            badge = '<span class="current-badge">Current</span>'
            highlights = "".join(f"<li>{esc(hl)}</li>" for hl in cr.get("highlights", []))
            other_projects = [p for p in exp.get("projects", []) if not p.get("images")]
            other_html = ""
            if other_projects:
                chips = "".join(f'<span class="tech-chip">{esc(p["name"])}</span>' for p in other_projects)
                other_html = f'<p class="also-worked"><strong>Also shipped:</strong></p><div class="spotlight-chips">{chips}</div>'
            body = f"""<h3>{esc(cr['label'])} — {esc(exp['position'])}</h3>
        <div class="timeline-head"><span class="timeline-dates">{esc(dates)}</span>{badge}</div>
        <div class="timeline-company">{esc(exp['company'])}</div>
        <ul class="timeline-highlights">{highlights}</ul>
        {other_html}"""
            flagship_html = build_flagship(cr["flagshipProject"]) if cr.get("flagshipProject") else ""
        else:
            dates = f"{month_year(exp.get('start'))} — {month_year(exp.get('end'))}"
            proj_list = "".join(f"<li>{esc(p['name'])}</li>" for p in exp.get("projects", []))
            body = f"""<h3>{esc(exp['position'])}</h3>
        <div class="timeline-head"><span class="timeline-dates">{esc(dates)}</span></div>
        <div class="timeline-company">{esc(exp['company'])}</div>
        <ul class="project-list">{proj_list}</ul>"""
            flagship_html = ""

        items += f"""<div class="timeline-item{dot_class} reveal">
      <span class="timeline-dot" aria-hidden="true"></span>
      {body}
      {flagship_html}
    </div>"""

    edu_cards = ""
    for edu in data.get("education", []):
        details = edu.get("achievements") or edu.get("subjects") or []
        li = "".join(f"<li>{esc(d)}</li>" for d in details)
        edu_cards += f"""<div class="edu-card reveal">
      <h4>{esc(edu['program'])}</h4>
      <div class="edu-dates">{esc(edu.get('institution', ''))} · {esc(month_year(edu.get('start')))} – {esc(month_year(edu.get('end')))}</div>
      <ul>{li}</ul>
    </div>"""

    return f"""<section id="experience" class="section timeline-section" aria-labelledby="exp-title">
  <div class="container">
    <p class="eyebrow">Career</p>
    <h2 id="exp-title">Experience &amp; <span class="grad-text">Education</span></h2>
    <div class="timeline">
      {items}
    </div>
    <div class="education-grid">
      {edu_cards}
    </div>
  </div>
</section>"""


def build_portfolio(data):
    projects = []
    for exp in data.get("experience", []):
        for p in exp.get("projects", []):
            if p.get("images"):
                projects.append(p)

    pills = '<button class="pill active" data-filter="all" type="button">All</button>\n'
    cards = ""
    for p in projects:
        key = p.get("filterKey") or slugify(p["name"])
        pills += f'<button class="pill" data-filter="{esc(key)}" type="button">{esc(p["name"])}</button>\n'

        cover = p["images"][0]
        blurb_parts = []
        for mod in p.get("modules", []):
            desc = mod.get("description") or []
            if desc:
                blurb_parts.append(desc[0])
        blurb = " ".join(blurb_parts)
        images_json = esc(json.dumps(p["images"], ensure_ascii=False))

        if p.get("link"):
            link_html = f'<a class="work-link" href="{esc(p["link"])}" target="_blank" rel="noopener">Visit live <i class="bi bi-box-arrow-up-right" aria-hidden="true"></i></a>'
        else:
            link_html = '<span class="work-tag">Internal system</span>'

        cards += f"""<article class="work-card reveal" data-cat="{esc(key)}">
      <button class="work-thumb" type="button" data-images='{images_json}' data-title="{esc(p['name'])}" aria-label="Open {esc(p['name'])} gallery">
        {img_tag(cover, p['name'] + " screenshot", loading="lazy")}
        <span class="work-overlay"><i class="bi bi-zoom-in" aria-hidden="true"></i> View gallery ({len(p['images'])})</span>
      </button>
      <div class="work-info">
        <h3>{esc(p['name'])}</h3>
        <p>{esc(blurb)}</p>
        {link_html}
      </div>
    </article>"""

    return f"""<section id="work" class="section portfolio" aria-labelledby="work-title">
  <div class="container">
    <p class="eyebrow">Selected Work</p>
    <h2 id="work-title">Projects I've <span class="grad-text">Shipped</span></h2>
    <div class="filter-pills" role="tablist" aria-label="Filter projects">
      {pills}
    </div>
    <div class="work-grid">
      {cards}
    </div>
  </div>
</section>"""


def build_contact(data):
    contact = data.get("contact", {})
    basics = data["basics"]
    cards = ""
    if contact.get("email"):
        cards += f"""<a class="contact-card" href="mailto:{esc(contact['email'])}">
      <i class="bi bi-envelope" aria-hidden="true"></i><div><strong>Email</strong><span>{esc(contact['email'])}</span></div>
    </a>"""
    if contact.get("phone"):
        cards += f"""<a class="contact-card" href="tel:{esc(contact['phone'])}">
      <i class="bi bi-telephone" aria-hidden="true"></i><div><strong>Phone</strong><span>{esc(contact['phone'])}</span></div>
    </a>"""
    if contact.get("location"):
        cards += f"""<div class="contact-card">
      <i class="bi bi-geo-alt" aria-hidden="true"></i><div><strong>Location</strong><span>{esc(contact['location'])}</span></div>
    </div>"""
    for key, url in basics.get("social", {}).items():
        icon = {"github": "bi-github", "behance": "bi-behance"}.get(key.lower(), "bi-link-45deg")
        cards += f"""<a class="contact-card" href="{esc(url)}" target="_blank" rel="noopener">
      <i class="bi {icon}" aria-hidden="true"></i><div><strong>{esc(key.title())}</strong><span>View profile</span></div>
    </a>"""

    return f"""<section id="contact" class="section contact" aria-labelledby="contact-title">
  <div class="container contact-inner">
    <p class="eyebrow">Contact</p>
    <h2 id="contact-title">Let's build something <span class="grad-text">great together</span>.</h2>
    <p>Have a project, a role, or an idea you want to talk through? My inbox is open — I usually reply within a day.</p>
    <div class="contact-grid">
      {cards}
    </div>
  </div>
</section>"""


def build_footer(data, year):
    name = data["basics"]["name"]
    return f"""<footer class="site-footer">
  <div class="container footer-inner">
    <p>&copy; {year} {esc(name)}. All rights reserved.</p>
    <a href="#top" class="back-to-top" aria-label="Back to top"><i class="bi bi-arrow-up" aria-hidden="true"></i></a>
  </div>
</footer>"""


def build_lightbox():
    return """<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-hidden="true" aria-label="Project image viewer">
  <button class="lightbox-close" type="button" aria-label="Close"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
  <button class="lightbox-prev" type="button" aria-label="Previous image"><i class="bi bi-chevron-left" aria-hidden="true"></i></button>
  <div>
    <img class="lightbox-img" src="" alt="">
    <p class="lightbox-caption"></p>
  </div>
  <button class="lightbox-next" type="button" aria-label="Next image"><i class="bi bi-chevron-right" aria-hidden="true"></i></button>
</div>"""


def build_body(data):
    year = datetime.date.today().year
    return f"""<body id="top">
<a href="#main" class="skip-link">Skip to content</a>
<div class="bg-decor" aria-hidden="true">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="grid"></div>
</div>

{build_header(data)}

<main id="main">
{build_hero(data)}
{build_about(data)}
{build_stats(data)}
{build_skills(data)}
{build_experience(data)}
{build_portfolio(data)}
{build_contact(data)}
</main>

{build_footer(data, year)}
{build_lightbox()}

<noscript><div class="noscript-banner">This page works without JavaScript — enable it for theme switching, the project gallery, and a few animations.</div></noscript>

<script src="assets/js/site.js"></script>
</body>
</html>"""


def build_og_card(data):
    """Regenerate assets/img/og-card.png (1200x630 social share card)."""
    if not HAVE_PIL:
        print("Pillow not available — skipping OG card generation.")
        return
    W, H = 1200, 630
    try:
        import numpy as np
        base = np.array([5, 7, 13], dtype=np.float32)
        violet = np.array([80, 50, 200], dtype=np.float32)
        cyan = np.array([20, 140, 170], dtype=np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        diag = (xx / W) * 0.5 + (yy / H) * 0.5  # 0 (top-left) -> 1 (bottom-right)
        # radial glow anchored top-left (violet) and bottom-right (cyan)
        glow_tl = np.clip(1 - np.sqrt((xx / W) ** 2 + (yy / H) ** 2), 0, 1) ** 1.6
        glow_br = np.clip(1 - np.sqrt(((W - xx) / W) ** 2 + ((H - yy) / H) ** 2), 0, 1) ** 1.6
        arr = base[None, None, :] \
            + glow_tl[:, :, None] * (violet - base)[None, None, :] * 0.9 \
            + glow_br[:, :, None] * (cyan - base)[None, None, :] * 0.55
        arr = np.clip(arr, 0, 255).astype("uint8")
        img = Image.fromarray(arr, "RGB")
    except Exception:
        img = Image.new("RGB", (W, H), (10, 8, 25))

    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)

    font_dir_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font_regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    def load_font(paths, size):
        for p in paths:
            if os.path.isfile(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    font_name = load_font(font_dir_candidates, 78)
    font_role = load_font(font_regular_candidates, 34)
    font_tag = load_font(font_dir_candidates, 22)

    basics = data["basics"]
    draw.text((80, 70), "◆ PORTFOLIO", font=font_tag, fill=(124, 220, 255))
    draw.text((78, 230), basics["name"], font=font_name, fill=(240, 242, 248))
    role_line = " / ".join(basics.get("title", [])[:2])
    draw.text((80, 330), role_line, font=font_role, fill=(170, 178, 195))

    chips = basics.get("heroTaglines", [])[:5]
    margin = 80
    cx = margin
    cy = 410
    for chip in chips:
        w = draw.textlength(chip, font=font_tag) + 34
        if cx + w > W - margin:
            cx = margin
            cy += 60
        draw.rounded_rectangle([cx, cy, cx + w, cy + 46], radius=23, outline=(150, 210, 255), width=2)
        draw.text((cx + 17, cy + 12), chip, font=font_tag, fill=(215, 225, 240))
        cx += w + 14

    out_path = os.path.join(ROOT, "assets", "img", "og-card.png")
    img.save(out_path, "PNG", optimize=True)
    print("Generated", out_path)


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    doc = build_head(data) + "\n" + build_body(data)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(doc)
    print("Built", OUT_PATH, f"({len(doc):,} bytes)")

    build_og_card(data)

    # robots.txt + sitemap.xml
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml\n")

    today = datetime.date.today().isoformat()
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
""")
    print("Built robots.txt and sitemap.xml")


if __name__ == "__main__":
    main()
