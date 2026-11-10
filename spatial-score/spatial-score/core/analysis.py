"""Audio analysis: turns an audio file into per-segment musical features."""
import os
import tempfile

import numpy as np

HOP = 512
SR = 22050
MAX_SEGMENTS = 120


def _ds(x, n, fn=np.mean):
    """Downsample a 1-D array to n bins."""
    idx = np.linspace(0, len(x), n + 1).astype(int)
    return [float(fn(x[a:b])) if b > a else 0.0 for a, b in zip(idx[:-1], idx[1:])]


def _viz(y, sr, S, rms, f0, beat_frames, n=300):
    """Compact data for the Musical Feature Analysis charts."""
    import librosa

    freqs = librosa.fft_frequencies(sr=sr, n_fft=2 * (S.shape[0] - 1))
    wave = _ds(np.abs(y) / max(float(np.max(np.abs(y))), 1e-9), n, np.max)
    e = np.asarray(_ds(rms, n))
    e = np.clip(e / max(float(np.percentile(e, 95)), 1e-9), 0, 1)
    bands = []
    for lo, hi in [(20, 150), (150, 500), (500, 2000), (2000, 6000), (6000, sr / 2 + 1)]:
        m = (freqs >= lo) & (freqs < hi)
        row = np.log1p(30 * S[m].mean(0)) if m.any() else np.zeros(S.shape[1])
        row = np.asarray(_ds(row, n))
        p5, p98 = np.percentile(row, 5), np.percentile(row, 98)
        bands.append([round(float(v), 3) for v in np.clip((row - p5) / max(p98 - p5, 1e-9), 0, 1)])
    idx = np.linspace(0, len(f0), n + 1).astype(int)
    pitch = []
    for lo, hi in zip(idx[:-1], idx[1:]):
        v = f0[lo:hi]
        v = v[~np.isnan(v)]
        pitch.append(round(float(librosa.hz_to_midi(np.median(v))), 2) if len(v) >= max(1, (hi - lo) // 4) else None)
    beats = np.round(librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP), 3).tolist()
    return {"duration": round(len(y) / sr, 3), "wave": [round(v, 3) for v in wave],
            "energy": [round(float(v), 3) for v in e], "pitch": pitch, "bands": bands, "beats": beats}


def _demo_viz(segs, tempo, n=300):
    D = segs[-1]["start"] + segs[-1]["duration"]
    t = (np.arange(n) + .5) / n * D
    st = np.array([s["start"] for s in segs])
    idx = np.clip(np.searchsorted(st, t, side="right") - 1, 0, len(segs) - 1)
    rms = np.array([s["rms"] for s in segs])[idx]
    r = rms / rms.max()
    pitch = np.array([s["pitch_midi"] for s in segs])[idx] + 0.4 * np.sin(t * 3)
    bands = [[round(float(v), 3) for v in np.clip(r * (.5 + .5 * np.sin(t * (1.1 + k * .7) + k)), 0, 1)] for k in range(5)]
    return {"duration": round(float(D), 3), "wave": [round(float(v), 3) for v in np.clip(r * (.6 + .4 * np.abs(np.sin(t * 37))), 0, 1)],
            "energy": [round(float(v), 3) for v in r], "pitch": [round(float(v), 2) for v in pitch], "bands": bands,
            "beats": [round(float(b), 3) for b in np.arange(0, D, 60 / tempo)]}


def _demo_core(n=28):
    """Synthetic features so the app works without any audio file."""
    t = np.arange(n)
    pitch = 62 + 10 * np.sin(t / 3.5) + 4 * np.sin(t / 1.3)
    return {
        "tempo": 108.0,
        "segments": [
            {
                "start": float(i * 1.2),
                "duration": float(1.0 + 0.8 * (1 + np.sin(i / 4.0))),
                "pitch_midi": float(pitch[i]),
                "rms": float(0.1 + 0.08 * (1 + np.sin(i / 5.0))),
                "centroid": float(1500 + 1200 * (1 + np.sin(i / 7.0))),
                "onset_density": float(1.5 + 2.5 * (1 + np.sin(i / 2.5)) / 2),
            }
            for i in range(n)
        ],
    }


def analyse(audio_bytes, filename="audio.wav", max_seconds=90, beats_per_segment=2):
    """Extract tempo + per-segment features using librosa."""
    import librosa  # imported here so the app can still start without it

    suffix = os.path.splitext(filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        path = f.name
    try:
        try:
            total = float(librosa.get_duration(path=path))
        except Exception:  # noqa: BLE001
            total = None
        y, sr = librosa.load(path, sr=SR, mono=True, duration=max_seconds)
    finally:
        os.unlink(path)

    if len(y) < sr:
        raise ValueError("Audio is too short (need at least 1 second).")

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=HOP)
    tempo = float(np.atleast_1d(tempo)[0])

    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    centroid = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=HOP)
    f0, _, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        frame_length=2048,
        hop_length=HOP,
    )

    n = min(len(rms), len(centroid), len(f0))
    rms, centroid, f0 = rms[:n], centroid[:n], f0[:n]

    # Segment boundaries: every N beats, or fixed ~2 s windows if beats are unreliable.
    if len(beat_frames) >= 4:
        bounds = beat_frames[::beats_per_segment]
    else:
        bounds = np.arange(0, n, int(2 * sr / HOP))
    bounds = np.unique(np.concatenate([[0], bounds, [n]])).astype(int)
    bounds = bounds[bounds <= n]
    while len(bounds) > MAX_SEGMENTS + 1:
        bounds = np.unique(np.concatenate([bounds[::2], [n]]))

    segments, last_pitch = [], 60.0
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < 2:
            continue
        dur = (b - a) * HOP / sr
        seg_f0 = f0[a:b]
        if np.any(~np.isnan(seg_f0)):
            last_pitch = float(librosa.hz_to_midi(np.nanmedian(seg_f0)))
        n_on = int(np.sum((onsets >= a) & (onsets < b)))
        segments.append(
            {
                "start": float(a * HOP / sr),
                "duration": float(dur),
                "pitch_midi": last_pitch,
                "rms": float(np.mean(rms[a:b])),
                "centroid": float(np.mean(centroid[a:b])),
                "onset_density": float(n_on / dur),
            }
        )
    try:
        viz = _viz(y, sr, S, rms, f0, beat_frames)
    except Exception:  # noqa: BLE001
        viz = None
    return {"tempo": tempo, "total_seconds": total, "segments": segments, "viz": viz}


def demo_features(n=28):
    f = _demo_core(n)
    f["viz"] = _demo_viz(f["segments"], f["tempo"])
    return f
