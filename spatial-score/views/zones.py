"""Zones page — Five-Zone Spatial Journey for the analysed song."""
import streamlit as st
from ui import graphics as g

# ── static zone metadata (reference card data) ───────────────────────────────
ZONE_META = {
    "intro":   ("01", "INTRO",   "Low, enclosed, sparse",
                "A calm and intimate beginning to the spatial experience.",
                ["Low ceiling", "Minimal elements", "Soft lighting"],
                "#ffb454", [18, 26, 20, 30, 22, 16]),
    "rhythm":  ("02", "RHYTHM",  "Repetitive ribs and frames",
                "A dynamic space shaped by rhythm and repetition.",
                ["Structured ribs", "Regular spacing", "Linear movement"],
                "#4f8cff", [62] * 8),
    "harmony": ("03", "HARMONY", "Layered and overlapping spaces",
                "A more complex space with layered volumes.",
                ["Multiple layers", "Varying heights", "Visual connections"],
                "#9b6bff", [40, 78, 55, 92, 48, 70]),
    "climax":  ("04", "CLIMAX",  "Tall, expansive, expressive volume",
                "The highlight of the experience.",
                ["Greater height", "Bold forms", "Dramatic lighting"],
                "#ff2d55", [22, 48, 100, 64, 96, 42, 26]),
    "outro":   ("05", "OUTRO",   "Gradually simpler and more open",
                "A calming conclusion to the journey.",
                ["Open space", "Fewer elements", "Soft finish"],
                "#3fd6a0", [92, 76, 62, 48, 34, 22, 12]),
}
ZONE_ORDER = ["intro", "rhythm", "harmony", "climax", "outro"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.zt-wrap{width:100%;border-collapse:separate;border-spacing:0 6px;font-family:'Inter',sans-serif}
.zt-wrap thead th{
  padding:.55rem 1rem;color:#a79fc0;font-weight:500;
  letter-spacing:.08em;text-transform:uppercase;font-size:.72rem;
  border-bottom:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03)
}
.zt-wrap tbody tr{transition:background .2s;border-radius:12px}
.zt-wrap tbody tr:hover td{background:rgba(255,255,255,.045)}
.zt-wrap td{
  padding:.9rem 1rem;border-top:1px solid rgba(255,255,255,.06);
  border-bottom:1px solid rgba(255,255,255,.06);vertical-align:middle
}
.zt-wrap td:first-child{border-left:3px solid var(--zc);border-radius:10px 0 0 10px}
.zt-wrap td:last-child{border-radius:0 10px 10px 0}
.zt-num{font-family:'Syne',sans-serif;font-weight:800;font-size:2rem;line-height:1;
        color:transparent;-webkit-text-stroke:1.5px var(--zc)}
