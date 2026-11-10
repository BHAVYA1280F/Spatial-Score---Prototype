"""SPATIAL SCORE - multi-page Streamlit app (entry point)."""
import streamlit as st

st.set_page_config(page_title="Spatial Score", layout="wide")

from ui.theme import setup  # noqa: E402

pages = [
    st.Page("views/home.py",   title="Home",    default=True),
    st.Page("views/studio.py", title="Studio"),
    st.Page("views/gallery.py",title="Gallery"),
    st.Page("views/zones.py",  title="Zones"),
    st.Page("views/method.py", title="Method"),
]
try:
    nav = st.navigation(pages, position="top")
except TypeError:
    nav = st.navigation(pages)
setup()
nav.run()
