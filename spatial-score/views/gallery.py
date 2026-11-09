import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from core.analysis import analyse
from core.mapping import map_features
from ui import graphics as g

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "assets" / "samples"
SP = [0.03, 0.09, 0.05, 0.11]
MIME = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg", ".flac": "audio/flac"}

# Original tracks synthesised for this project (see tools/make_samples.py).
META = {
    "hazy-rooms": ("Hazy Rooms", "68 BPM | slow and dark", "Soft pads, a late-night pulse and a few lonely notes.", ("#1a0a1f", "#c4122f", "#f3d9c4")),
    "neon-drive": ("Neon Drive", "122 BPM | bright and driving", "Four-on-the-floor with a glowing arpeggio.", ("#0f2a5a", "#7aa2ff", "#ff7ab6")),
    "glass-piano": ("Glass Piano", "80 BPM | sparse and clear", "Bell-like notes in wide open space.", ("#101c28", "#4f8cff", "#d9f1ff")),
    "pulse-city": ("Pulse City", "140 BPM | hard and fast", "Square-wave lead over a relentless kick.", ("#101018", "#9b6bff", "#ff2d55")),
}


@st.cache_data(show_spinner="Listening to the track...")
def analyse_sample(path: str):
    p = Path(path)
    return analyse(p.read_bytes(), p.name, 90, 2)


st.markdown(g.head("Gallery", "Sample tracks, in motion",
                   "Pick a sample track to see the pavilion it builds. Hover a sleeve and the record slides out."), unsafe_allow_html=True)

# ---------------- sample tracks ----------------
tracks = sorted(p for p in SAMPLE_DIR.glob("*") if p.suffix.lower() in MIME)
st.markdown('<div class="eyebrow reveal">Sample tracks</div><h2 class="reveal disp" style="font-size:clamp(1.8rem,4vw,3rem)">'
            'See the architecture of a song</h2>', unsafe_allow_html=True)
for r in range(0, len(tracks), 4):
    cols = st.columns(4)
    for col, p in zip(cols, tracks[r:r + 4]):
        i = tracks.index(p)
        title, tag, text, pal = META.get(p.stem, (p.stem.replace("-", " ").replace("_", " ").title(), "Your track",
                                                   "Added by you in assets/samples.", g.COVERS[i % len(g.COVERS)][1]))
        with col:
            st.markdown(g.cover_card(g.cover_svg(i, pal), title, pal, SP[i % 4]) +
                        f'<p style="margin:2rem 0 .2rem;font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;color:#ff5c7c">{tag}</p>'
                        f'<p style="color:#b9b1d3;font-size:.9rem;margin:0 0 .6rem">{text}</p>', unsafe_allow_html=True)
            if st.button("See its architecture", key=f"play_{p.stem}"):
                st.session_state["sample"] = str(p)

sel = st.session_state.get("sample")
if sel and Path(sel).exists():
    p = Path(sel)
    title = META.get(p.stem, (p.stem.replace("-", " ").replace("_", " ").title(),))[0]
    st.markdown(f'<div class="eyebrow reveal">Now exploring</div><h2 class="reveal disp" style="font-size:clamp(1.8rem,4vw,3rem);margin:0">{title}</h2>',
                unsafe_allow_html=True)
    try:
        features = analyse_sample(sel)
    except Exception as e:  # noqa: BLE001
        features = None
        st.error(f"Could not analyse this track: {e}")
    if features:
        arch = map_features(features)
        arch["song_seconds"] = features.get("total_seconds")
        arch["viz"] = features.get("viz")
        segs = arch["segments"]
        if segs:
            end_t = segs[-1]["start_time"] + segs[-1]["duration"]
            fmt = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
            st.markdown(g.stats([("Tempo", f"{arch['tempo']} BPM"), ("Spaces", len(segs)), ("Walk length", fmt(end_t))]), unsafe_allow_html=True)
            st.markdown('<div class="eyebrow reveal">Architectural parameters</div>' + g.summary_html(arch), unsafe_allow_html=True)
        raw = p.read_bytes()
        audio_uri = (f"data:{MIME[p.suffix.lower()]};base64," + base64.b64encode(raw).decode()) if len(raw) <= 15 * 1024 * 1024 else None
        html = (ROOT / "viewer" / "scene.html").read_text(encoding="utf-8")
        html = html.replace("__DATA__", json.dumps(arch)).replace("__AUDIO__", json.dumps(audio_uri))
        components.html(html, height=640 + (920 if arch.get("viz") else 0))
        st.caption("Click a room (or any chart) to see which musical information shaped it. Press Walk with music to hear the track while you move through its pavilion. Full experience and Speed work here too.")
        if st.button("Close"):
            st.session_state.pop("sample", None)
            st.rerun()
