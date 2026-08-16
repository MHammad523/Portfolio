"""
build_resume_html.py — generates Resume.html: a single, self-contained,
print-ready A4 page (210mm x 297mm) built entirely from data/resume.json.

Design: a fresh, light, editorial layout (paper background, ink text, a
single warm accent used only for hairlines/labels/borders) so it degrades
perfectly to black & white printing — nothing depends on a filled color
block to remain legible.

No external CSS/JS/fonts/images — everything (including the QR code,
rendered as inline SVG rects) is baked into one HTML file. Open it in a
browser and use Print -> Save as PDF to export a matching one-page PDF.

Usage:
    python3 build_resume_html.py
"""
import json
import os
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "resume.json")
OUT_PATH = os.path.join(ROOT, "Resume.html")
PORTFOLIO_URL = "https://mhammad523.github.io/"


def esc(s):
    return html.escape(str(s), quote=True)


def qr_svg(url, size_mm=30, dark="#16181d"):
    """Dependency-free inline SVG QR code using reportlab's encoder for the
    bit-matrix only (no image/raster embedding, no external qrcode lib)."""
    from reportlab.graphics.barcode.qr import QrCodeWidget
    w = QrCodeWidget(url)
    w.getBounds()  # forces the encoder to build the module matrix
    qrobj = w.qr
    n = qrobj.moduleCount
    modules = qrobj.modules
    rects = []
    for r in range(n):
        for c in range(n):
            if modules[r][c]:
                rects.append(f'<rect x="{c}" y="{r}" width="1" height="1"/>')
    return (
        f'<svg viewBox="0 0 {n} {n}" width="{size_mm}mm" height="{size_mm}mm" '
        f'shape-rendering="crispEdges" role="img" aria-label="QR code linking to {esc(url)}">'
        f'<rect x="0" y="0" width="{n}" height="{n}" fill="#ffffff"/>'
        f'<g fill="{dark}">{"".join(rects)}</g>'
        f'</svg>'
    )


with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)
basics = data["basics"]
skills = data.get("skills", {})

# ---------------- Experience ----------------
exp0 = data["experience"][0]
cr = exp0["currentRole"]
fp = cr["flagshipProject"]
exp1 = data["experience"][1]

current_highlights_html = "".join(f"<li>{esc(h)}</li>" for h in cr.get("highlights", []))

proj_bits = []
for p in exp0["projects"]:
    mods = p.get("modules", [])
    d = mods[0]["description"][0] if mods and mods[0].get("description") else ""
    proj_bits.append(f'<li><b>{esc(p["name"])}:</b> {esc(d)}</li>')
also_delivered_html = "".join(proj_bits)

aptech_bits = []
for p in exp1["projects"]:
    d = " ".join(p.get("description", []))
    aptech_bits.append(f'<li><b>{esc(p["name"])}:</b> {esc(d)}</li>')
aptech_html = "".join(aptech_bits)

flagship_tech_chips = "".join(f'<span class="chip">{esc(t)}</span>' for t in fp.get("technologies", []))

# ---------------- Education ----------------
edu_dates = ["2018 – 2021", "2019 – 2021", "2015 – 2018"]
edu_items = []
for i, edu in enumerate(data["education"]):
    details = edu.get("achievements") or edu.get("subjects") or []
    inst = f" — {esc(edu['institution'])}" if edu.get("institution") else ""
    edu_items.append(f"""
        <div class="edu-item">
          <div class="edu-top"><span class="edu-title">{esc(edu['program'])}{inst}</span><span class="edu-date">{edu_dates[i]}</span></div>
          <div class="edu-sub">{esc(', '.join(details))}</div>
        </div>""")
education_html = "".join(edu_items)

# ---------------- Skills (outline chip groups) ----------------
def skill_group(title, items):
    chips = "".join(f'<span class="skill-chip">{esc(i)}</span>' for i in items)
    return f'<div class="skill-group"><div class="rail-label">{esc(title)}</div><div class="chip-wrap">{chips}</div></div>'

skills_html = (
    skill_group("Languages", skills.get("languages", []))
    + skill_group("Web & Frameworks", skills.get("web", []))
    + skill_group("Databases", skills.get("databases", []))
    + skill_group("AI / ML", skills.get("ai_ml", []))
)

