# 🎼🏛️ SPATIAL SCORE
### Translating Musical Structure into Architectural Experience

Upload a piece of music. Spatial Score analyses it and turns it into a 3D architectural form you can explore in your browser.

> An interdisciplinary collaboration between **Architecture** and **Computer Science** at Amity University.

---

## 📖 Table of Contents
1. [About the Project](#-about-the-project)
2. [Core Concept: Music → Architecture Mapping](#-core-concept-music--architecture-mapping)
3. [Features](#-features)
4. [Tech Stack](#-tech-stack)
5. [System Architecture](#-system-architecture)
6. [Audio Analysis Details](#-audio-analysis-details)
7. [3D Generation Details](#-3d-generation-details)
8. [Project Structure](#-project-structure)
9. [Installation & Setup](#-installation--setup)
10. [Usage](#-usage)
11. [Deployment (Free)](#-deployment-free)
12. [Limitations](#-limitations)
13. [Roadmap](#-roadmap)
14. [Team](#-team)
15. [Acknowledgements & License](#-acknowledgements--license)

---

## 🌟 About the Project

Music and architecture have long been compared ("architecture is frozen music"). Both organise **rhythm, proportion, repetition, tension and release** across time (music) or space (architecture).

**Spatial Score** makes this comparison literal. It extracts measurable musical features from an audio file and maps them to architectural parameters such as height, length, spacing, density, materiality and openness. The result is a generated 3D form the user can orbit and walk through.

**Goals**
- Explore how musical structure can inform spatial design.
- Provide an interactive tool where anyone can "see" their music as architecture.
- Bridge computational analysis and architectural thinking.

---

## 🎯 Core Concept: Music → Architecture Mapping

The mapping framework is designed by the architecture side of the team. The software implements these rules.

| Musical Element | Architectural Translation | What It Does |
|---|---|---|
| **Pitch** | Height | Controls the vertical height of spaces |
| **Duration** | Spatial Length | Controls the length/depth of spatial segments |
| **Rhythm** | Repetition & Spacing | Controls the repetition and intervals of architectural elements |
| **Tempo** | Spatial Compression / Expansion | Tight, compressed spaces for fast music; expansive for slow |
| **Melody** | Spatial Sequence / Path | Determines the main spatial journey |
| **Harmony** | Spatial Relationships / Overlap | Defines interaction between simultaneous spatial layers |
| **Texture** | Spatial Density | Controls density of architectural elements and layers |
| **Timbre** | Materiality | Influences material and surface character |
| **Form** | Overall Spatial Organisation | Determines arrangement of major spatial zones |
| **Dynamics / Intensity** | Openness / Enclosure | Influences how open or enclosed a space feels |

---

## ✨ Features

- 🎵 Upload audio (MP3 / WAV)
- 🔍 Automatic extraction of pitch, tempo, beats, onsets, energy, timbre and more
- 🧮 Rule-based mapping from audio features to architectural parameters
- 🏗️ Procedurally generated 3D form
- 🖱️ Interactive viewer (orbit, zoom, pan; walkthrough camera planned)
- 🎛️ Adjustable mapping settings (sliders for scale, height range, density)
- 📦 Export parameters as JSON (3D export to OBJ/GLB planned)
- 💸 Fully free to build and host

---

## 🛠️ Tech Stack

### Frontend / App Framework
| Technology | Purpose |
|---|---|
| **Streamlit** | Web app UI, file upload, controls, and hosting-ready framework |
| **Three.js** (embedded via `st.components.v1.html`) | Interactive 3D rendering and walkthrough camera |
| **Plotly** (`Mesh3d`) | Optional quick 3D preview in pure Python |
| **HTML / CSS / JavaScript** | Custom 3D viewer component |

### Backend / Processing (Python)
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **librosa** | Audio analysis: pitch (`pyin`), tempo, beats, onsets, spectral features, chroma |
| **NumPy** | Numerical processing |
| **SciPy** | Signal processing and smoothing |
| **pandas** | Structuring per-segment feature data |
| **soundfile / audioread** | Audio decoding |
| **msaf** *(optional, later)* | Structural segmentation (verse / chorus / bridge) |
| **trimesh** *(optional, later)* | Export geometry to OBJ / GLB |

### Tools & Infrastructure
| Technology | Purpose |
|---|---|
| **Git & GitHub** | Version control and deployment source |
| **Streamlit Community Cloud** | Free hosting |
| **Blender / Rhino** *(optional)* | Post-processing exported models for portfolio use |
| **VS Code** | Development |

---

## 🧩 System Architecture

```
┌──────────────┐     ┌────────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  User uploads │ →  │  Audio Analysis     │ →  │  Mapping Engine  │ →  │  3D Viewer        │
│  MP3 / WAV    │     │  (librosa, NumPy)   │     │  (rules → JSON)  │     │  (Three.js)       │
└──────────────┘     └────────────────────┘     └─────────────────┘     └──────────────────┘
        Streamlit handles upload, caching, controls and page layout end to end
```

**Flow**
1. User uploads a track in the Streamlit app.
2. The track is split into time segments (by beats or fixed windows).
3. librosa extracts features for each segment.
4. The mapping engine converts features into architectural parameters (a JSON structure).
5. The JSON is passed to an embedded Three.js scene that builds the geometry.
6. The user explores the result; results are cached with `st.cache_data`.

**Example parameter JSON (per segment)**
```json
{
  "segment": 12,
  "start_time": 24.5,
  "duration": 2.1,
  "height": 8.4,
  "length": 3.2,
  "spacing": 0.7,
  "density": 0.55,
  "openness": 0.3,
  "material": "concrete"
}
```

---

## 🔬 Audio Analysis Details

| Feature | Method | Feeds |
|---|---|---|
| Pitch | `librosa.pyin` (fundamental frequency) | Height |
| Note / segment duration | Onset detection and segment lengths | Spatial length |
| Rhythm | Onset times and inter-onset intervals | Repetition & spacing |
| Tempo | `librosa.beat.beat_track` | Compression / expansion |
| Dynamics | RMS energy | Openness / enclosure |
| Timbre | Spectral centroid, rolloff, MFCCs | Materiality |
| Texture | Onset density, spectral flux, spectral bandwidth | Density |
| Melody | Smoothed pitch contour | Spatial path |
| Harmony | Chroma features and chord estimation | Overlap / layers |
| Form | Structural segmentation (self-similarity) | Spatial zones |

**Accuracy notes:** pitch, tempo, dynamics and rhythm are reliable. Melody, harmony and form are *approximate*, especially on dense full-band songs with vocals. They work best on solo or simple instrumental tracks.

---

## 🏗️ 3D Generation Details

- **Height** from pitch is normalised to a configurable range (for example 2–20 units).
- **Length** from duration is scaled linearly or logarithmically.
- **Spacing** between repeated elements comes from rhythmic intervals.
- **Openness** controls wall opacity, window/void size and enclosure.
- **Materiality** assigns textures: bright timbre → glass/light materials; dark or warm timbre → concrete/wood/stone.
- **Path** (melody) bends the sequence of volumes along a curve.
- The output is an **interpretation**, not a single "correct" translation. Mapping rules are adjustable.

---

## 📁 Project Structure

```
spatial-score/
├── app.py                  # Streamlit entry point
├── requirements.txt        # Python dependencies
├── README.md
├── core/
│   ├── analysis.py         # librosa feature extraction
│   ├── mapping.py          # music → architecture rules
│   └── export.py           # JSON / OBJ / GLB export
├── viewer/
│   └── scene.html          # Three.js scene template
├── assets/
│   └── textures/           # Material textures
├── samples/                # Short royalty-free test audio
└── docs/
    └── mapping_framework.md
```

---

## ⚙️ Installation & Setup

**Prerequisites:** Python 3.10+, Git, and FFmpeg (needed to decode MP3).

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/spatial-score.git
cd spatial-score

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

**`requirements.txt`**
```
streamlit
librosa
numpy
scipy
pandas
soundfile
plotly
trimesh
```

For Streamlit Community Cloud, add a `packages.txt` file containing:
```
ffmpeg
```

---

## ▶️ Usage

1. Open the app (locally at `http://localhost:8501`).
2. Upload an MP3 or WAV file (recommended: under 5 minutes).
3. Wait for the analysis (cached afterwards).
4. Adjust mapping sliders if desired.
5. Explore the generated 3D architecture.
6. Download the parameter JSON (or 3D model, once available).

---

## 🚀 Deployment (Free)

1. Push the project to a **public GitHub repository**.
2. Go to **Streamlit Community Cloud** and sign in with GitHub.
3. Click **New app**, choose the repo, branch and `app.py`.
4. Deploy. You get a public link to share.

**Free tier notes**
- About 1 GB RAM, so limit audio length (3–5 minutes).
- Apps sleep after inactivity and wake in a few seconds.
- Use `st.cache_data` to avoid reprocessing the same song.

---

## ⚠️ Limitations

- Harmony, melody and form detection are approximate on complex music.
- Free hosting has CPU/RAM limits, so very long files may fail.
- The architectural output is an artistic interpretation, not a structural design.
- Generated forms are conceptual and are not engineering-ready.

---

## 🗺️ Roadmap

- [ ] **MVP:** upload → extract pitch, duration, tempo, rhythm → stacked-block / corridor form
- [ ] **v2:** timbre-based materials, dynamics-based openness, melody-driven path
- [ ] **v3:** harmony layers, structural zones, texture density
- [ ] Walkthrough (first-person) camera
- [ ] OBJ / GLB export for Rhino and Blender
- [ ] Preset mapping styles (sculptural, urban, interior)
- [ ] Side-by-side audio playback synced with the 3D walkthrough

---

## 👥 Team

| Name | Role |
|---|---|
| **Agna** | Concept, architectural framework and mapping system (5th-year Architecture, Amity University) |
| **Bhavya Kalra** | Technical development: audio analysis, app and 3D visualisation (B.Tech CSE, Amity University, Noida) |

---

## 🙏 Acknowledgements & License

- Thanks to Vibha ma'am for connecting the collaborators.
- Built with open-source tools: [librosa](https://librosa.org), [Streamlit](https://streamlit.io), [Three.js](https://threejs.org).
- License: MIT (suggested; update as the team decides).

---

*"Architecture is frozen music." (attributed to Goethe, and echoed by many since)*
