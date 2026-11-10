"""Zones page — Five-Zone Spatial Journey with SVG zone previews from real segment data."""
import math
import streamlit as st
from ui import graphics as g

# ── static zone metadata ──────────────────────────────────────────────────────
ZONE_META = {
    "intro":   ("01", "INTRO",   "Low, enclosed, sparse",
                "A calm and intimate beginning to the spatial experience.",
                ["Low ceiling", "Minimal elements", "Soft lighting"],
                "#ffb454"),
    "rhythm":  ("02", "RHYTHM",  "Repetitive ribs and frames",
                "A dynamic space shaped by rhythm and repetition.",
                ["Structured ribs", "Regular spacing", "Linear movement"],
                "#4f8cff"),
    "harmony": ("03", "HARMONY", "Layered and overlapping spaces",
                "A more complex space with layered volumes.",
                ["Multiple layers", "Varying heights", "Visual connections"],
                "#9b6bff"),
    "climax":  ("04", "CLIMAX",  "Tall, expansive, expressive volume",
                "The highlight of the experience.",
                ["Greater height", "Bold forms", "Dramatic lighting"],
                "#ff2d55"),
    "outro":   ("05", "OUTRO",   "Gradually simpler and more open",
                "A calming conclusion to the journey.",
                ["Open space", "Fewer elements", "Soft finish"],
                "#3fd6a0"),
}
ZONE_ORDER = ["intro", "rhythm", "harmony", "climax", "outro"]

MAT_COLOR = {"concrete": "#9a9690", "wood": "#c68a4b", "glass": "#9fd8ee"}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- table ---- */
.zt-wrap{width:100%;border-collapse:separate;border-spacing:0 8px;font-family:'Inter',sans-serif}
.zt-wrap thead th{
  padding:.5rem 1rem;color:#a79fc0;font-weight:500;
  letter-spacing:.08em;text-transform:uppercase;font-size:.7rem;
  border-bottom:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03)
}
.zt-wrap tbody tr td{
  padding:.85rem 1rem;
  border-top:1px solid rgba(255,255,255,.06);
  border-bottom:1px solid rgba(255,255,255,.06);
  vertical-align:middle;background:rgba(255,255,255,.02);
  transition:background .2s
}
.zt-wrap tbody tr:hover td{background:rgba(255,255,255,.05)}
.zt-wrap tbody tr td:first-child{
  border-left:3px solid var(--zc);border-radius:12px 0 0 12px
}
.zt-wrap tbody tr td:last-child{border-radius:0 12px 12px 0}
/* ---- zone id ---- */
.zt-num{font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;line-height:1;
        color:transparent;-webkit-text-stroke:1.5px var(--zc)}
