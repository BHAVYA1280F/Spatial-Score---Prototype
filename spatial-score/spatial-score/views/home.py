import streamlit as st
import streamlit.components.v1 as components

from ui import graphics as g

components.html(g.hero_html(), height=640)
st.markdown(g.band("PITCH HEIGHT DURATION LENGTH RHYTHM SPACING TEMPO MELODY ") +
            g.band("HARMONY TEXTURE TIMBRE FORM DYNAMICS OPENNESS ", rev=True), unsafe_allow_html=True)

st.markdown('<div class="eyebrow reveal">The idea</div><h2 class="reveal disp" style="font-size:clamp(2rem,5vw,3.6rem)">'
            'Three moves from sound to space</h2>', unsafe_allow_html=True)
steps = [("01", "Listen", "The song is cut at its beats. Pitch, loudness, brightness and note density are measured for each slice.", [20, 55, 35, 80, 45, 90], "#ff2d55"),
         ("02", "Translate", "Every measurement is mapped to an architectural rule: height, length, openness, material, spacing.", [60, 60, 60, 60, 60], "#9b6bff"),
         ("03", "Walk", "Rooms join into a pavilion. Walk through it while the song plays, in time with the music.", [90, 70, 50, 35, 20], "#4f8cff")]
st.markdown('<div class="grid3">' + "".join(g.card(c, n, t, d, g.bars(h, c)) for n, t, d, h, c in steps) + "</div>", unsafe_allow_html=True)

st.markdown('<div class="eyebrow reveal">The journey</div><h2 class="reveal disp" style="font-size:clamp(2rem,5vw,3.6rem)">'
            'Five zones follow the song</h2>', unsafe_allow_html=True)
st.markdown('<div class="grid5">' + "".join(g.card(c, str(i + 1), n, d, g.bars(h, c)) for i, (n, c, h, d) in enumerate(g.ZONES)) + "</div>",
            unsafe_allow_html=True)

st.markdown(g.band("LISTEN TRANSLATE WALK ") , unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.page_link("views/studio.py", label="Open the Studio")
c2.page_link("views/gallery.py", label="Browse the Gallery")
c3.page_link("views/method.py", label="See the method")
st.markdown('<p class="lead reveal" style="margin-top:3rem">An interdisciplinary project between Architecture and Computer Science at Amity University. '
            'Concept and mapping framework by Agna. Technical development by Bhavya Kalra.</p>', unsafe_allow_html=True)