.zt-name{font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:var(--zc);margin:.1rem 0 .15rem}
.zt-sub{color:#a79fc0;font-size:.78rem;font-style:italic}
.zt-desc{color:#d6d0f0;line-height:1.5;font-size:.88rem;margin-bottom:.4rem}
.zt-bullets{list-style:none;padding:0;margin:0}
.zt-bullets li{color:#b9b1d3;font-size:.82rem;padding:.08rem 0}
.zt-bullets li::before{content:"● ";color:var(--zc);font-size:.6rem;vertical-align:middle}
.zt-stat{text-align:center;padding:.4rem .6rem}
.zt-stat b{display:block;font-family:'Syne';font-size:1.5rem;color:var(--zc)}
.zt-stat span{color:#a79fc0;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase}
.zt-bar-wrap{display:flex;align-items:flex-end;gap:3px;height:48px}
.zt-bar{border-radius:2px 2px 0 0;width:10px;min-height:3px;opacity:.8;transition:height .4s}
.zt-badge{display:inline-block;padding:.15rem .55rem;border-radius:999px;
          border:1px solid var(--zc);color:var(--zc);font-size:.72rem;margin:.12rem .12rem 0 0}
.no-song{text-align:center;padding:3rem 2rem;color:#a79fc0;font-size:1rem;
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
    'Each section of the song becomes a distinct architectural zone. '
    'Upload a track in <b>Studio</b> to see your song\'s zones here.</p>',
    unsafe_allow_html=True,
)

# ── pull arch data from session state ─────────────────────────────────────────
arch = st.session_state.get("arch")

if not arch or not arch.get("segments"):
    st.markdown(
        '<div class="no-song">'
        '<b>No song analysed yet</b>'
        'Go to the <b>Studio</b> page, upload a track (or use demo data), '
        'and your song\'s five zones will appear here.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("views/studio.py", label="Open the Studio")
    st.stop()

segs = arch["segments"]
song_name = st.session_state.get("song_name", "Your song")

# ── compute per-zone stats from real segment data ─────────────────────────────
def zone_stats(zone_name):
    z = [s for s in segs if s["zone"] == zone_name]
    if not z:
        return None
    avg = lambda k: sum(s[k] for s in z) / len(z)
    start_t = min(s["start_time"] for s in z)
    end_t   = max(s["start_time"] + s["duration"] for s in z)
    mats    = {}
    for s in z:
        mats[s["material"]] = mats.get(s["material"], 0) + 1
    dominant_mat = max(mats, key=mats.get)
    # build bar heights from real pitch norms of segments in this zone
    pitch_vals = [int(s["norm"]["pitch"] * 100) for s in z]
    # downsample/upsample to 8 bars
    target = 8
    if len(pitch_vals) >= target:
        step = len(pitch_vals) / target
        bars = [pitch_vals[int(i * step)] for i in range(target)]
    else:
        bars = pitch_vals + [pitch_vals[-1]] * (target - len(pitch_vals))
    return {
        "rooms":       len(z),
        "avg_height":  avg("height"),
        "avg_length":  avg("length"),
        "avg_open":    avg("openness"),
        "avg_light":   avg("light"),
        "total_ribs":  sum(s["ribs"] for s in z),
        "start_t":     start_t,
        "end_t":       end_t,
        "material":    dominant_mat,
        "bars":        bars,
    }

# ── header info row ───────────────────────────────────────────────────────────
tempo  = arch.get("tempo", "—")
n_segs = len(segs)
fmt    = lambda x: f"{int(x//60)}:{int(x%60):02d}"
end_t  = segs[-1]["start_time"] + segs[-1]["duration"]

st.markdown(
    f'<p class="lead reveal" style="margin-bottom:1.5rem">'
    f'<b style="color:#ff2d55">{song_name}</b> — '
    f'{n_segs} spaces &nbsp;·&nbsp; {tempo} BPM &nbsp;·&nbsp; {fmt(end_t)} walk length</p>',
    unsafe_allow_html=True,
)

# ── build the zones table ─────────────────────────────────────────────────────
def bar_divs(heights, color):
    divs = "".join(
        f'<div class="zt-bar" style="height:{max(4, int(h * 48 / 100))}px;background:{color}"></div>'
        for h in heights
    )
    return f'<div class="zt-bar-wrap">{divs}</div>'

rows_html = ""
for zname in ZONE_ORDER:
    num, name, subtitle, desc, bullets, color, _default_bars = ZONE_META[zname]
    stats = zone_stats(zname)
    if stats is None:
        continue

    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
    bars        = bar_divs(stats["bars"], color)
    mat_badge   = f'<span class="zt-badge">{stats["material"]}</span>'
    pat_badge   = f'<span class="zt-badge">{arch["segments"][0].get("pattern","—") if segs else "—"}</span>'
    # get pattern from first segment in zone
    z_segs = [s for s in segs if s["zone"] == zname]
    pattern = z_segs[0].get("pattern", "—") if z_segs else "—"

    rows_html += f"""
    <tr style="--zc:{color}">
      <td style="min-width:130px">
        <div class="zt-num">{num}</div>
        <div class="zt-name">{name}</div>
        <div class="zt-sub">{subtitle}</div>
      </td>
      <td style="max-width:220px">
        <div class="zt-desc">{desc}</div>
        <ul class="zt-bullets">{bullet_html}</ul>
      </td>
      <td class="zt-stat">
        <b>{stats['rooms']}</b><span>Spaces</span>
      </td>
      <td class="zt-stat">
        <b>{stats['avg_height']:.1f} m</b><span>Avg height</span>
      </td>
      <td class="zt-stat">
        <b>{int(stats['avg_open']*100)}%</b><span>Openness</span>
      </td>
      <td class="zt-stat">
        <b>{stats['total_ribs']}</b><span>Total arches</span>
      </td>
      <td style="min-width:110px">
        {bars}
      </td>
      <td style="min-width:160px">
        <span class="zt-badge">{stats['material']}</span>
        <span class="zt-badge">{pattern}</span>
        <span class="zt-badge">{fmt(stats['start_t'])} – {fmt(stats['end_t'])}</span>
      </td>
    </tr>"""

st.markdown(f"""
<div class="reveal" style="overflow-x:auto">
<table class="zt-wrap">
  <thead>
    <tr>
      <th>Zone</th>
      <th>Spatial Character</th>
      <th>Spaces</th>
      <th>Avg Height</th>
      <th>Openness</th>
      <th>Arches</th>
      <th>Pitch Profile</th>
      <th>Material · Pattern · Time</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── scrolling marquee ─────────────────────────────────────────────────────────
st.markdown(g.band("INTRO RHYTHM HARMONY CLIMAX OUTRO "), unsafe_allow_html=True)

# ── zone detail cards (real data) ────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal" style="margin-top:2.5rem">Zone breakdown</div>'
    '<h2 class="reveal disp" style="font-size:clamp(1.5rem,4vw,2.4rem);margin-bottom:1.2rem">'
    'Your song\'s five zones</h2>',
    unsafe_allow_html=True,
)

cols = st.columns(5)
for col, zname in zip(cols, ZONE_ORDER):
    num, name, subtitle, desc, bullets, color, _ = ZONE_META[zname]
    stats = zone_stats(zname)
    if stats is None:
        col.markdown(
            f'<div class="card" style="--c:{color};opacity:.35;text-align:center">'
            f'<div class="num">{num}</div>'
            f'<h3 style="color:{color};font-family:Syne">{name}</h3>'
            f'<p style="color:#a79fc0;font-size:.8rem">Not present in this song</p></div>',
            unsafe_allow_html=True,
        )
        continue

    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
    z_segs = [s for s in segs if s["zone"] == zname]
    pattern = z_segs[0].get("pattern", "—") if z_segs else "—"

    col.markdown(f"""
    <div class="card tilt reveal" style="--c:{color}">
      <div class="num">{num}</div>
      <h3 style="color:{color};font-family:'Syne',sans-serif;margin:.2rem 0 .15rem">{name}</h3>
      <p style="color:#a79fc0;font-size:.78rem;margin:0 0 .5rem">{subtitle}</p>
      {g.bars(stats['bars'], color)}
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.3rem;margin:.7rem 0 .5rem">
        <div class="zt-stat" style="background:rgba(255,255,255,.04);border-radius:8px;padding:.4rem">
          <b style="font-family:Syne;font-size:1.2rem;color:{color}">{stats['rooms']}</b>
          <span style="color:#a79fc0;font-size:.7rem;display:block;text-transform:uppercase;letter-spacing:.1em">Spaces</span>
        </div>
        <div class="zt-stat" style="background:rgba(255,255,255,.04);border-radius:8px;padding:.4rem">
          <b style="font-family:Syne;font-size:1.2rem;color:{color}">{stats['avg_height']:.1f}m</b>
          <span style="color:#a79fc0;font-size:.7rem;display:block;text-transform:uppercase;letter-spacing:.1em">Avg height</span>
        </div>
        <div class="zt-stat" style="background:rgba(255,255,255,.04);border-radius:8px;padding:.4rem">
          <b style="font-family:Syne;font-size:1.2rem;color:{color}">{int(stats['avg_open']*100)}%</b>
          <span style="color:#a79fc0;font-size:.7rem;display:block;text-transform:uppercase;letter-spacing:.1em">Openness</span>
        </div>
        <div class="zt-stat" style="background:rgba(255,255,255,.04);border-radius:8px;padding:.4rem">
          <b style="font-family:Syne;font-size:1.2rem;color:{color}">{stats['total_ribs']}</b>
          <span style="color:#a79fc0;font-size:.7rem;display:block;text-transform:uppercase;letter-spacing:.1em">Arches</span>
        </div>
      </div>
      <span class="zt-badge" style="--zc:{color}">{stats['material']}</span>
      <span class="zt-badge" style="--zc:{color}">{pattern}</span>
      <p style="color:#a79fc0;font-size:.75rem;margin:.5rem 0 0">
        {fmt(stats['start_t'])} – {fmt(stats['end_t'])}
      </p>
    </div>""", unsafe_allow_html=True)

# ── pipeline callout ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="card reveal" style="margin-top:2.5rem;text-align:center">'
    '<div class="eyebrow" style="margin-top:0">How zones are found</div>'
    '<p class="lead" style="margin:0 auto;max-width:60rem">'
    'The first 15% of the song → <span style="color:#ffb454">Intro</span>. '
    'Last 15% → <span style="color:#3fd6a0">Outro</span>. '
    'Loudest 15% window in the middle → <span style="color:#ff2d55">Climax</span>. '
    'Above-median note density → <span style="color:#4f8cff">Rhythm</span>. '
    'Below-median → <span style="color:#9b6bff">Harmony</span>.'
    '</p></div>',
    unsafe_allow_html=True,
)

# ── nav ───────────────────────────────────────────────────────────────────────
st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.page_link("views/studio.py",  label="Back to Studio")
c2.page_link("views/gallery.py", label="Browse Gallery")
c3.page_link("views/method.py",  label="See the Method")
