"""Mapping engine: musical features -> architectural parameters.

  pitch    -> height          duration -> length
  rhythm   -> spacing/ribs    tempo    -> compression / expansion
  dynamics -> openness        timbre   -> material
  texture  -> density         melody   -> path (turning of the corridor)
"""
import math

import numpy as np


def _norm(values):
    """Robust 0-1 normalisation (5th-95th percentile)."""
    v = np.asarray(values, dtype=float)
    lo, hi = np.percentile(v, 5), np.percentile(v, 95)
    if hi - lo < 1e-9:
        return np.full_like(v, 0.5)
    return np.clip((v - lo) / (hi - lo), 0.0, 1.0)


def _material(c):
    return "concrete" if c < 0.34 else "wood" if c < 0.67 else "glass"


def map_features(features, height_range=(3.0, 18.0), length_scale=1.0,
                 turn_strength=0.6, width=4.0):
    segs = features["segments"]
    if not segs:
        return {"tempo": features.get("tempo", 0), "width": width, "segments": []}

    pitch = _norm([s["pitch_midi"] for s in segs])
    energy = _norm([s["rms"] for s in segs])
    bright = _norm([s["centroid"] for s in segs])
    dens = _norm([s["onset_density"] for s in segs])

    tempo = float(features.get("tempo") or 100.0)
    compression = float(np.clip(100.0 / tempo, 0.6, 1.5))  # fast = compressed

    out, heading, px, pz = [], 0.0, 0.0, 0.0
    hmin, hmax = height_range
    for i, s in enumerate(segs):
        length = float(np.clip(s["duration"] * 1.5 * length_scale * compression, 2.0, 12.0))
        height = hmin + (hmax - hmin) * float(pitch[i])
        spacing = 2.5 - (2.5 - 0.6) * float(dens[i])
        heading += (float(pitch[i]) - 0.5) * turn_strength * 0.5
        dx, dz = math.sin(heading), math.cos(heading)
        out.append({
            "segment": i,
            "start_time": round(s["start"], 2),
            "duration": round(s["duration"], 2),
            "height": round(height, 2),
            "length": round(length, 2),
            "spacing": round(spacing, 2),
            "ribs": max(2, int(length / spacing)),
            "openness": round(float(energy[i]), 2),
            "density": round(float(dens[i]), 2),
            "material": _material(float(bright[i])),
            "heading": round(heading, 3),
            "x0": round(px, 2), "z0": round(pz, 2),
            "x": round(px + dx * length / 2, 2), "z": round(pz + dz * length / 2, 2),
        })
        px += dx * length
        pz += dz * length
    return {"tempo": round(tempo, 1), "width": width, "segments": out}
