"""Zones page — Five-Zone Spatial Journey with live-rendered 3D model thumbnails."""
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

from ui import graphics as g

ROOT = Path(__file__).resolve().parent.parent

# ── static zone metadata ──────────────────────────────────────────────────────
ZONE_META = {
    "intro":   ("01", "INTRO",   "Low, enclosed, sparse",
                "A calm and intimate beginning to the spatial experience.",
                ["Low ceiling", "Minimal elements", "Soft lighting"], "#ffb454"),
    "rhythm":  ("02", "RHYTHM",  "Repetitive ribs and frames",
                "A dynamic space shaped by rhythm and repetition.",
                ["Structured ribs", "Regular spacing", "Linear movement"], "#4f8cff"),
    "harmony": ("03", "HARMONY", "Layered and overlapping spaces",
                "A more complex space with layered volumes.",
                ["Multiple layers", "Varying heights", "Visual connections"], "#9b6bff"),
    "climax":  ("04", "CLIMAX",  "Tall, expansive, expressive volume",
                "The highlight of the experience.",
                ["Greater height", "Bold forms", "Dramatic lighting"], "#ff2d55"),
    "outro":   ("05", "OUTRO",   "Gradually simpler and more open",
                "A calming conclusion to the journey.",
                ["Open space", "Fewer elements", "Soft finish"], "#3fd6a0"),
}
ZONE_ORDER = ["intro", "rhythm", "harmony", "climax", "outro"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.zt-wrap{width:100%;border-collapse:separate;border-spacing:0 8px;font-family:'Inter',sans-serif}
.zt-wrap thead th{
  padding:.5rem 1rem;color:#a79fc0;font-weight:500;
  letter-spacing:.08em;text-transform:uppercase;font-size:.7rem;
  border-bottom:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03)
}
.zt-wrap tbody tr td{
  padding:.8rem 1rem;
  border-top:1px solid rgba(255,255,255,.06);
  border-bottom:1px solid rgba(255,255,255,.06);
  vertical-align:middle;background:rgba(255,255,255,.02);transition:background .2s
}
.zt-wrap tbody tr:hover td{background:rgba(255,255,255,.05)}
.zt-wrap tbody tr td:first-child{border-left:3px solid var(--zc);border-radius:12px 0 0 12px}
.zt-wrap tbody tr td:last-child{border-radius:0 12px 12px 0}
.zt-num{font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;line-height:1;
        color:transparent;-webkit-text-stroke:1.5px var(--zc)}
