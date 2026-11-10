"""Compare view: analyse two songs side-by-side and render both pavilions."""
import base64
import json
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

from core.analysis import analyse, demo_features
from core.mapping import map_features
from ui import graphics as g

ROOT = Path(__file__).resolve().parent.parent
MIME = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg", "flac": "audio/flac"}

st.markdown(
    g.head("Compare", "Two songs, side by side",
           "Upload two tracks and see how differently the same musical rules can shape a pavilion."),
    unsafe_allow_html=True,
)

# sidebar shared mapping controls
with st.sidebar:
    st.header("Shared mapping settings")
    max_seconds = st.slider("Max audio length (s)", 20, 300, 90, 10)
    beats_per_segment = st.slider("Beats per space", 1, 8, 2)
    hr = st.slider("Height range (pitch)", 2.0, 30.0, (3.0, 18.0))
    length_scale = st.slider("Length scale (duration)", 0.5, 2.0, 1.0, 0.1)
    turn = st.slider("Path turning (melody)", 0.0, 2.0, 0.6, 0.1)
    use_zones = st.checkbox("Divide into zones", True)


@st.cache_data(show_spinner=False)
def cached_analyse(data, name, max_s, bps):
    return analyse(data, name, max_s, bps)


def audio_uri_for(raw, ext):
    # type: (bytes, str) -> Optional[str]
    if len(raw) <= 15 * 1024 * 1024:
        return "data:{};base64,".format(MIME.get(ext, "audio/mpeg")) + base64.b64encode(raw).decode()
    return None


def build_arch(features):
    arch = map_features(features, hr, length_scale, turn, zones=use_zones)
    arch["song_seconds"] = features.get("total_seconds")
    arch["viz"] = features.get("viz")
    return arch


def render_slot(col, label, slot_key):
    """Render one upload + pavilion column. Returns (arch, audio_uri) or (None, None)."""
    with col:
        st.markdown("### {}".format(label))
        source = st.radio("Source", ["Upload", "Demo data"], horizontal=True,
                          key="src_{}".format(slot_key))
        file = None
        if source == "Upload":
            file = st.file_uploader(
                "Drop a song (MP3, WAV, OGG, FLAC)",
                type=["mp3", "wav", "ogg", "flac"],
                key="file_{}".format(slot_key),
            )

        use_demo = (source == "Demo data")
        features = None
        uri = None

        if file is not None and not use_demo:
            raw = file.getvalue()
            fname = file.name if "." in (file.name or "") else "recording.wav"
            with st.spinner("Analysing…"):
                try:
                    features = cached_analyse(raw, fname, max_seconds, beats_per_segment)
                except Exception as e:  # noqa: BLE001
                    st.error("Could not analyse this file: {}".format(e))
            ext = fname.rsplit(".", 1)[-1].lower()
            uri = audio_uri_for(raw, ext)
        elif use_demo:
            features = demo_features()
        else:
            st.info("Upload a track or choose Demo data.")
            return None, None

        if features is None:
            return None, None

        arch = build_arch(features)
        segs = arch.get("segments", [])
        if not segs:
            st.warning("No segments found — try a different file.")
            return None, None

        end_t = segs[-1]["start_time"] + segs[-1]["duration"]
        def fmt(x):
            return "{}:{:02d}".format(int(x // 60), int(x % 60))
        st.markdown(
            g.stats([
                ("Tempo", "{} BPM".format(arch["tempo"])),
                ("Spaces", len(segs)),
                ("Walk", fmt(end_t)),
            ]),
            unsafe_allow_html=True,
        )
        return arch, uri


# two-column layout
col_a, divider, col_b = st.columns([10, 1, 10])

with divider:
    st.markdown(
        "<div style='border-left:2px solid rgba(255,255,255,.12);"
        "height:600px;margin:60px auto 0;width:0'></div>",
        unsafe_allow_html=True,
    )

arch_a, uri_a = render_slot(col_a, "Song A", "a")
arch_b, uri_b = render_slot(col_b, "Song B", "b")

# show pavilions
scene_tpl = (ROOT / "viewer" / "scene.html").read_text(encoding="utf-8")

if arch_a is not None:
    st.markdown("---")
    st.markdown('<div class="eyebrow reveal">Pavilion A</div>', unsafe_allow_html=True)
    html_a = scene_tpl.replace("__DATA__", json.dumps(arch_a)).replace("__AUDIO__", json.dumps(uri_a))
    components.html(html_a, height=640)

if arch_b is not None:
    st.markdown("---")
    st.markdown('<div class="eyebrow reveal">Pavilion B</div>', unsafe_allow_html=True)
    html_b = scene_tpl.replace("__DATA__", json.dumps(arch_b)).replace("__AUDIO__", json.dumps(uri_b))
    components.html(html_b, height=640)

# difference summary
if arch_a is not None and arch_b is not None:
    st.markdown("---")
    st.markdown('<div class="eyebrow reveal">How they differ</div>', unsafe_allow_html=True)

    segs_a = arch_a["segments"]
    segs_b = arch_b["segments"]

    def avg(segs, k):
        return sum(s[k] for s in segs) / max(1, len(segs))

    zone_order = ["intro", "rhythm", "harmony", "climax", "outro"]

    def zone_str(arch):
        parts = []
        for z in zone_order:
            count = arch["zones"].get(z, 0)
            if count:
                color = g.ZONE_COLORS.get(z, "#fff")
                parts.append('<span style="color:{}">{} {}</span>'.format(color, z, count))
        return " &middot; ".join(parts)

    rows = [
        ("Tempo",
         "{} BPM".format(arch_a["tempo"]),
         "{} BPM".format(arch_b["tempo"])),
        ("Spaces (rooms)", len(segs_a), len(segs_b)),
        ("Avg height",
         "{:.1f} m".format(avg(segs_a, "height")),
         "{:.1f} m".format(avg(segs_b, "height"))),
        ("Avg openness",
         "{:.0f}%".format(avg(segs_a, "openness") * 100),
         "{:.0f}%".format(avg(segs_b, "openness") * 100)),
        ("Total arches",
         sum(s["ribs"] for s in segs_a),
         sum(s["ribs"] for s in segs_b)),
        ("Dominant material",
         max(["concrete", "wood", "glass"],
             key=lambda m: sum(1 for s in segs_a if s["material"] == m)),
         max(["concrete", "wood", "glass"],
             key=lambda m: sum(1 for s in segs_b if s["material"] == m))),
        ("Zone breakdown", zone_str(arch_a), zone_str(arch_b)),
    ]

    table_rows = "".join(
        "<tr>"
        "<td style='color:#a79fc0;padding:6px 12px'>{}</td>"
        "<td style='color:#fff;padding:6px 12px'>{}</td>"
        "<td style='color:#fff;padding:6px 12px'>{}</td>"
        "</tr>".format(lab, a, b)
        for lab, a, b in rows
    )
    st.markdown(
        "<table style='border-collapse:collapse;width:100%;font-size:.9rem'>"
        "<tr style='border-bottom:1px solid rgba(255,255,255,.12)'>"
        "<th style='text-align:left;padding:6px 12px;color:#cfd6e6'>Metric</th>"
        "<th style='text-align:left;padding:6px 12px;color:#ff5c7c'>Song A</th>"
        "<th style='text-align:left;padding:6px 12px;color:#4f8cff'>Song B</th>"
        "</tr>{}</table>".format(table_rows),
        unsafe_allow_html=True,
    )
