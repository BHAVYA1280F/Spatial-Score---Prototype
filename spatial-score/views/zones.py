"""Zones page — Five-Zone Spatial Journey reference table, styled to match the app."""
import streamlit as st
import streamlit.components.v1 as components

from ui import graphics as g

# ── page header ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal">From Music to Architecture</div>'
    '<h1 class="reveal disp" style="font-size:clamp(2rem,5vw,3.4rem);margin-bottom:.3rem">'
    'SPATIAL <strong>SCORE</strong></h1>'
    '<p class="lead reveal" style="margin-bottom:2.5rem">Five-Zone Spatial Journey — '
    'how each section of the song becomes a distinct architectural experience.</p>',
    unsafe_allow_html=True,
)

# ── zone data ─────────────────────────────────────────────────────────────────
# (number, name, subtitle, description, bullet features, accent colour, bar heights)
ZONES_TABLE = [
    (
        "01", "INTRO",
        "Low, enclosed, sparse",
        "A calm and intimate beginning to the spatial experience.",
        ["Low ceiling", "Minimal elements", "Soft lighting"],
        "#ffb454",
        [18, 26, 20, 30, 22, 16],
    ),
    (
        "02", "RHYTHM",
        "Repetitive ribs and frames",
        "A dynamic space shaped by rhythm and repetition.",
        ["Structured ribs", "Regular spacing", "Linear movement"],
        "#4f8cff",
        [62] * 8,
    ),
    (
        "03", "HARMONY",
        "Layered and overlapping spaces",
        "A more complex space with layered volumes.",
        ["Multiple layers", "Varying heights", "Visual connections"],
        "#9b6bff",
        [40, 78, 55, 92, 48, 70],
    ),
    (
        "04", "CLIMAX",
        "Tall, expansive, expressive volume",
        "The highlight of the experience.",
        ["Greater height", "Bold forms", "Dramatic lighting"],
        "#ff2d55",
        [22, 48, 100, 64, 96, 42, 26],
    ),
    (
        "05", "OUTRO",
        "Gradually simpler and more open",
        "A calming conclusion to the journey.",
        ["Open space", "Fewer elements", "Soft finish"],
        "#3fd6a0",
        [92, 76, 62, 48, 34, 22, 12],
    ),
]

# ── architectural detail per zone ─────────────────────────────────────────────
ZONE_ARCH = {
    "INTRO":   ("Soft glowing membrane",   "Few slender ribs",         "Warm amber",  "30% of normal"),
    "RHYTHM":  ("Dense twisted plank ribs", "Woven diagonal strands",   "Blue",        "Beat-synced"),
    "HARMONY": ("Overlapping petal shells", "Layered glass skin",        "Violet",      "Sustained"),
    "CLIMAX":  ("Tree columns",             "Shingled roof + spires",    "Red pulse",   "Tallest (×1.4)"),
    "OUTRO":   ("Ribs dissolve open",       "Fading structure",          "Green fade",  "Gradual drop"),
}

# ── CSS for the zones table ───────────────────────────────────────────────────
TABLE_CSS = """
<style>
.zt-wrap{width:100%;border-collapse:separate;border-spacing:0;font-family:'Inter',sans-serif;font-size:.93rem}
.zt-wrap thead tr th{
  padding:.6rem 1rem;
  color:#a79fc0;font-weight:500;letter-spacing:.08em;text-transform:uppercase;font-size:.75rem;
  border-bottom:1px solid rgba(255,255,255,.12);
  background:rgba(255,255,255,.03);
  position:sticky;top:0;
}
.zt-wrap tbody tr{transition:background .2s}
.zt-wrap tbody tr:hover{background:rgba(255,255,255,.04)}
.zt-wrap td{padding:.85rem 1rem;border-bottom:1px solid rgba(255,255,255,.06);vertical-align:top}
.zt-num{font-family:'Syne',sans-serif;font-weight:800;font-size:2.4rem;line-height:1;
        color:transparent;-webkit-text-stroke:1.5px var(--zc)}
.zt-name{font-family:'Syne',sans-serif;font-weight:700;font-size:1.15rem;color:var(--zc);margin:.1rem 0 .15rem}
.zt-sub{color:#a79fc0;font-size:.8rem;font-style:italic}
.zt-desc{color:#d6d0f0;line-height:1.55;margin-bottom:.5rem}
.zt-bullets{list-style:none;padding:0;margin:0}
.zt-bullets li{color:#b9b1d3;font-size:.85rem;padding:.12rem 0}
.zt-bullets li::before{content:"● ";color:var(--zc);font-size:.65rem;vertical-align:middle}
.zt-arch-label{font-size:.75rem;color:#a79fc0;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.25rem}
.zt-arch-val{font-size:.88rem;color:#e0dbf5}
.zt-badge{display:inline-block;padding:.18rem .6rem;border-radius:999px;
          border:1px solid var(--zc);color:var(--zc);font-size:.75rem;margin:.15rem .15rem 0 0}
.zt-bar-wrap{display:flex;align-items:flex-end;gap:3px;height:52px;padding:.2rem 0}
.zt-bar{border-radius:2px 2px 0 0;width:12px;min-height:3px;opacity:.85}
.zone-section{margin-top:3rem}
.zone-section .reveal{opacity:0;transform:translateY(32px);transition:opacity .8s ease,transform .8s ease}
</style>
"""