.zt-name{font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:var(--zc);margin:.1rem 0 .12rem}
.zt-sub{color:#a79fc0;font-size:.75rem;font-style:italic}
.zt-desc{color:#d6d0f0;line-height:1.5;font-size:.85rem;margin-bottom:.4rem}
.zt-bullets{list-style:none;padding:0;margin:0}
.zt-bullets li{color:#b9b1d3;font-size:.8rem;padding:.07rem 0}
.zt-bullets li::before{content:"● ";color:var(--zc);font-size:.58rem;vertical-align:middle}
.zt-stat{text-align:center}
.zt-stat b{display:block;font-family:'Syne';font-size:1.4rem;color:var(--zc)}
.zt-stat span{color:#a79fc0;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase}
.zt-badge{display:inline-block;padding:.13rem .5rem;border-radius:999px;
          border:1px solid var(--zc);color:var(--zc);font-size:.7rem;margin:.1rem .1rem 0 0}
.zt-thumb{border-radius:10px;overflow:hidden;background:#07060d;
          border:1px solid rgba(255,255,255,.1);line-height:0}
.zt-thumb canvas{width:100%!important;height:auto!important}
.no-song{text-align:center;padding:3rem 2rem;color:#a79fc0;
         border:1px dashed rgba(255,255,255,.15);border-radius:16px;margin-top:2rem}
.no-song b{display:block;font-family:'Syne';font-size:1.6rem;color:#ff2d55;margin-bottom:.5rem}
</style>
""", unsafe_allow_html=True)

# ── header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="eyebrow reveal">From Music to Architecture</div>'
    '<h1 class="reveal disp" style="font-size:clamp(2rem,5vw,3.4rem);margin-bottom:.3rem">'
    'Five-Zone <strong>Spatial Journey</strong></h1>'
    '<p class="lead reveal" style="margin-bottom:2rem">'
    'Each section of your song becomes a distinct architectural zone — '
    'rendered directly from the same geometry as the 3D model.</p>',
    unsafe_allow_html=True,
)

# ── session state check ───────────────────────────────────────────────────────
arch      = st.session_state.get("arch")
song_name = st.session_state.get("song_name", "Your song")

if not arch or not arch.get("segments"):
    st.markdown(
        '<div class="no-song">'
        '<b>No song analysed yet</b>'
        'Go to <b>Studio</b>, upload a track (or tick demo data), '
        'then come back here — your song\'s actual 3D zone renders will appear.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("views/studio.py", label="Open the Studio")
    st.stop()

segs = arch["segments"]
fmt  = lambda x: f"{int(x//60)}:{int(x%60):02d}"

def zone_segs(zname): return [s for s in segs if s["zone"] == zname]
def avg(z, k): return sum(s[k] for s in z) / len(z) if z else 0

def zone_stats(zname):
    z = zone_segs(zname)
    if not z: return None
    mats = {}
    for s in z: mats[s["material"]] = mats.get(s["material"], 0) + 1
    return {
        "rooms":      len(z),
        "avg_height": avg(z, "height"),
        "avg_open":   avg(z, "openness"),
        "total_ribs": sum(s["ribs"] for s in z),
        "start_t":    min(s["start_time"] for s in z),
        "end_t":      max(s["start_time"] + s["duration"] for s in z),
        "material":   max(mats, key=mats.get),
        "pattern":    z[0].get("pattern", "woven lattice"),
        "segs":       z,
    }

# ── strip large fields before passing to HTML to keep size down ───────────────
def slim_arch(arch):
    keep = {"tempo","compression","width","zones"}
    slim = {k: arch[k] for k in keep if k in arch}
    slim["segments"] = [
        {k: s[k] for k in
         ("zone","height","length","width","ribs","openness","density",
          "material","light","x0","z0","x","z","heading","pattern")
         if k in s}
        for s in arch.get("segments", [])
    ]
    return slim

# ── song info row ─────────────────────────────────────────────────────────────
tempo  = arch.get("tempo", "—")
n_segs = len(segs)
end_t  = segs[-1]["start_time"] + segs[-1]["duration"]

st.markdown(
    f'<p class="lead reveal" style="margin-bottom:1.5rem">'
    f'<b style="color:#ff2d55">{song_name}</b> — '
    f'{n_segs} spaces &nbsp;·&nbsp; {tempo} BPM &nbsp;·&nbsp; {fmt(end_t)} walk</p>',
    unsafe_allow_html=True,
)

# ── FULL-WIDTH ZONE STRIP (all 5 zones side by side, actual rendered geometry) ──
st.markdown('<div class="eyebrow reveal">3D model — rendered per zone</div>', unsafe_allow_html=True)

thumb_html = (ROOT / "viewer" / "zone_thumbs.html").read_text(encoding="utf-8")
thumb_html = thumb_html.replace("__DATA__", json.dumps(slim_arch(arch)))
components.html(thumb_html, height=190, scrolling=False)

st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

# ── MAIN TABLE ────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow reveal" style="margin-top:1.5rem">Zone breakdown</div>', unsafe_allow_html=True)

rows_html = ""
for zname in ZONE_ORDER:
    num, name, subtitle, desc, bullets, color = ZONE_META[zname]
    stats = zone_stats(zname)
    if stats is None:
        continue
    bullet_html = "".join(f"<li>{b}</li>" for b in bullets)
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
<div class="reveal" style="overflow-x:auto;margin-top:.8rem">
<table class="zt-wrap">
  <thead>
    <tr>
      <th>Zone</th>
      <th>Spatial Character</th>
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

# ── pipeline callout ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="card reveal" style="margin-top:2rem;text-align:center">'
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
