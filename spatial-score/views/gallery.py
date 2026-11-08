import base64
import io
from pathlib import Path

import streamlit as st

from ui import graphics as g

COVER_DIR = Path(__file__).resolve().parent.parent / "assets" / "covers"


@st.cache_data
def load_covers(folder: str):
    from PIL import Image
    items = []
    for p in sorted(Path(folder).glob("*")):
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((600, 600))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82)
        q = im.resize((64, 64)).quantize(colors=4)
        pal = q.getpalette()[:12]
        colors = ["#%02x%02x%02x" % tuple(pal[i:i + 3]) for i in (0, 3, 6, 9)]
        items.append((p.stem.replace("-", " ").replace("_", " ").title(), base64.b64encode(buf.getvalue()).decode(), colors))
    return items


st.markdown(g.head("Gallery", "Album art, in motion",
                   "Hover a sleeve and the record slides out. Scroll and the columns drift at different speeds."), unsafe_allow_html=True)
real = load_covers(str(COVER_DIR))
sp = [0.03, 0.09, 0.05, 0.11]
cards = []
if real:
    for i, (title, b64, pal) in enumerate(real):
        cards.append(g.cover_card(f'<img src="data:image/jpeg;base64,{b64}" alt="{title}">', title, pal, sp[i % 4]))
else:
    for i, (title, pal) in enumerate(g.COVERS):
        cards.append(g.cover_card(g.cover_svg(i, pal), title, pal, sp[i % 4]))
    st.markdown('<div class="card reveal" style="--c:#4f8cff;margin:1rem 0 2rem"><h3>Showing original sample artwork</h3><p>Add your own album covers by putting '
                'image files in <b>assets/covers/</b> (for example after-hours.jpg). They replace these tiles automatically and a colour palette is taken from each one. '
                'Use covers you own or have permission to display.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="grid4" style="margin-top:2rem">' + "".join(cards) + "</div>", unsafe_allow_html=True)
st.markdown(g.band("SOUND SPACE SOUND SPACE ", rev=True), unsafe_allow_html=True)