# ── build bar SVG for the table ───────────────────────────────────────────────
def bar_svg(heights, color):
    bars = "".join(
        f'<div class="zt-bar" style="height:{max(4,int(h*52/100))}px;background:{color}"></div>'
        for h in heights
    )
    return f'<div class="zt-bar-wrap">{bars}</div>'


# ── build the full HTML table ─────────────────────────────────────────────────
def zones_table_html():
    rows = ""
    for num, name, subtitle, desc, bullets, color, bar_hs in ZONES_TABLE:
        arch = ZONE_ARCH[name]
        bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
        badge_html  = "".join(f'<span class="zt-badge">{a}</span>' for a in arch)
        rows += f"""
        <tr style="--zc:{color}">
          <td style="min-width:140px">
            <div class="zt-num">{num}</div>
            <div class="zt-name">{name}</div>
            <div class="zt-sub">{subtitle}</div>
          </td>
          <td style="max-width:260px">
            <div class="zt-desc">{desc}</div>
            <ul class="zt-bullets">{bullet_html}</ul>
          </td>
          <td style="min-width:120px">
            {bar_svg(bar_hs, color)}
          </td>
          <td style="min-width:200px">
            <div class="zt-arch-label">Architectural pattern</div>
            <div style="margin-top:.3rem">{badge_html}</div>
          </td>
        </tr>"""

    return f"""{TABLE_CSS}
<div class="zone-section reveal">
  <table class="zt-wrap">
    <thead>
      <tr>
        <th>Zone</th>
        <th>Spatial Character</th>
        <th>Energy Profile</th>
        <th>Architectural Pattern</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</div>"""


# ── render table ──────────────────────────────────────────────────────────────
st.markdown(zones_table_html(), unsafe_allow_html=True)

# ── scrolling marquee ─────────────────────────────────────────────────────────
st.markdown(
    g.band("INTRO RHYTHM HARMONY CLIMAX OUTRO "),
    unsafe_allow_html=True,
)

# ── detailed zone cards ───────────────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal" style="margin-top:3rem">Deep dive</div>'
    '<h2 class="reveal disp" style="font-size:clamp(1.6rem,4vw,2.6rem);margin-bottom:1.2rem">'
    'Each zone in detail</h2>',
    unsafe_allow_html=True,
)

cols = st.columns(5)
for col, (num, name, subtitle, desc, bullets, color, bar_hs) in zip(cols, ZONES_TABLE):
    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
    card_html = f"""
    <div class="card tilt reveal" style="--c:{color};height:100%">
      <div class="num">{num}</div>
      <h3 style="color:{color};font-family:'Syne',sans-serif;margin:.3rem 0 .2rem">{name}</h3>
      <p style="color:#a79fc0;font-size:.8rem;margin:0 0 .6rem">{subtitle}</p>
      {g.bars(bar_hs, color)}
      <p style="margin:.5rem 0 .4rem;font-size:.88rem;color:#d6d0f0">{desc}</p>
      <ul class="zt-bullets" style="list-style:none;padding:0;margin:0">
        {bullet_html}
      </ul>
    </div>"""
    col.markdown(card_html, unsafe_allow_html=True)

# ── pipeline callout ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="card reveal" style="margin-top:2.5rem;text-align:center">'
    '<div class="eyebrow" style="margin-top:0">How zones are found</div>'
    '<p class="lead" style="margin:0 auto;max-width:60rem">'
    'The first 15% of the song becomes <span style="color:#ffb454">Intro</span>. '
    'The last 15% is <span style="color:#3fd6a0">Outro</span>. '
    'The loudest 15% window in the middle (biased late) is '
    '<span style="color:#ff2d55">Climax</span>. '
    'Remaining segments with above-median note density become '
    '<span style="color:#4f8cff">Rhythm</span>; '
    'below-median become <span style="color:#9b6bff">Harmony</span>. '
    'A 5-segment majority filter smooths the boundaries so zones stay connected.'
    '</p></div>',
    unsafe_allow_html=True,
)

# ── nav links ─────────────────────────────────────────────────────────────────
st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.page_link("views/studio.py",  label="Open the Studio")
c2.page_link("views/gallery.py", label="Browse the Gallery")
c3.page_link("views/method.py",  label="See the Method")
