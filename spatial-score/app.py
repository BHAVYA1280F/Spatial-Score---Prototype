"""SPATIAL SCORE - Streamlit app: music in, architecture out."""
import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.analysis import analyse, demo_features
from core.mapping import map_features

st.set_page_config(page_title="Spatial Score", page_icon="🏛️", layout="wide")
st.title("🏛️ SPATIAL SCORE")
st.caption("Translating musical structure into architectural experience")

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
    file = st.file_uploader("Upload music (MP3 / WAV)", type=["mp3", "wav", "ogg", "flac"])
else:
    st.caption("Play music near the mic, or sing / play an instrument. 20-60 seconds works best. "
               "Press the mic button to start, press again to stop.")
    file = st.audio_input("Record a clip")
fname = file.name if file is not None and "." in (file.name or "") else "recording.wav"
use_demo = st.checkbox("Use demo data (no audio needed)", value=file is None)


@st.cache_data(show_spinner="Analysing music...")
def cached_analyse(data: bytes, name: str, max_s: int, bps: int):
    return analyse(data, name, max_s, bps)


MIME = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg", "flac": "audio/flac"}
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
                        intro_frac=intro_pct / 100, outro_frac=outro_pct / 100,
                        climax_frac=climax_pct / 100)
    arch["song_seconds"] = features.get("total_seconds")
    if arch["segments"]:
        end_t = arch["segments"][-1]["start_time"] + arch["segments"][-1]["duration"]
        total = features.get("total_seconds")
        if total and total - end_t > 2:
            m = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
            st.warning(f"Only the first {m(end_t)} of this {m(total)} track was analysed, so the walk lasts {m(end_t)}. "
                       "Raise 'Max audio length' or tick 'Analyse the whole song' to cover the full track.")
    html = (Path(__file__).parent / "viewer" / "scene.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(arch)).replace("__AUDIO__", json.dumps(audio_uri))
    components.html(html, height=640)
    st.caption("Walkthrough = silent walk. ♪ Walk with music = the same walk with the song playing. "
               "Both follow the song's timeline, so the walk lasts as long as the analysed part of the song. "
               "'Full experience' works in both.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Tempo", f"{arch['tempo']} BPM")
    c2.metric("Spaces generated", len(arch["segments"]))
    c3.download_button("Download parameters (JSON)", json.dumps(arch, indent=2),
                       "spatial_score.json", "application/json")
    if use_zones:
        st.caption("Zones: " + "  ›  ".join(f"{k.title()} ({v})" for k, v in arch["zones"].items()))
    with st.expander("Segment data"):
        st.dataframe(pd.DataFrame(arch["segments"]), use_container_width=True)
else:
    st.info("Upload a track or tick the demo option to begin.")