titles_html = " &nbsp;/&nbsp; ".join(esc(t).upper() for t in basics.get("title", []))
qr_markup = qr_svg(basics.get("portfolio", PORTFOLIO_URL))
portfolio_display = basics.get("portfolio", PORTFOLIO_URL).replace("https://", "").replace("http://", "").rstrip("/")
first_name = basics["name"].split(" ")[0]
last_name = " ".join(basics["name"].split(" ")[1:])

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(basics['name'])} — Resume</title>
<style>
  @page {{ size: A4; margin: 0; }}

  * {{ box-sizing: border-box; }}

  :root {{
    --paper: #faf9f6;
    --ink: #16181d;
    --ink-soft: #52565f;
    --muted: #8b8f99;
    --accent: #3373a3;
    --accent-tint: rgba(51, 115, 163, 0.07);
    --line: #e7ecef;
    --line-strong: #dbe3e8;
    --rail-bg: #f2f6f9;
    --rail-line: rgba(22, 24, 29, 0.09);
  }}

  html, body {{
    margin: 0;
    padding: 0;
    background: #e9e7e1;
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    color-adjust: exact;
  }}

  .print-hint {{
    max-width: 210mm;
    margin: 6mm auto 0;
    padding: 3mm 5mm;
    background: #fff7d6;
    border: 1px solid #e8d27a;
    border-radius: 6px;
    font-size: 12px;
    color: #4a3f10;
  }}
  .print-hint b {{ color: #2a2400; }}

  .page-wrap {{
    display: flex;
    justify-content: center;
    padding: 6mm 0 12mm;
  }}

  .page {{
    position: relative;
    width: 210mm;
    height: 297mm;
    background: var(--paper);
    box-shadow: 0 4px 24px rgba(0,0,0,0.16);
    overflow: hidden;
    color: var(--ink);
  }}

  /* ---------- full-height colored rail column ---------- */
  .rail {{
    position: absolute;
    top: 0; left: 0;
    width: 68mm;
    height: 297mm;
    background: var(--rail-bg);
    border-right: 1px solid var(--line-strong);
    padding: 17mm 8mm 13mm 15mm;
  }}

  /* ---------- white main column ---------- */
  .main-col {{
    position: absolute;
    top: 0; left: 68mm; right: 0;
    height: 297mm;
    padding: 17mm 15mm 13mm 13mm;
  }}

  /* ---------- header ---------- */
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 6mm;
  }}
  .name {{
    font-size: 26pt;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.3px;
    margin: 0 0 2mm;
  }}
  .name .last {{ color: var(--accent); font-weight: 700; }}
  .titles {{
    font-size: 7.6pt;
    letter-spacing: 1.4px;
    color: var(--accent);
    font-weight: 600;
  }}
  .contact-block {{
    text-align: right;
    font-size: 7.6pt;
    color: var(--ink-soft);
    line-height: 1.55;
    white-space: nowrap;
  }}
  .badge {{
    display: inline-block;
    margin-top: 2mm;
    padding: 1mm 2.6mm;
    border: 1px solid var(--accent);
    border-radius: 20px;
    font-size: 6.6pt;
    letter-spacing: 0.5px;
    color: var(--accent);
    font-weight: 600;
  }}

  .rule {{
    position: relative;
    margin: 4mm 0 6mm;
    border-top: 1px solid var(--line-strong);
  }}
  .rule::before {{
    content: "";
    position: absolute;
    top: -1px; left: 0;
    width: 16mm;
    border-top: 2px solid var(--accent);
  }}

  .rail-label, h2.section {{
    font-size: 7.4pt;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--ink);
    font-weight: 700;
    margin: 0 0 2.4mm;
  }}
  .rail-block {{ margin-bottom: 6mm; }}
  .rail-block h2.section {{
    padding-bottom: 1.4mm;
    border-bottom: 1px solid var(--rail-line);
  }}

  .skill-group {{ margin-bottom: 3.4mm; }}
  .skill-group .rail-label {{
    font-size: 6.7pt;
    letter-spacing: 1px;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 1.6mm;
  }}
  .chip-wrap {{ display: flex; flex-wrap: wrap; gap: 1.3mm; }}
  .skill-chip {{
    font-size: 6.9pt;
    padding: 0.9mm 2mm;
    border: 1px solid var(--line-strong);
    border-radius: 3px;
    color: var(--ink-soft);
    line-height: 1.3;
    background: #ffffff;
  }}

  .edu-item {{ margin-bottom: 3.4mm; }}
  .edu-top {{ display: flex; justify-content: space-between; gap: 2mm; align-items: baseline; }}
  .edu-title {{ font-size: 7.6pt; font-weight: 700; color: var(--ink); line-height: 1.3; }}
  .edu-date {{ font-size: 6.6pt; color: var(--muted); white-space: nowrap; flex-shrink: 0; }}
  .edu-sub {{ font-size: 6.9pt; color: var(--ink-soft); margin-top: 0.8mm; line-height: 1.35; }}

  .qr-block {{
    margin-top: 2mm;
    padding-top: 4mm;
    border-top: 1px solid var(--rail-line);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2.4mm;
    text-align: center;
  }}
  .qr-frame {{
    border: 1px solid var(--rail-line);
    border-radius: 2px;
    padding: 1.4mm;
    line-height: 0;
    background: #ffffff;
  }}
  .qr-text .qr-title {{
    font-size: 7.2pt;
    font-weight: 700;
    color: var(--ink);
  }}

  /* ---------- experience (main column) ---------- */
  .job {{ margin-bottom: 3.6mm; }}
  .job-top {{ display: flex; justify-content: space-between; align-items: baseline; gap: 3mm; }}
  .job-role {{ font-size: 9.4pt; font-weight: 700; color: var(--ink); }}
  .job-dates {{ font-size: 6.8pt; color: var(--muted); white-space: nowrap; }}
  .job-company {{ font-size: 7.6pt; color: var(--accent); font-weight: 600; margin: 0.4mm 0 1.8mm; }}

  ul.bullets {{
    margin: 0 0 2mm;
    padding-left: 3.4mm;
    font-size: 7.3pt;
    line-height: 1.48;
    color: var(--ink-soft);
  }}
  ul.bullets li {{ margin-bottom: 0.6mm; }}
  ul.bullets li::marker {{ color: var(--accent); }}

  .callout {{
    margin: 2.4mm 0;
    padding: 2.6mm 3.4mm;
    border-left: 2px solid var(--accent);
    background: var(--accent-tint);
    border-radius: 0 3px 3px 0;
  }}
  .callout .callout-label {{
    font-size: 6.6pt;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 1mm;
  }}
  .callout .callout-name {{
    font-size: 8.3pt;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 1mm;
  }}
  .callout p {{
    font-size: 7.2pt;
    line-height: 1.48;
    color: var(--ink-soft);
    margin: 0 0 1.8mm;
  }}
  .chip {{
    display: inline-block;
    font-size: 6.4pt;
    padding: 0.7mm 1.7mm;
    margin: 0 0.8mm 0.8mm 0;
    border: 1px solid var(--line-strong);
    border-radius: 3px;
    color: var(--ink-soft);
    background: #ffffff;
  }}

  .also-label {{
    font-size: 6.8pt;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--ink);
    margin: 2.2mm 0 1.2mm;
  }}
  ul.proj-list {{
    margin: 0;
    padding-left: 3.4mm;
    font-size: 7.1pt;
    line-height: 1.48;
    color: var(--ink-soft);
  }}
  ul.proj-list li {{ margin-bottom: 0.6mm; }}
  ul.proj-list li::marker {{ color: var(--accent); }}
  ul.proj-list b {{ color: var(--ink); }}

  @media print {{
    html, body {{ background: #fff; }}
    .print-hint {{ display: none; }}
    .page-wrap {{ padding: 0; }}
    .page {{ box-shadow: none; }}
  }}
</style>
</head>
<body>

  <div class="print-hint">
    <b>To export as PDF:</b> File &rarr; Print (or Cmd/Ctrl+P) &rarr; Destination: "Save as PDF" &rarr;
    Margins: None &rarr; Background graphics: on (optional — this design is built to look great even without it, for clean black &amp; white printing).
    This page is sized exactly to A4 (210 &times; 297mm), one page. This banner will not appear in the exported PDF.
  </div>

  <div class="page-wrap">
    <div class="page">

      <div class="rail">

        <div class="rail-block">
          <h2 class="section">Skills</h2>
          {skills_html}
        </div>

        <div class="rail-block">
          <h2 class="section">Education</h2>
          {education_html}
        </div>

        <div class="qr-block">
          <div class="qr-frame">{qr_markup}</div>
          <div class="qr-text">
            <div class="qr-title">View live portfolio</div>
          </div>
        </div>

      </div>

      <div class="main-col">

        <div class="header">
          <div>
            <div class="name">{esc(first_name)} <span class="last">{esc(last_name)}</span></div>
            <div class="titles">{titles_html}</div>
          </div>
          <div class="contact-block">
            <div>{esc(basics['email'])}</div>
            <div>{esc(basics['phone'])}</div>
            <div>{esc(basics.get('location',''))}</div>
          </div>
        </div>
        <div class="rule"></div>

        <h2 class="section">Experience</h2>

        <div class="job">
          <div class="job-top">
            <span class="job-role">{esc(cr['label'])}</span>
            <span class="job-dates">Aug 2021 – Present</span>
          </div>
          <div class="job-company">{esc(exp0['company'])}</div>
          <ul class="bullets">
            {current_highlights_html}
          </ul>

          <div class="callout">
            <div class="callout-label">Flagship project</div>
            <div class="callout-name">{esc(fp['name'])}</div>
            <p>{esc(fp['summary'])}</p>
            <div>{flagship_tech_chips}</div>
          </div>

          <div class="also-label">Also delivered</div>
          <ul class="proj-list">{also_delivered_html}</ul>
        </div>

        <div class="job">
          <div class="job-top">
            <span class="job-role">{esc(exp1['position'])}</span>
            <span class="job-dates">Nov 2018 – Apr 2021</span>
          </div>
          <div class="job-company">{esc(exp1['company'])}</div>
          <ul class="proj-list">{aptech_html}</ul>
        </div>

      </div>

    </div>
  </div>

</body>
</html>
"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote", OUT_PATH)
