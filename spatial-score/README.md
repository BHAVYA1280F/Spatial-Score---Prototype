# SPATIAL SCORE
### Translating Musical Structure into Architectural Experience

Give it a song. Spatial Score listens, measures the music, and builds a 3D pavilion from what it hears. You can orbit the building, or walk through it while the song plays, in time with the music.

An interdisciplinary project between Architecture and Computer Science at Amity University.
Concept and mapping framework: **Agna** (5th-year Architecture). Technical development: **Bhavya Kalra** (B.Tech CSE, Amity University, Noida).

---

## Contents
1. [What it does](#1-what-it-does)
2. [Quick start](#2-quick-start)
3. [The app: four pages](#3-the-app-four-pages)
4. [Project structure](#4-project-structure)
5. [How it works, step by step](#5-how-it-works-step-by-step)
6. [The mapping rules](#6-the-mapping-rules)
7. [The five zones](#7-the-five-zones)
8. [The 3D viewer and walkthrough](#8-the-3d-viewer-and-walkthrough)
   - [Musical Feature Analysis and the room inspector](#8b-musical-feature-analysis-and-the-room-inspector)
9. [The frontend design](#9-the-frontend-design)
10. [Music sources](#10-music-sources)
11. [Tech stack](#11-tech-stack)
12. [Deploying for free](#12-deploying-for-free)
13. [Troubleshooting](#13-troubleshooting)
14. [Limitations](#14-limitations)
15. [How to change things](#15-how-to-change-things)
16. [Roadmap](#16-roadmap)

---

## 1. What it does

```
 SONG -> cut at the beats -> measure each slice -> measurements become rooms -> 3D pavilion -> walk through it
 (mp3)     (librosa)           (analysis.py)         (mapping.py)               (Three.js)      (with music)
```

- The song is cut into slices at its beats (about 1 to 4 seconds each, at most 120).
- Each slice is measured: pitch, loudness, brightness, note density, duration.
- Each slice becomes one room. Its height, length, openness, material and spacing come from the measurements.
- Rooms are placed one after another, forming a path.
- The pavilion is divided into five connected zones that follow the song: intro, rhythm, harmony, climax and outro.
- A camera walks the path in time with the song's clock, with the music playing if you want.

---

## 2. Quick start

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the link it prints (normally http://localhost:8501). On the **Studio** page, tick **Use demo data** to see a pavilion straight away, or upload a short MP3 or WAV (30 to 60 seconds is best).

Notes:
- **Windows:** if `streamlit.exe` is blocked by a Device Guard policy, always start the app with `python -m streamlit run app.py` (or `py -m streamlit run app.py`).
- **Python version:** librosa depends on `numba`, which can lag behind the newest Python. If installing fails on Python 3.14, use Python 3.11 or 3.12.
- **Streamlit version:** 1.46 or newer is required for the top navigation bar. On an older version the app falls back to a sidebar menu, and the microphone recorder needs 1.40 or newer.
- **Internet:** the 3D viewer loads Three.js from a CDN, and the page fonts come from Google Fonts, so you need to be online.
- **FFmpeg:** needed to decode MP3 files (`packages.txt` installs it on Streamlit Cloud).

---

## 3. The app: four pages

Navigation is a bar across the top of the page.

| Page | What it is |
|---|---|
| **Home** | The landing page. A hero made of music bars arranged in a ring. Moving the cursor makes nearby bars spike, and scrolling unrolls the ring into a flat skyline (music turning into architecture). Below it: scrolling outlined words, the three-step idea, and the five zones as animated cards. |
| **Studio** | The working tool. Choose a music source, set the rules, and get stat cards, an architectural parameter summary, the 3D pavilion with walkthrough and room inspector, the Musical Feature Analysis charts, a JSON download and the segment data table. |
| **Gallery** | Four original sample tracks, each with a **See its architecture** button. Clicking one analyses it and shows its stats, parameter summary, 3D pavilion and analysis charts, with the walk and music. Hovering a sleeve slides a record out from behind it. |
| **Method** | Ten cards, one per musical element, each with a small animation that speeds up on hover. Plus the pipeline, the tech chips and an honest note on limits. |

### Studio controls (sidebar)

| Control | Range | Effect |
|---|---|---|
| Max audio length (s) | 20 to 300, default 90 | Only this much of the song is analysed. The pavilion and the walk cover this part only. |
| Analyse the whole song | on/off | Raises the cap to 600 seconds (slower; can be heavy on free hosting). |
| Beats per space | 1 to 8, default 2 | How many beats go into one room. |
| Height range (pitch) | 2 to 30, default 3 to 18 | Lowest and highest wall height. |
| Length scale (duration) | 0.5 to 2.0 | Makes all rooms longer or shorter. |
| Path turning (melody) | 0 to 2.0, default 0.6 | How strongly the route curves. 0 is a straight line. |
| Divide pavilion into zones | on/off | Turns the five zones on or off. |
| Intro / Outro / Climax length (%) | 5 to 30, default 15 each | How much of the song each zone takes. |

Mapping sliders update the result instantly. Only the analysis settings re-analyse the song, because the analysis is cached.

---

## 4. Project structure

```
spatial-score/
├── app.py                    Entry point: page config, navigation, theme
├── requirements.txt          Python packages
├── packages.txt              System package (ffmpeg) for Streamlit Cloud
├── README.md                 This file
├── .streamlit/
│   └── config.toml           Dark theme colours
├── core/
│   ├── __init__.py
│   ├── analysis.py           Listens to the audio (librosa)
│   └── mapping.py            Music measurements -> architecture, zones, path
├── views/                    The four pages
│   ├── home.py
│   ├── studio.py
│   ├── gallery.py
│   └── method.py
├── ui/                       Frontend building blocks
│   ├── __init__.py
│   ├── theme.py              CSS and the script that adds scroll/hover effects
│   └── graphics.py           SVG icons, hero canvas, cards, parameter summary
├── viewer/
│   └── scene.html            The 3D scene and walkthrough (Three.js)
├── assets/
│   └── samples/              Four original sample tracks (mp3)
├── tools/
│   └── make_samples.py       Script that synthesised the sample tracks
└── tests/
    └── test_mapping.py       Checks for the mapping engine
```

Data flows one way:

```
views/studio.py (or gallery.py) -> core/analysis.py -> features -> core/mapping.py -> architecture JSON -> viewer/scene.html
```

(`assets/covers/` from an earlier version is no longer used and can be deleted.)

---

## 5. How it works, step by step

### 5.1 `core/analysis.py` (the ears)

`analyse(audio_bytes, filename, max_seconds, beats_per_segment)`:

1. **Load.** Saves the audio to a temporary file (so MP3 decoding works) and loads it as mono at 22,050 samples per second, keeping the first `max_seconds`. Under 1 second raises an error. It also records the full length of the track (`total_seconds`).
2. **Beats.** `librosa.beat.beat_track` gives the tempo and beat positions.
3. **Frame measurements** (frames of 512 samples, about 23 ms): loudness (RMS), brightness (spectral centroid), note onsets, and pitch (`pyin`, searched between C2 and C7).
4. **Segments.** A boundary every Nth beat. If fewer than 4 beats are found, fixed 2-second windows are used. A cap of 120 segments is enforced by thinning boundaries.
5. **Six numbers per segment:** start, duration, median pitch (as a MIDI note; silent segments reuse the previous pitch), average loudness, average brightness, and note density (onsets per second).

`demo_features()` returns synthetic data in the same format so the whole pipeline works without any audio.

### 5.2 `core/mapping.py` (the translator)

1. **Normalise.** Pitch, loudness, brightness and density are each rescaled to 0 to 1 across the song, using the 5th and 95th percentiles so one extreme moment doesn't squash everything. Every song therefore uses the full range of rooms.
2. **Apply the rules** (section 6) to make one room per segment.
3. **Assign zones** (section 7) and apply each zone's effects.
4. **Place the rooms** along a path, each starting where the previous one ended. The output is a JSON structure with every room's dimensions, zone, light level, position and heading.

### 5.3 `viewer/scene.html` (the builder)

Receives that JSON and the (optional) audio, and draws the pavilion. See section 8.

---

## 6. The mapping rules

| Music | Becomes | Rule (n = normalised 0 to 1 value) |
|---|---|---|
| **Pitch** | Height | `height = hmin + (hmax - hmin) x pitch_n` |
| **Duration** | Spatial length | `length = clip(duration x 1.5 x length_scale x compression, 2, 12)` |
| **Tempo** | Compression / expansion | `compression = clip(100 / tempo, 0.6, 1.5)`. Fast songs squeeze every room, slow songs stretch them. |
| **Rhythm / texture** | Spacing and ribs | `spacing = 2.5 - 1.9 x density_n`; `ribs = max(2, int(length / spacing))` |
| **Dynamics** | Openness | `openness = loudness_n`. Loud songs open the walls and drop the roof. |
| **Timbre** | Material | brightness_n below 0.34 is concrete, below 0.67 is wood, otherwise glass |
| **Melody** | Path | The pitch contour is smoothed over 5 segments, then `heading = heading x 0.9 + (change in smoothed pitch) x turn_strength x 6`. |

**Why the path rule works this way:** an earlier version turned the path by pitch *height*, and the turns added up until the route curled into a loop (it was tested on a real 5:41 song, where the heading reached 248 degrees). Turning by pitch *movement* means a rising melody bends the corridor one way and a falling one bends it the other, and the 0.9 factor keeps pulling it back toward straight. On the same song the heading stays within about 70 degrees and the path forms a gentle S-curve. The old rule is still available as `path_mode="level"`.

---

## 7. The five zones

The pavilion is divided into five connected zones following the song's progression. `assign_zones()` labels every segment:

| Zone | How it is found | What the pavilion does |
|---|---|---|
| **Intro** | First 15% of the song | Enclosed (openness x 0.3), half the ribs, soft dim warm light |
| **Rhythm** | Middle segments with above-median note density | More repeated ribs and columns, spacing follows the beat |
| **Harmony** | Middle segments with below-median note density (more sustained) | Two overlapping glass layers per room, at different heights |
| **Climax** | The loudest 15% window between intro and outro, slightly biased to come later | Height x 1.4, outward-leaning walls, tapered spires instead of ribs, no roof, pulsing coloured light |
| **Outro** | Last 15% of the song | Rooms get lower, more open and dimmer, fading gradually |

Rhythm and harmony labels are smoothed with a 5-segment majority filter so zones stay connected instead of flickering. Each zone has its own light colour: warm amber, blue, violet, red, green.

Honest note: "harmony" here is chosen from how sustained or busy the music is, not from real chord detection.

---

## 8. The 3D viewer and walkthrough

### What is drawn for each room
- a floor slab
- two walls (opacity falls as openness rises; in the climax they lean outward)
- a roof, only when openness is below 0.6 (never in the climax)
- ribs along both outer sides (tapered spires in the climax)
- two overlapping glass layers in harmony rooms
- a glowing light strip on the ceiling, coloured by zone; the climax lights pulse and a few real point lights flicker

Materials: concrete is grey and solid, wood is brown and solid, glass is light blue and at most 45% opaque.

### Controls
- **Orbit:** drag to rotate, scroll to zoom.
- **Walkthrough:** a silent walk along the song's timeline. It lasts exactly as long as the analysed part of the song.
- **Walk with music:** the same walk with the song playing (shown only when audio is loaded).
- **Pause / play** and a **seek bar** to scrub; the camera follows instantly.
- **Speed:** 0.5x, 1x, 1.5x, 2x, 3x or 4x. The walk goes faster or slower, and with music the song does too (pitch is kept where the browser supports it). 4x is the maximum because browsers mute audio beyond that.
- **Full experience:** a toggle that works in both walks. When on, the camera looks up in tall rooms and sways gently, drifts sideways through the harmony layers, rises and widens its field of view in the climax, and pulls back to an aerial view of the whole pavilion in the last seconds.
- The current zone name shows while walking, and a legend shows the zone colours.

### How the sync works
Every room came from one segment of the song and remembers its `start_time`. The viewer reads the current song time (the audio clock, or a silent clock), finds which segment that is, and places the camera that far along that room's floor. When the chorus hits, you are in the climax zone. Rooms from short segments pass quickly, long ones slowly.

### Why the walk can be shorter than the song
Only the first "Max audio length" seconds are analysed (default 90). The app shows a warning with both lengths. Raise the slider or tick **Analyse the whole song** to cover the full track.

---

## 8b. Musical Feature Analysis and the room inspector

Below the 3D pavilion (Studio and Gallery) is a **Musical Feature Analysis** section. All charts share one time axis, so you can read them against each other and against the model.

| Chart | What it shows |
|---|---|
| **Waveform** | Amplitude over time, coloured by section |
| **Beat detection** | Detected beats (every fourth in red) and the local tempo curve |
| **Pitch** | The pitch contour over time, plus a **pitch distribution** (which of the 12 notes the song uses) |
| **Energy and intensity** | Loudness over time; the dashed steps are the loudness value each room receives |
| **Musical layers** | Five frequency bands, bass to treble, as a colour heat-map |
| **Section detection** | The five zones found in the song, with a time axis |

**Click a room in the model, or any point on any chart**, and the **inspector panel** (top right of the 3D view) shows which musical information shaped that room's geometry: the measured value, how it ranks within the song (a bar from 0 to 100%), and the result it produced.

| Musical information | Inspector shows | Geometry result |
|---|---|---|
| Pitch | Note name and MIDI number | Height (and the value before the zone effect) |
| Duration and tempo | Seconds, tempo, squeeze factor | Length |
| Note density | Notes per second | Rib spacing and rib count |
| Loudness | RMS value | Openness and how solid the walls are |
| Brightness | Frequency in Hz | Material |
| Melody movement | Change in smoothed pitch | Path turn in degrees |
| Song position | Zone and why it was chosen | The zone's effect and light level |

The selected room is outlined in white in the model, and as a white band on every chart. During a walkthrough the inspector follows you from room to room, and a playhead line moves across the charts.

Above the viewer, an **Architectural parameters** summary shows the real generated values: room count, path length, height range and average, average openness, total ribs, a material split bar, and a per-zone table (rooms, average height and length, openness, density, ribs, light).

Where the data comes from: `core/analysis.py` returns a compact `viz` block (300 points per chart, the beat times, five band energies) next to the per-segment features. `core/mapping.py` adds `raw`, `norm` and `base` values to every room so the inspector can explain it.

## 9. The frontend design

- **Dark, cinematic theme** (crimson, violet and blue on near-black), with Syne and Inter fonts. **No emojis** anywhere.
- **Multi-page** with a top navigation bar (`st.navigation`).
- **Cursor glow:** a soft red light follows the mouse across the page.
- **Scroll progress line** across the top edge.
- **Reveal on scroll:** sections fade and rise into place as they appear.
- **3D hover tilt:** cards tilt toward the cursor with a moving highlight.
- **Scroll-driven motion:** giant outlined words slide sideways as you scroll, and gallery tiles drift at different speeds (capped at 60 pixels so they never overlap other content).
- **Animated graphics** built from SVG and CSS: equalizer bars, drawn melody lines, floating glass layers, twinkling texture dots, sliding walls.
- **Hero visualiser:** an HTML canvas that reacts to the cursor and to scrolling.

How it works: `ui/theme.py` adds the CSS and one small script that reaches the parent page from inside Streamlit's embedded frame to add the cursor glow, scroll progress, reveal, tilt and parallax effects. This works on current Streamlit versions, but a future Streamlit update could change it.

---

## 10. Music sources

| Source | How it works |
|---|---|
| **Upload a file** (Studio) | MP3, WAV, OGG or FLAC. |
| **Record with microphone** (Studio) | Streamlit's built-in recorder (`st.audio_input`, Streamlit 1.40 or newer). It records a clip, then the app analyses it like an uploaded file, and the walk plays your recording back. After recording, the app shows how much audio was captured and warns if it is almost empty. |
| **Sample tracks** (Gallery) | Four original tracks synthesised for this project: Hazy Rooms (68 BPM, slow and dark), Neon Drive (122 BPM), Glass Piano (80 BPM), Pulse City (140 BPM). Each has an intro, a beat section, a lush sustained section, a climax and an outro. Any audio file placed in `assets/samples/` also gets its own button. |
| **Spotify** | Not supported. Spotify does not give apps the raw audio of its tracks (it is copy-protected, and its audio-analysis API is closed to new apps). Use a file you own, or record the song with the microphone while it plays. |

Recording is clip-based, not real-time.

---

## 11. Tech stack

| Layer | Tool | Role |
|---|---|---|
| Web app | Streamlit | Pages, navigation, upload, recorder, sliders, caching, hosting |
| Audio analysis | librosa, NumPy, SciPy, soundfile | Beats, pitch, loudness, brightness, onsets |
| Data | pandas | Segment table |
| 3D | Three.js r128 (via cdnjs) | Geometry, lights, camera, walkthrough |
| Graphics | SVG, CSS animation, HTML canvas | Icons, hero visualiser, hover and scroll effects |
| Fonts | Google Fonts (Syne, Inter) | Typography |
| MP3 decoding | ffmpeg (`packages.txt`) | Needed on Streamlit Cloud |
| Hosting | Streamlit Community Cloud | Free, deployed from a public GitHub repo |

`requirements.txt`: streamlit>=1.46, librosa>=0.10, numpy, scipy, pandas, soundfile, pillow.

---

## 12. Deploying for free

1. Put the project in a **public GitHub repository**. Keep `app.py` and `requirements.txt` in the same folder.
2. Go to Streamlit Community Cloud, sign in with GitHub, click **New app**, and pick the repo and `app.py`.
3. Deploy and share the link. The app sleeps when idle and wakes in a few seconds. After updating files on GitHub, it redeploys on its own (or use **Manage app, Reboot app**).

Free hosting has about 1 GB of RAM, so keep "Max audio length" at 90 to 120 seconds. Make sure the `.streamlit` folder (its name starts with a dot) is uploaded too; browsers sometimes skip it when dragging and dropping.

---

## 13. Troubleshooting

| Problem | Fix |
|---|---|
| `streamlit.exe was blocked by Device Guard` | Run `python -m streamlit run app.py` instead. |
| `pip install` fails on librosa | Use Python 3.11 or 3.12 instead of the newest Python. |
| `SyntaxError` at an import line after an update | One of the files in `core/` or `ui/` was copied wrongly. Re-upload the original file as a file (GitHub: Add file, Upload files) instead of copy-pasting, then reboot. The log under **Manage app** names the exact file and line. |
| Top navigation looks like a sidebar menu | Your Streamlit is older than 1.46. Update `requirements.txt` and reboot. |
| Microphone recorder missing or not working | Needs Streamlit 1.40 or newer. Allow microphone access in the browser (lock icon beside the address bar), and pick the right input device in the browser and in Windows Sound settings. If the headset mic is dead, use the laptop's built-in mic, or record on a phone and upload the file. |
| The walk is shorter than the song | Only the first "Max audio length" seconds are analysed. Raise it or tick "Analyse the whole song". |
| No sound in "Walk with music" | Browsers only start sound after a click. Also, files over 15 MB are not embedded and play without music. |
| Gallery tracks take a few seconds the first time | Each track is analysed on first click and then cached. |

---

## 14. Limitations

- **Pitch** is clearest on a single melody (voice, flute, piano). On a full band mix it is approximate.
- **Harmony and form** are approximations (sustained passages and loudness, not real chord or verse/chorus detection).
- **Tempo** can be read at double or half its real value on some songs.
- **Analysis speed:** pitch tracking (`pyin`) is the slowest step. Expect several seconds to a minute for 90 seconds of audio.
- **High "Path turning" values** can bend the path back on itself, and rooms can leave small gaps at sharp bends.
- **Free hosting** limits memory and CPU, so very long files may fail.
- The scroll and hover effects depend on a script that reaches into Streamlit's page, which a future Streamlit update could break.
- The result is an **interpretation** of the music, not a structural design.

---

## 15. How to change things

| I want to... | Edit |
|---|---|
| Change what pitch does (for example width instead of height) | `core/mapping.py`, the `height = ...` line |
| Change material thresholds | `_material()` in `core/mapping.py` |
| Change what a zone does | The `if zone == ...` block in `core/mapping.py` |
| Change zone lengths or how climax is found | `assign_zones()` in `core/mapping.py` |
| Make the path curvier or straighter | The `heading = ...` line in `core/mapping.py` (the `* 6` factor) |
| Change room shape (arches, slopes, curved walls) | The `segs.forEach` block in `viewer/scene.html` |
| Add a colour or material | `BASE` and `ZC` in `viewer/scene.html`, and `_material()` |
| Change walking speed options | The `<select id="speed">` in `viewer/scene.html` |
| Change colours, fonts or hover effects | `CSS` in `ui/theme.py` |
| Change the hero animation | `hero_html()` in `ui/graphics.py` |
| Add a sample track | Put an audio file in `assets/samples/` |
| Regenerate the sample tracks | `python tools/make_samples.py` (needs numpy, scipy, ffmpeg) |

Run the tests with `pip install pytest` then `python -m pytest tests`.

---

## 16. Roadmap

- [x] Upload, analyse, map, 3D view, JSON export
- [x] Five zones following the song's progression
- [x] Walkthrough and Walk with music, synced to the song, with seek and speed
- [x] Full experience camera (look up, sway, rise, aerial finale)
- [x] Microphone recording
- [x] Multi-page frontend with animated graphics and sample tracks
- [ ] Real chord-based harmony layers
- [ ] Verse and chorus detection for better zones
- [ ] OBJ / GLB export for Rhino and Blender
- [ ] Real-time building while music plays
- [ ] Touch controls for the 3D viewer
- [ ] Preset styles (sculptural, urban, interior)

---

## Credits

Concept and mapping framework: **Agna**. Technical development: **Bhavya Kalra**. Thanks to Vibha ma'am for connecting the collaborators. Built with librosa, Streamlit and Three.js. The sample tracks are original, synthesised for this project. License: MIT (suggested; update as the team decides).
