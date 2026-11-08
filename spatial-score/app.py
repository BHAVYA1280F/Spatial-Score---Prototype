"""SPATIAL SCORE - Streamlit app: music in, architecture out."""
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
    max_seconds = st.slider("Max audio length (s)", 20, 180, 90, 10)
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

file = st.file_uploader("Upload music (MP3 / WAV)", type=["mp3", "wav", "ogg", "flac"])
use_demo = st.checkbox("Use demo data (no audio needed)", value=file is None)


@st.cache_data(show_spinner="Analysing music...")
def cached_analyse(data: bytes, name: str, max_s: int, bps: int):
    return analyse(data, name, max_s, bps)


features = None
if file is not None and not use_demo:
    try:
        features = cached_analyse(file.getvalue(), file.name, max_seconds, beats_per_segment)
    except Exception as e:  # noqa: BLE001
        st.error(f"Could not analyse this file: {e}")
elif use_demo:
    features = demo_features()

if features:
    arch = map_features(features, hr, length_scale, turn, zones=use_zones,
                        intro_frac=intro_pct / 100, outro_frac=outro_pct / 100,
                        climax_frac=climax_pct / 100)
    html = (Path(__file__).parent / "viewer" / "scene.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(arch))
    components.html(html, height=640)

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