"""Zones page — Five-Zone Spatial Journey with Three.js renders inside the table."""
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

from ui import graphics as g

ROOT = Path(__file__).resolve().parent.parent

st.markdown(
    '<div class="eyebrow reveal">From Music to Architecture</div>'
    '<h1 class="reveal disp" style="font-size:clamp(2rem,5vw,3.4rem);margin-bottom:.3rem">'
    'Five-Zone <strong>Spatial Journey</strong></h1>'
    '<p class="lead reveal" style="margin-bottom:2rem">'
    'Each section of your song becomes a distinct architectural zone — '
    'rendered with the same Three.js geometry as the 3D model.</p>',
    unsafe_allow_html=True,
)

arch      = st.session_state.get("arch")
song_name = st.session_state.get("song_name", "Your song")

if not arch or not arch.get("segments"):
    st.markdown(
        '<div style="text-align:center;padding:3rem 2rem;color:#a79fc0;'
        'border:1px dashed rgba(255,255,255,.15);border-radius:16px;margin-top:2rem">'
        '<b style="display:block;font-family:Syne;font-size:1.6rem;color:#ff2d55;margin-bottom:.5rem">'
        'No song analysed yet</b>'
        'Go to <b>Studio</b>, upload a track (or tick demo data), '
        'then come back — your song\'s actual 3D zone renders will appear here.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("views/studio.py", label="Open the Studio")
    st.stop()

segs  = arch["segments"]
tempo = arch.get("tempo", "—")
end_t = segs[-1]["start_time"] + segs[-1]["duration"]
fmt   = lambda x: f"{int(x//60)}:{int(x%60):02d}"

st.markdown(
    f'<p class="lead reveal" style="margin-bottom:1rem">'
    f'<b style="color:#ff2d55">{song_name}</b> — '
    f'{len(segs)} spaces &nbsp;·&nbsp; {tempo} BPM &nbsp;·&nbsp; {fmt(end_t)} walk</p>',
    unsafe_allow_html=True,
)

def slim(a):
    out = {k: a[k] for k in ("tempo","compression","width","zones") if k in a}
    out["segments"] = [
        {k: s[k] for k in
         ("zone","height","length","width","ribs","openness","density",
          "material","light","tilt","arch_p","twist","weave","pattern",
          "x0","z0","x","z","heading","start_time","duration","zt")
         if k in s}
        for s in a.get("segments", [])
    ]
    return out

html = (ROOT / "viewer" / "zone_thumbs.html").read_text(encoding="utf-8")
html = html.replace("__DATA__", json.dumps(slim(arch)))
components.html(html, height=760, scrolling=True)

st.markdown(g.band("INTRO RHYTHM HARMONY CLIMAX OUTRO "), unsafe_allow_html=True)

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
