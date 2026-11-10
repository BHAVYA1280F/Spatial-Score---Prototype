import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.analysis import analyse, demo_features
from core.mapping import map_features
from ui import graphics as g

ROOT = Path(__file__).resolve().parent.parent
MIME = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg", "flac": "audio/flac"}

st.markdown(g.head("Studio", "Make a pavilion",
                   "Bring a song, shape the rules, then walk the space it creates."), unsafe_allow_html=True)

with st.sidebar:
    st.header("Analysis")
    max_seconds = st.slider("Max audio length (s)", 20, 300, 90, 10)
    if st.checkbox("Analyse the whole song (slower)", False):
        max_seconds = 600
        st.caption("Whole songs can take 1-3 minutes. Free hosting may run out of memory on long tracks.")
    beats_per_segment = st.slider("Beats per space", 1, 8, 2)
    st.header("Mapping")
    hr = st.slider("Height range (pitch)", 2.0, 30.0, (3.0, 18.0))
    length_scale = st.slider("Length scale (duration)", 0.5, 2.0, 1.0, 0.1)
    turn = st.slider("Path turning (melody)", 0.0, 2.0, 0.6, 0.1)
    st.header("Zones (song progression)")
    use_zones = st.checkbox("Divide pavilion into zones", True)
    intro_pct = st.slider("Intro length (%)", 5, 30, 15)
    outro_pct = st.slider("Outro length (%)", 5, 30, 15)
    climax_pct = st.slider("Climax length (%)", 5, 30, 15)

source = st.radio("Music source", ["Upload a file", "Record with microphone"], horizontal=True)
if source == "Upload a file":
    file = st.file_uploader("Drop a song here (MP3, WAV, OGG, FLAC)", type=["mp3", "wav", "ogg", "flac"])
else:
    st.caption("Play music near the mic, or sing or play an instrument. 20 to 60 seconds works best.")
    if hasattr(st, "audio_input"):
        file = st.audio_input("Record a clip")
        if file is not None:
            kb = len(file.getvalue()) / 1024
            st.caption(f"Captured {kb:.0f} KB of audio.")
            if kb < 20:
                st.warning("That recording is almost empty. Check microphone permission and the input device, then record again.")
    else:
        file = None
        st.error(f"This Streamlit version ({st.__version__}) has no microphone recorder. Upgrade to 1.40 or newer, "
                 "or record on your phone and use 'Upload a file'.")
fname = file.name if file is not None and "." in (file.name or "") else "recording.wav"
use_demo = st.checkbox("Use demo data (no audio needed)", value=file is None)


@st.cache_data(show_spinner="Listening to the music...")
def cached_analyse(data: bytes, name: str, max_s: int, bps: int):
    return analyse(data, name, max_s, bps)


audio_uri = None
if file is not None and not use_demo:
    raw = file.getvalue()
    if len(raw) <= 15 * 1024 * 1024:
        ext = fname.rsplit(".", 1)[-1].lower()
        audio_uri = f"data:{MIME.get(ext, 'audio/mpeg')};base64," + base64.b64encode(raw).decode()
    else:
        st.warning("File is over 15 MB, so the walkthrough will run without music (analysis still works).")

features = None
if file is not None and not use_demo:
    try:
        features = cached_analyse(file.getvalue(), fname, max_seconds, beats_per_segment)
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not analyse this file: {e}")
elif use_demo:
    features = demo_features()

if features:
    arch = map_features(features, hr, length_scale, turn, zones=use_zones,
                        intro_frac=intro_pct / 100, outro_frac=outro_pct / 100, climax_frac=climax_pct / 100)
    arch["song_seconds"] = features.get("total_seconds")
    arch["viz"] = features.get("viz")
    # persist so the Zones page can read the current song's data
    st.session_state["arch"] = arch
    st.session_state["song_name"] = fname if not use_demo else "Demo track"
    segs = arch["segments"]
    if segs:
        end_t = segs[-1]["start_time"] + segs[-1]["duration"]
        total = features.get("total_seconds")
        fmt = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
        if total and total - end_t > 2:
            st.warning(f"Only the first {fmt(end_t)} of this {fmt(total)} track was analysed, so the walk lasts {fmt(end_t)}. "
                       "Raise 'Max audio length' or tick 'Analyse the whole song' to cover the full track.")
        st.markdown(g.stats([("Tempo", f"{arch['tempo']} BPM"), ("Spaces", len(segs)), ("Walk length", fmt(end_t))]), unsafe_allow_html=True)
        st.markdown('<div class="eyebrow reveal">Architectural parameters</div>' + g.summary_html(arch), unsafe_allow_html=True)
    html = (ROOT / "viewer" / "scene.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(arch)).replace("__AUDIO__", json.dumps(audio_uri))
    st.markdown('<div class="eyebrow reveal">The pavilion</div>', unsafe_allow_html=True)
    components.html(html, height=640 + 1080 + (920 if arch.get("viz") else 0))
    st.caption("Walkthrough is silent. Walk with music plays the song. Both follow the song's timeline, and Full experience works in both.")
    st.download_button("Download parameters (JSON)", json.dumps(arch, indent=2), "spatial_score.json", "application/json")
    with st.expander("Segment data"):
        st.dataframe(pd.DataFrame(segs), use_container_width=True)
else:
    st.info("Upload a track or tick the demo option to begin.")