.zt-name{font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:var(--zc);margin:.1rem 0 .12rem}
.zt-sub{color:#a79fc0;font-size:.75rem;font-style:italic}
/* ---- description ---- */
.zt-desc{color:#d6d0f0;line-height:1.5;font-size:.85rem;margin-bottom:.4rem}
.zt-bullets{list-style:none;padding:0;margin:0}
.zt-bullets li{color:#b9b1d3;font-size:.8rem;padding:.07rem 0}
.zt-bullets li::before{content:"● ";color:var(--zc);font-size:.58rem;vertical-align:middle}
/* ---- stat cell ---- */
.zt-stat{text-align:center}
.zt-stat b{display:block;font-family:'Syne';font-size:1.4rem;color:var(--zc)}
.zt-stat span{color:#a79fc0;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase}
/* ---- badge ---- */
.zt-badge{display:inline-block;padding:.13rem .5rem;border-radius:999px;
          border:1px solid var(--zc);color:var(--zc);font-size:.7rem;margin:.1rem .1rem 0 0}
/* ---- svg preview ---- */
.zt-svg-wrap{background:#0d0f1a;border-radius:10px;overflow:hidden;
             border:1px solid rgba(255,255,255,.08);line-height:0}
/* ---- no song ---- */
.no-song{text-align:center;padding:3rem 2rem;color:#a79fc0;
         border:1px dashed rgba(255,255,255,.15);border-radius:16px;margin-top:2rem}
.no-song b{display:block;font-family:'Syne';font-size:1.6rem;color:#ff2d55;margin-bottom:.5rem}
</style>
""", unsafe_allow_html=True)

# ── page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal">From Music to Architecture</div>'
    '<h1 class="reveal disp" style="font-size:clamp(2rem,5vw,3.4rem);margin-bottom:.3rem">'
    'Five-Zone <strong>Spatial Journey</strong></h1>'
    '<p class="lead reveal" style="margin-bottom:2rem">'
    'Each section of your song becomes a distinct architectural zone — '
    'with its own geometry, material and light drawn directly from the music.</p>',
    unsafe_allow_html=True,
)

# ── pull arch from session state ──────────────────────────────────────────────
arch      = st.session_state.get("arch")
song_name = st.session_state.get("song_name", "Your song")

if not arch or not arch.get("segments"):
    st.markdown(
        '<div class="no-song">'
        '<b>No song analysed yet</b>'
        'Go to <b>Studio</b>, upload a track (or tick demo data), '
        'then come back here to see your song\'s zones.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("views/studio.py", label="Open the Studio")
    st.stop()

segs = arch["segments"]

# ── helpers ───────────────────────────────────────────────────────────────────
fmt = lambda x: f"{int(x//60)}:{int(x%60):02d}"

def zone_segs(zname):
    return [s for s in segs if s["zone"] == zname]

def zone_stats(zname):
    z = zone_segs(zname)
    if not z:
        return None
    avg = lambda k: sum(s[k] for s in z) / len(z)
    mats = {}
    for s in z:
        mats[s["material"]] = mats.get(s["material"], 0) + 1
    return {
        "rooms":      len(z),
        "avg_height": avg("height"),
        "avg_length": avg("length"),
        "avg_open":   avg("openness"),
        "avg_light":  avg("light"),
        "total_ribs": sum(s["ribs"] for s in z),
        "start_t":    min(s["start_time"] for s in z),
        "end_t":      max(s["start_time"] + s["duration"] for s in z),
        "material":   max(mats, key=mats.get),
        "pattern":    z[0].get("pattern", "woven lattice"),
        "pitch_norm": [s["norm"]["pitch"] for s in z],
        "open_norm":  [s["openness"] for s in z],
        "segs":       z,
    }

# ── SVG zone preview generator ────────────────────────────────────────────────
def zone_svg(zname, stats, color, W=320, H=160):
    """
    Draws a combined longitudinal section + cross-section of the zone,
    computed from real segment data — matches the Three.js scene geometry.
    """
    if stats is None:
        return f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}"><text x="50%" y="50%" fill="#444" text-anchor="middle" font-size="12">No data</text></svg>'

    z      = stats["segs"]
    mat    = stats["material"]
    mcol   = MAT_COLOR.get(mat, "#aaa")
    glow   = color
    n      = len(z)
    # --- sky / background ---
    parts  = [
        f'<defs>',
        f'<linearGradient id="sky{zname}" x1="0" y1="0" x2="0" y2="1">',
        f'  <stop offset="0%" stop-color="#05060f"/>',
        f'  <stop offset="100%" stop-color="#10131c"/>',
        f'</linearGradient>',
        f'<radialGradient id="lg{zname}" cx="50%" cy="100%" r="60%">',
        f'  <stop offset="0%" stop-color="{glow}" stop-opacity="0.35"/>',
        f'  <stop offset="100%" stop-color="{glow}" stop-opacity="0"/>',
        f'</radialGradient>',
        f'</defs>',
        f'<rect width="{W}" height="{H}" fill="url(#sky{zname})"/>',
        f'<rect width="{W}" height="{H}" fill="url(#lg{zname})"/>',
    ]

    # --- floor ---
    parts.append(f'<rect x="0" y="{H-14}" width="{W}" height="14" fill="#1a1d2a" rx="0"/>')
    parts.append(f'<rect x="0" y="{H-14}" width="{W}" height="1" fill="{glow}" opacity="0.4"/>')

    # --- longitudinal section: arch silhouette across all rooms ---
    # map rooms left-to-right
    total_len = sum(s["length"] for s in z) or 1
    px = 10
    floor_y = H - 14
    max_h_px = H - 24   # max drawable height in px
    global_max_h = max(s["height"] for s in segs) or 1

    arch_pts = [(px, floor_y)]
    for s in z:
        rw  = (s["length"] / total_len) * (W - 20)
        rh  = (s["height"] / global_max_h) * max_h_px
        cx  = px + rw / 2
        # arch peak
        peak_y = floor_y - rh
        # left base, peak, right base
        arch_pts.append((px, floor_y))
        arch_pts.append((cx, peak_y))
        arch_pts.append((px + rw, floor_y))
        px += rw
    arch_pts.append((px, floor_y))

    # smooth silhouette path using quadratic bezier
    path_d = f"M {arch_pts[0][0]:.1f},{arch_pts[0][1]:.1f}"
    i = 1
    while i < len(arch_pts) - 1:
        mx = (arch_pts[i][0] + arch_pts[i+1][0]) / 2
        my = (arch_pts[i][1] + arch_pts[i+1][1]) / 2
        path_d += f" Q {arch_pts[i][0]:.1f},{arch_pts[i][1]:.1f} {mx:.1f},{my:.1f}"
        i += 1
    path_d += f" L {W-10:.1f},{floor_y}"
    path_d += f" L 10,{floor_y} Z"

    # filled silhouette
    parts.append(f'<path d="{path_d}" fill="{mcol}" opacity="0.18"/>')
    # outline
    outline_d = path_d.split(" L ")[0]  # just the arch part without close
    parts.append(f'<path d="{outline_d}" fill="none" stroke="{glow}" stroke-width="1.5" opacity="0.9" stroke-linejoin="round"/>')

    # --- ribs: vertical lines inside the silhouette ---
    px = 10
    for s in z:
        rw = (s["length"] / total_len) * (W - 20)
        rh = (s["height"] / global_max_h) * max_h_px
        ribs = max(1, s["ribs"])
        for r in range(ribs + 1):
            rx = px + (r / ribs) * rw
            # rib height follows arch curve (parabola)
            t_   = r / ribs
            ry   = rh * (1 - (2 * t_ - 1) ** 2)  # parabola
            rib_top = floor_y - ry
            parts.append(
                f'<line x1="{rx:.1f}" y1="{floor_y}" x2="{rx:.1f}" y2="{rib_top:.1f}" '
                f'stroke="{glow}" stroke-width="0.7" opacity="0.35"/>'
            )
        px += rw

    # --- cross-section: arch in the right corner ---
    # pick the representative segment (median height)
    rep = sorted(z, key=lambda s: s["height"])[len(z)//2]
    cs_x, cs_y = W - 90, floor_y
    cs_w = 76
    cs_h = (rep["height"] / global_max_h) * max_h_px
    cs_open = rep["openness"]

    # arch curve: semi-ellipse
    n_pts = 24
    arch_path = " ".join(
        f"{cs_x + cs_w/2 + (cs_w/2)*math.sin(i*math.pi/(n_pts-1)):.1f},"
        f"{cs_y - cs_h * math.sin(i*math.pi/(n_pts-1)) * (1 - 0.3*abs(math.cos(i*math.pi/(n_pts-1)))):.1f}"
        for i in range(n_pts)
    )
    cs_path = f"M {cs_x:.1f},{cs_y} L " + arch_path + f" L {cs_x+cs_w:.1f},{cs_y} Z"

    # walls (opacity driven by openness)
    wall_op = max(0.08, 0.6 - cs_open * 0.5)
    parts.append(f'<path d="{cs_path}" fill="{mcol}" opacity="{wall_op:.2f}"/>')
    parts.append(f'<path d="M {cs_x:.1f},{cs_y} L " + "{arch_path}" + " L {cs_x+cs_w:.1f},{cs_y}" fill="none" stroke="{glow}" stroke-width="1.8" opacity="0.95"/>')

    # cross-section ribs
    n_ribs = max(1, min(rep["ribs"], 6))
    for r in range(n_ribs + 1):
        angle = r * math.pi / n_ribs
        rx = cs_x + cs_w/2 + (cs_w/2) * math.sin(angle)
        ry = cs_y - cs_h * math.sin(angle) * (1 - 0.3 * abs(math.cos(angle)))
        parts.append(
            f'<line x1="{cs_x + cs_w/2:.1f}" y1="{cs_y - cs_h * 0.1:.1f}" '
            f'x2="{rx:.1f}" y2="{ry:.1f}" '
            f'stroke="{glow}" stroke-width="1" opacity="0.4"/>'
        )

    # cross-section label
    parts.append(f'<text x="{cs_x + cs_w/2:.1f}" y="{cs_y - cs_h - 6:.1f}" '
                 f'fill="{glow}" font-size="8" text-anchor="middle" opacity="0.7" font-family="system-ui">section</text>')

    # climax spires
    if zname == "climax":
        for i in range(3):
            sx = cs_x + 10 + i * 28
            parts.append(f'<polygon points="{sx},{cs_y-4} {sx+5},{cs_y-cs_h*0.6} {sx+10},{cs_y-4}" fill="{glow}" opacity="0.5"/>')

    # harmony double-layer ghost
    if zname == "harmony":
        ghost_path = f"M {cs_x+5:.1f},{cs_y-4} " + " ".join(
            f"{cs_x+5 + (cs_w-10)/2 + (cs_w-10)/2*math.sin(i*math.pi/(n_pts-1)):.1f},"
            f"{cs_y - cs_h*0.75*math.sin(i*math.pi/(n_pts-1)):.1f}"
            for i in range(n_pts)
        ) + f" L {cs_x+cs_w-5:.1f},{cs_y-4}"
        parts.append(f'<path d="{ghost_path}" fill="none" stroke="{glow}" stroke-width="1" stroke-dasharray="3,3" opacity="0.45"/>')

    # human figure scale
    fig_x = cs_x - 14
    fig_h = min(cs_h, max_h_px) * 0.28
    fig_y = cs_y
    parts.append(
        f'<line x1="{fig_x:.1f}" y1="{fig_y}" x2="{fig_x:.1f}" y2="{fig_y - fig_h:.1f}" '
        f'stroke="#c0b8d8" stroke-width="1.5" opacity="0.5"/>'
        f'<circle cx="{fig_x:.1f}" cy="{fig_y - fig_h - 3:.1f}" r="2.5" fill="#c0b8d8" opacity="0.5"/>'
    )

    # zone label bottom-left
    parts.append(
        f'<text x="14" y="{H-20}" fill="{glow}" font-size="9" font-family="system-ui" '
        f'font-weight="700" letter-spacing="1" opacity="0.85">'
        f'{zname.upper()}</text>'
    )

    return f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'

# ── build the main table ──────────────────────────────────────────────────────
tempo  = arch.get("tempo", "—")
n_segs = len(segs)
end_t  = segs[-1]["start_time"] + segs[-1]["duration"]

st.markdown(
    f'<p class="lead reveal" style="margin-bottom:1.5rem">'
    f'<b style="color:#ff2d55">{song_name}</b> — '
    f'{n_segs} spaces &nbsp;·&nbsp; {tempo} BPM &nbsp;·&nbsp; {fmt(end_t)} walk</p>',
    unsafe_allow_html=True,
)

rows_html = ""
for zname in ZONE_ORDER:
    num, name, subtitle, desc, bullets, color = ZONE_META[zname]
    stats = zone_stats(zname)
    if stats is None:
        continue

    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
    svg_preview = zone_svg(zname, stats, color)

    rows_html += f"""
    <tr style="--zc:{color}">
      <td style="min-width:120px;width:120px">
        <div class="zt-num">{num}</div>
        <div class="zt-name">{name}</div>
        <div class="zt-sub">{subtitle}</div>
      </td>
      <td style="max-width:200px">
        <div class="zt-desc">{desc}</div>
        <ul class="zt-bullets">{bullet_html}</ul>
      </td>
      <td style="width:330px;padding:.6rem">
        <div class="zt-svg-wrap">{svg_preview}</div>
      </td>
      <td class="zt-stat" style="width:80px">
        <b>{stats['rooms']}</b><span>Spaces</span>
      </td>
      <td class="zt-stat" style="width:90px">
        <b>{stats['avg_height']:.1f} m</b><span>Avg height</span>
      </td>
      <td class="zt-stat" style="width:80px">
        <b>{int(stats['avg_open']*100)}%</b><span>Openness</span>
      </td>
      <td class="zt-stat" style="width:80px">
        <b>{stats['total_ribs']}</b><span>Arches</span>
      </td>
      <td style="min-width:160px">
        <span class="zt-badge">{stats['material']}</span><br>
        <span class="zt-badge" style="margin-top:.3rem">{stats['pattern']}</span><br>
        <span style="color:#a79fc0;font-size:.75rem;display:block;margin-top:.4rem">
          {fmt(stats['start_t'])} – {fmt(stats['end_t'])}
        </span>
      </td>
    </tr>"""

st.markdown(f"""
<div class="reveal" style="overflow-x:auto">
<table class="zt-wrap">
  <thead>
    <tr>
      <th>Zone</th>
      <th>Spatial Character</th>
      <th>3D Section Preview</th>
      <th>Spaces</th>
      <th>Avg Height</th>
      <th>Openness</th>
      <th>Arches</th>
      <th>Material · Pattern · Time</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── marquee ───────────────────────────────────────────────────────────────────
st.markdown(g.band("INTRO RHYTHM HARMONY CLIMAX OUTRO "), unsafe_allow_html=True)

# ── zone cards ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal" style="margin-top:2.5rem">Zone breakdown</div>'
    '<h2 class="reveal disp" style="font-size:clamp(1.5rem,4vw,2.4rem);margin-bottom:1.2rem">'
    'Your song\'s five zones</h2>',
    unsafe_allow_html=True,
)

cols = st.columns(5)
for col, zname in zip(cols, ZONE_ORDER):
    num, name, subtitle, desc, bullets, color = ZONE_META[zname]
    stats = zone_stats(zname)

    if stats is None:
        col.markdown(
            f'<div class="card" style="--c:{color};opacity:.3;text-align:center">'
            f'<div class="zt-num" style="--zc:{color}">{num}</div>'
            f'<div class="zt-name" style="color:{color}">{name}</div>'
            f'<p style="color:#a79fc0;font-size:.8rem">Not present</p></div>',
            unsafe_allow_html=True,
        )
        continue

    svg_card = zone_svg(zname, stats, color, W=240, H=120)
    bullet_html = "".join(f"<li>{b}</li>" for b in bullets[:3])

    col.markdown(f"""
    <div class="card tilt reveal" style="--c:{color};padding:1rem">
      <div style="--zc:{color}">
        <div class="zt-num" style="font-size:1.5rem">{num}</div>
        <div class="zt-name" style="font-size:.95rem">{name}</div>
        <div class="zt-sub" style="font-size:.72rem;margin-bottom:.5rem">{subtitle}</div>
      </div>
      <div class="zt-svg-wrap" style="margin-bottom:.6rem">{svg_card}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.25rem;margin-bottom:.5rem">
        <div style="background:rgba(255,255,255,.04);border-radius:7px;padding:.3rem;text-align:center">
          <b style="font-family:Syne;font-size:1.1rem;color:{color}">{stats['rooms']}</b>
          <span style="color:#a79fc0;font-size:.62rem;display:block;text-transform:uppercase">Spaces</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:7px;padding:.3rem;text-align:center">
          <b style="font-family:Syne;font-size:1.1rem;color:{color}">{stats['avg_height']:.1f}m</b>
          <span style="color:#a79fc0;font-size:.62rem;display:block;text-transform:uppercase">Height</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:7px;padding:.3rem;text-align:center">
          <b style="font-family:Syne;font-size:1.1rem;color:{color}">{int(stats['avg_open']*100)}%</b>
          <span style="color:#a79fc0;font-size:.62rem;display:block;text-transform:uppercase">Open</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:7px;padding:.3rem;text-align:center">
          <b style="font-family:Syne;font-size:1.1rem;color:{color}">{stats['total_ribs']}</b>
          <span style="color:#a79fc0;font-size:.62rem;display:block;text-transform:uppercase">Arches</span>
        </div>
      </div>
      <ul class="zt-bullets" style="--zc:{color}">{bullet_html}</ul>
      <p style="color:#a79fc0;font-size:.72rem;margin:.5rem 0 0">
        {fmt(stats['start_t'])} – {fmt(stats['end_t'])}
      </p>
    </div>""", unsafe_allow_html=True)

# ── pipeline callout ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="card reveal" style="margin-top:2.5rem;text-align:center">'
    '<div class="eyebrow" style="margin-top:0">How zones are found</div>'
    '<p class="lead" style="margin:0 auto;max-width:60rem">'
    'First 15% → <span style="color:#ffb454">Intro</span> &nbsp;·&nbsp; '
    'Last 15% → <span style="color:#3fd6a0">Outro</span> &nbsp;·&nbsp; '
    'Loudest 15% window → <span style="color:#ff2d55">Climax</span> &nbsp;·&nbsp; '
    'Above-median density → <span style="color:#4f8cff">Rhythm</span> &nbsp;·&nbsp; '
    'Below-median → <span style="color:#9b6bff">Harmony</span>'
    '</p></div>',
    unsafe_allow_html=True,
)

st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.page_link("views/studio.py",  label="Back to Studio")
c2.page_link("views/gallery.py", label="Browse Gallery")
c3.page_link("views/method.py",  label="See the Method")
