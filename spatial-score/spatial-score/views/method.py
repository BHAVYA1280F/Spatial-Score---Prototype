import streamlit as st

from ui import graphics as g

st.markdown(g.head("Method", "How music becomes space",
                   "Ten musical elements, ten architectural translations. Hover a card to hear it move."), unsafe_allow_html=True)
st.markdown('<div class="grid4" style="margin-top:2rem">' + "".join(
    g.card(c, "", f"{m} <span style='color:#a79fc0;font-weight:400'>/ {a}</span>", d, g.icon(i, c)) for m, a, i, c, d in g.METHOD) + "</div>",
    unsafe_allow_html=True)

st.markdown(g.band("SEGMENT MEASURE MAP BUILD WALK "), unsafe_allow_html=True)
st.markdown('<div class="eyebrow reveal">Pipeline</div><h2 class="reveal disp" style="font-size:clamp(2rem,5vw,3.2rem)">What happens to your song</h2>',
            unsafe_allow_html=True)
pipe = [("Segment", "The track is cut at its beats into 1 to 4 second slices (at most 120)."),
        ("Measure", "Each slice gets pitch, loudness, brightness, note density and duration."),
        ("Map", "Measurements are rescaled to 0 to 1 and turned into room dimensions and zones."),
        ("Build", "Three.js draws every room: floor, walls, ribs, layers, spires and light."),
        ("Walk", "The camera follows the song's clock through the pavilion, with optional music.")]
st.markdown('<div class="grid5">' + "".join(g.card("#ff2d55", str(i + 1), t, d) for i, (t, d) in enumerate(pipe)) + "</div>", unsafe_allow_html=True)

st.markdown('<div class="eyebrow reveal">Built with</div><div class="chips reveal">' + "".join(
    f"<span>{t}</span>" for t in ["Streamlit", "librosa", "NumPy", "SciPy", "pandas", "Three.js", "Python", "HTML canvas"]) + "</div>",
    unsafe_allow_html=True)
st.markdown('<div class="card reveal" style="margin-top:2rem;--c:#ffb454"><h3>Honest limits</h3><p>Pitch is clearest on a single melody. Harmony here means sustained passages, '
            'not detected chords. The output is an interpretation of the music, not a structural design.</p></div>', unsafe_allow_html=True)
