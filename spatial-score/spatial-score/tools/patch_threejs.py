"""Inline three.min.js into scene.html to avoid CDN fetch issues on Streamlit Cloud."""
import pathlib

viewer_dir = pathlib.Path(__file__).resolve().parent.parent / "viewer"
three_js = (viewer_dir / "three.min.js").read_text(encoding="utf-8")
scene = (viewer_dir / "scene.html").read_text(encoding="utf-8")

CDN_TAG = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
INLINE_TAG = "<script>" + three_js + "</script>"

if CDN_TAG not in scene:
    print("ERROR: CDN tag not found in scene.html — already patched or file changed.")
else:
    patched = scene.replace(CDN_TAG, INLINE_TAG)
    (viewer_dir / "scene.html").write_text(patched, encoding="utf-8")
    print(f"Patched! scene.html size: {len(patched):,} bytes")
