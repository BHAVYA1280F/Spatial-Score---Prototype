"""Audio analysis: turns an audio file into per-segment musical features."""
import os
import tempfile

import numpy as np

HOP = 512
SR = 22050
MAX_SEGMENTS = 120


def demo_features(n=28):
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
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP)[0]
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
    return {"tempo": tempo, "total_seconds": total, "segments": segments}