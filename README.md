# SPATIAL SCORE
### Translating Musical Structure into Architectural Experience

Upload a song. The app listens to it, measures things like pitch, tempo, loudness and brightness, and **builds a 3D building from those measurements**. You can rotate around the building or "walk" through it.

> Concept and mapping framework: **Agna** (Architecture, Amity). Technical build: **Bhavya Kalra** (CSE, Amity).

---

## 1. The idea in 30 seconds

A song is a sequence of moments. A building (here, a corridor of rooms) is a sequence of spaces. So:

- Chop the song into **segments** (roughly every 2 beats).
- Measure each segment (how high is the pitch, how long is it, how loud, how bright, how busy).
- Turn each segment into **one room** whose size, openness and material come from those measurements.
- Place the rooms one after another to form a path you can walk along.

```
 SONG  ->  chop into segments  ->  measure each  ->  measurements become room sizes  ->  3D building
 (mp3)       (by beats)            (librosa)            (mapping.py)                     (Three.js)
```

---

## 2. Quick start

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

- Open the link it prints (normally http://localhost:8501).
- Tick **"Use demo data"** to see a building immediately, with no audio.
- Or upload a short MP3/WAV (30 to 60 seconds is best).
- The 3D viewer loads Three.js from the internet (cdnjs), so you must be online.

**Windows tip:** if `streamlit.exe` is blocked ("Device Guard policy"), always start it with `python -m streamlit run app.py` (or `py -m streamlit run app.py`).
**Python version tip:** librosa depends on `numba`, which can lag behind the newest Python. If install fails on Python 3.14, use Python 3.11 or 3.12.

---

## 3. What is in the project

```
spatial-score/
├── app.py               The website (Streamlit). Glues everything together.
├── core/
│   ├── analysis.py      Listens to the audio and measures it (librosa).
│   └── mapping.py       Converts measurements into room dimensions.
├── viewer/
│   └── scene.html       The 3D scene (Three.js) that draws the rooms.
├── tests/
│   └── test_mapping.py  Checks the mapping gives sensible numbers.
├── requirements.txt     Python packages to install.
├── packages.txt         System package (ffmpeg) for Streamlit Cloud.
└── README.md            This file.
```

The data flows in one direction:

```
app.py  ->  analysis.py  ->  features  ->  mapping.py  ->  architecture JSON  ->  scene.html
```

---

## 4. How each part works

### 4.1 `app.py` (the website)

Streamlit turns this Python script into a web page. It does the following, in order:

1. Draws the title and the **sidebar sliders** (settings below).
2. Shows the **upload box** and a **demo checkbox**. The demo box is ticked automatically until you upload a file.
3. Gets the *features*:
   - From your file via `analyse(...)` in `analysis.py`, or
   - From `demo_features()` if the demo box is ticked.
   - The analysis is wrapped in `@st.cache_data`, so moving a *mapping* slider does **not** re-analyse the song (it takes seconds) and the page updates instantly.
4. Runs `map_features(...)` from `mapping.py` to get the building description.
5. Reads `viewer/scene.html`, replaces the text `__DATA__` with that description (as JSON), and displays it inside the page with `components.html`.
6. Shows tempo, the number of spaces generated, a **JSON download button** and a table of every segment.

**Sidebar settings**

| Slider | Group | What it changes |
|---|---|---|
| Max audio length (s) | Analysis | Only the first N seconds are analysed (keeps it fast and within free-hosting memory) |
| Beats per space | Analysis | How many beats go into one room. 1 gives many small rooms, 8 gives few long ones |
| Height range (pitch) | Mapping | Lowest and highest wall height |
| Length scale (duration) | Mapping | Makes all rooms longer or shorter |
| Path turning (melody) | Mapping | How strongly the corridor curves. 0 gives a straight line |

### 4.2 `core/analysis.py` (the "ears")

`analyse(audio_bytes, filename, max_seconds, beats_per_segment)` does this:

1. **Load the audio.** Saves the upload to a temporary file (so MP3 decoding works), then loads it as mono at 22,050 samples per second, keeping only the first `max_seconds`. Audio under 1 second raises an error.
2. **Find the beat.** `librosa.beat.beat_track` returns the tempo (BPM) and the position of each beat.
3. **Compute frame-by-frame measurements.** The song is read in tiny frames (hop of 512 samples, about 23 milliseconds):
   - `rms`: loudness (energy) per frame
   - `spectral_centroid`: how "bright" the sound is (high = sharp/treble-heavy, low = dull/bassy)
   - `onset detection`: the moments a new note or hit begins
   - `pyin`: the pitch (fundamental frequency), searched between C2 and C7
4. **Cut into segments.** A boundary is placed on every Nth beat (N = "Beats per space"). If the beat tracker finds fewer than 4 beats (e.g. ambient music), it falls back to fixed 2-second windows. There is a hard cap of 120 segments; if more are found, boundaries are thinned out.
5. **Summarise each segment** into 6 numbers:

| Feature | How it is computed |
|---|---|
| `start`, `duration` | Segment position and length in seconds |
| `pitch_midi` | Median pitch inside the segment, converted to a MIDI note number. If the segment has no detectable pitch (silence, drums), it reuses the previous segment's pitch |
| `rms` | Average loudness |
| `centroid` | Average brightness |
| `onset_density` | Number of note onsets divided by the duration (notes per second) |

The function returns `{"tempo": ..., "segments": [ ... ]}`.

`demo_features()` produces fake sine-wave-shaped data in the same format, so the whole pipeline can be tested without audio.

### 4.3 `core/mapping.py` (the "translator")

This file holds the **rules that turn music into architecture**. These are the rules Agna should tune.

**Step A: normalise.** Raw numbers are not comparable (pitch is about 60, loudness about 0.1, brightness about 2000). So pitch, loudness, brightness and density are each rescaled to **0 to 1** across the song, using the 5th and 95th percentiles so that one extreme moment doesn't squash everything. This means each song uses the full range, so a quiet song and a loud song both give a full variety of rooms.

**Step B: apply the rules, one room per segment.**

| Music | Becomes | Formula (n = normalised 0 to 1 value) |
|---|---|---|
| **Pitch** | **Height** | `height = hmin + (hmax - hmin) × pitch_n` (high notes give tall rooms) |
| **Duration** | **Length** | `length = clip(duration × 1.5 × length_scale × compression, 2, 12)` |
| **Tempo** | **Compression / expansion** | `compression = clip(100 / tempo, 0.6, 1.5)`. Fast songs squeeze all rooms shorter, slow songs stretch them |
| **Rhythm / texture** | **Spacing and ribs** | `spacing = 2.5 − 1.9 × density_n`; `ribs = max(2, int(length / spacing))`. Busy music gives more, tighter vertical fins |
| **Dynamics** | **Openness** | `openness = loudness_n`. Loud gives more open (transparent walls, no roof) |
| **Timbre** | **Material** | brightness_n below 0.34 gives concrete, below 0.67 gives wood, otherwise glass |
| **Melody** | **Path** | `heading += (pitch_n − 0.5) × turn_strength × 0.5`. Higher-than-average pitch turns the corridor one way, lower turns it the other |

**Step C: place the rooms.** Starting at the origin, each room is placed at the end of the previous one, pointing in the current heading direction. For each room the code saves its start point (`x0`, `z0`), its centre (`x`, `z`), its `heading` and all dimensions.

The output is a JSON like:

```json
{
  "tempo": 108.0,
  "width": 4.0,
  "segments": [
    {"segment": 0, "height": 9.4, "length": 3.6, "spacing": 1.7, "ribs": 2,
     "openness": 0.3, "density": 0.4, "material": "wood",
     "heading": -0.02, "x0": 0, "z0": 0, "x": -0.04, "z": 1.8}
  ]
}
```

### 4.3b Pavilion zones (song progression)

On top of the per-room rules, the pavilion is divided into **five connected zones** that follow the song. `assign_zones()` in `core/mapping.py` labels every segment:

| Zone | How it is found | What the pavilion does |
|---|---|---|
| **Intro** | First 15% of the song | More enclosed (openness × 0.3), half the ribs, soft dim warm light |
| **Rhythm** | Middle segments with above-median note density | Extra repeated ribs/columns, spacing follows the rhythm |
| **Harmony** | Middle segments with below-median note density (more sustained) | Two overlapping glass layers per room, at different heights |
| **Climax** | The loudest window (15% of the song) between intro and outro, slightly biased to come later | Height × 1.4, outward-leaning walls, tapered spires instead of ribs, no roof, pulsing coloured light |
| **Outro** | Last 15% of the song | Rooms get lower, more open and dimmer, fading gradually |

Each zone has its own light colour (warm, blue, violet, red, green). The lengths are adjustable in the sidebar ("Zones" section), and the whole thing can be switched off. In walkthrough mode the current zone name is shown at the top.

*Honest note:* "harmony" here is chosen from how sustained or busy the music is, not from real chord detection. Chord-based layering is still a roadmap item. Zones are smoothed so they stay connected, but in a song with no clear build, rhythm and harmony zones may alternate.

### 4.4 `viewer/scene.html` (the "builder")

A single web page using **Three.js** (a JavaScript 3D library). The app injects the JSON in place of `__DATA__`. For each segment it builds one room (a Three.js *group*), placed at `(x, z)` and rotated by `heading`:

| Part | Drawn as |
|---|---|
| Floor | A thin slab, width 4 and the room's length |
| Two walls | Boxes as tall as `height`. Opacity = `1 − 0.8 × openness`, so open rooms have see-through walls |
| Roof | Only added if `openness < 0.6`, and more transparent as openness rises |
| Ribs | `ribs` thin vertical concrete columns along both outer sides |
| Material | Concrete is grey and solid, wood is brown and solid, glass is light blue and at most 45% opaque |

**Controls**
- **Orbit mode:** drag to rotate, scroll to zoom. The camera circles the middle of the building.
- **Walkthrough button:** the camera drops to eye level (1.7 units) and glides along a smooth curve through all the rooms at 4 units per second, looping at the end. Press again to return to orbit.

### 4.5 `tests/test_mapping.py`

Runs the demo data through the mapping and checks that every height, length, openness, material and rib count is within its allowed range, and that empty input doesn't crash.

---

## 5. A worked example

Say a segment of your song has: high pitch, 2 seconds long, loud, bright, and busy, in a 120 BPM song.

- High pitch (pitch_n about 0.9) gives a **tall** room (about 16 of a 3-to-18 range).
- Tempo 120 gives compression 0.83. Length = 2 × 1.5 × 1 × 0.83 gives about **2.5 units** long.
- Loud (loudness_n about 0.9) gives an **open** room with very transparent walls and no roof.
- Bright (brightness_n about 0.9) gives **glass**.
- Busy (density_n about 0.9) gives spacing of about 0.8, so 3 ribs along each side.
- Pitch above 0.5 gives the corridor a gentle turn.

A quiet, low, dull, sparse segment would instead give a short, solid concrete room with thick walls, a roof and wide-spaced ribs. As the song moves between the two, the building changes character, so you can *see* the structure of the music.

---

## 6. Tech stack

| Layer | Tool | Role |
|---|---|---|
| Web app | Streamlit | Page, upload, sliders, caching, hosting |
| Audio analysis | librosa (+ NumPy, SciPy, soundfile) | Beats, pitch, loudness, brightness, onsets |
| Data | pandas | Segment table |
| 3D | Three.js r128 (via cdnjs) | Geometry, lights, camera |
| Hosting | Streamlit Community Cloud | Free, deploy from a public GitHub repo |
| Decoding MP3 | ffmpeg (`packages.txt`) | Needed on Streamlit Cloud |

---

## 7. Deploying for free

1. Put the folder in a **public GitHub repo**.
2. Go to Streamlit Community Cloud, sign in with GitHub, click **New app**, and pick the repo and `app.py`.
3. Deploy and share the link. The app sleeps when idle and wakes in a few seconds.

Free hosting has about 1 GB of RAM, so keep "Max audio length" at 90 seconds or less.

---

## 8. Honest limitations

- **Pitch** tracking works best on a single melody (voice, flute, piano). On a full band mix it picks something approximate.
- **Analysis speed:** pitch tracking (`pyin`) is the slowest step. Expect several seconds to a minute for 90 seconds of audio.
- **The path can curve a lot.** Turning accumulates, so long songs may spiral, and rooms can overlap or leave small gaps at sharp bends. Lower "Path turning" to fix this.
- **Not built yet:** real chord-based harmony, proper verse/chorus detection, texture as a separate layer, OBJ/GLB export, and touch controls.
- The output is an **interpretation**. The rules are a first draft, not the one right answer.

---

## 9. How to change things

| I want to... | Edit |
|---|---|
| Change what pitch does (for example width instead of height) | `core/mapping.py`, the `height = ...` line |
| Change material thresholds | `_material()` in `core/mapping.py` |
| Add a new material or colour | `BASE` in `viewer/scene.html`, and `_material()` |
| Change room shape (arches, slopes, curved walls) | The `segs.forEach` block in `viewer/scene.html` |
| Add a new measurement (for example chords) | Add it in `core/analysis.py`, then use it in `mapping.py` |
| Change walking speed | The `4 * dt` in `viewer/scene.html` |

---

## 10. Roadmap

- [x] MVP: upload, analyse, map, 3D view, walkthrough, JSON export
- [ ] Harmony: stack overlapping layers from detected chords
- [x] Form (first version): intro / rhythm / harmony / climax / outro zones
- [ ] Form (better): detect verse/chorus structure properly
- [ ] OBJ / GLB export for Rhino and Blender
- [ ] Sync audio playback with the walkthrough
- [ ] Preset styles (sculptural, urban, interior)

---

## 11. Credits

Concept and mapping framework: **Agna** (5th-year Architecture, Amity University). Technical development: **Bhavya Kalra** (B.Tech CSE, Amity University, Noida). Thanks to Vibha ma'am for connecting the collaborators. Built with librosa, Streamlit and Three.js. License: MIT (suggested).
