"""Mapping engine: musical features -> architectural parameters.

Per-room rules:
  pitch -> height        duration -> length       tempo -> compression/expansion
  rhythm/texture -> spacing + ribs                dynamics -> openness
  timbre -> material     melody -> path turning

Pavilion zones (song progression): intro -> rhythm / harmony -> climax -> outro
All final dimensions are in metres (see _architect).
"""
import math

import numpy as np

ZONE_ORDER = ["intro", "rhythm", "harmony", "climax", "outro"]


def _norm(values):
    """Robust 0-1 normalisation (5th-95th percentile)."""
    v = np.asarray(values, dtype=float)
    lo, hi = np.percentile(v, 5), np.percentile(v, 95)
    if hi - lo < 1e-9:
        return np.full_like(v, 0.5)
    return np.clip((v - lo) / (hi - lo), 0.0, 1.0)


def _material(c):
    return "concrete" if c < 0.34 else "wood" if c < 0.67 else "glass"


PATTERN = {"intro": "soft membrane", "rhythm": "twisted rib lattice", "harmony": "petal shells",
           "climax": "tree-column canopy", "outro": "dissolving ribs", "none": "woven lattice"}


def _architect(out, length_scale):
    """Convert the rooms (abstract units) into pavilion dimensions in metres."""
    n = len(out)
    Lp = float(np.clip(18 + 0.25 * n, 18, 48)) * length_scale
    k = Lp / max(1e-9, sum(o["length"] for o in out))
    px = pz = carry = carry_b = 0.0
    for o in out:
        z, t, d = o["zone"], o.get("zt", 0.0), o["density"]
        L = o["length"] * k
        h = max(1.8, 1.2 + 0.42 * o["height"])
        hb = max(1.8, 1.2 + 0.42 * o["base"]["height"])
        sp = 1.7 - 1.2 * d
        sp_zone = sp * {"intro": 1.6, "rhythm": 0.7, "climax": 0.8, "outro": 1 + 0.8 * t}.get(z, 1.0)
        hd = o["heading"] * 0.5
        carry += L / sp_zone          # carry the remainder so the average arch spacing is preserved
        nr = int(carry)
        carry -= nr
        carry_b += L / sp
        nb = int(carry_b)
        carry_b -= nb
        o.update(length=round(L, 2), height=round(h, 2), spacing=round(sp_zone, 2), ribs=nr, heading=round(hd, 3))
        o["base"] = {"height": round(hb, 2), "openness": o["base"]["openness"], "ribs": nb}
        o["width"] = round(5 + 8 * o["openness"], 1)
        o["arch_p"] = round(0.7 + 0.8 * o["norm"]["bright"], 2)
        o["twist"] = round(float(np.clip(o["move"] * 220, -70, 70)), 1)
        o["weave"] = round({"intro": .05, "rhythm": .3, "harmony": .55, "climax": .4, "outro": .1}.get(z, .25) + .25 * d, 2)
        o["pattern"] = PATTERN.get(z, "woven lattice")
        dx, dz = math.sin(hd), math.cos(hd)
        o.update(x0=round(px, 2), z0=round(pz, 2), x=round(px + dx * L / 2, 2), z=round(pz + dz * L / 2, 2))
        px += dx * L
        pz += dz * L


def assign_zones(energy, dens, intro_frac=0.15, outro_frac=0.15, climax_frac=0.15):
    """Label every segment intro / rhythm / harmony / climax / outro.

    intro  = first part of the song      outro = last part
    climax = the loudest window in between (slightly biased to come later)
    rest   = 'rhythm' where note density is above the middle value, else 'harmony',
             smoothed so zones stay connected instead of flickering.
    """
    n = len(energy)
    if n < 5:
        return ["intro"] + ["climax"] * (n - 2) + ["outro"] if n >= 3 else ["climax"] * n
    n_out = min(max(1, round(n * outro_frac)), n - 2)
    n_in = min(max(1, round(n * intro_frac)), n - n_out - 1)
    body_end = n - n_out
    m = body_end - n_in
    n_cl = min(max(1, round(n * climax_frac)), m)

    best, best_s = -1.0, n_in
    for s in range(n_in, body_end - n_cl + 1):
        score = float(np.mean(energy[s:s + n_cl])) + 0.1 * (s / n)
        if score > best:
            best, best_s = score, s

    zones = ["intro"] * n_in + [None] * m + ["outro"] * n_out
    for i in range(best_s, best_s + n_cl):
        zones[i] = "climax"
    rest = [i for i in range(n_in, body_end) if zones[i] is None]
    if rest:
        med = float(np.median([dens[i] for i in rest]))
        raw = ["rhythm" if dens[i] > med else "harmony" for i in rest]
        for k, i in enumerate(rest):
            w = raw[max(0, k - 2):k + 3]
            r, h = w.count("rhythm"), w.count("harmony")
            zones[i] = raw[k] if r == h else ("rhythm" if r > h else "harmony")
    return zones


def map_features(features, height_range=(3.0, 18.0), length_scale=1.0,
                 turn_strength=0.6, width=4.0, zones=True,
                 intro_frac=0.15, outro_frac=0.15, climax_frac=0.15, path_mode="change"):
    segs = features["segments"]
    if not segs:
        return {"tempo": features.get("tempo", 0), "width": width, "zones": {}, "segments": []}

    pitch = _norm([s["pitch_midi"] for s in segs])
    energy = _norm([s["rms"] for s in segs])
    bright = _norm([s["centroid"] for s in segs])
    dens = _norm([s["onset_density"] for s in segs])
    n = len(segs)
    pitch_sm = np.convolve(np.pad(pitch, (2, 2), mode="edge"), np.ones(5) / 5, mode="valid")  # melody contour

    tempo = float(features.get("tempo") or 100.0)
    compression = float(np.clip(100.0 / tempo, 0.6, 1.5))  # fast = compressed
    zl = assign_zones(energy, dens, intro_frac, outro_frac, climax_frac) if zones else ["none"] * n
    seen = {}

    out, heading, px, pz = [], 0.0, 0.0, 0.0
    hmin, hmax = height_range
    for i, s in enumerate(segs):
        zone = zl[i]
        k, total = seen.get(zone, 0), zl.count(zone)
        seen[zone] = k + 1
        t = k / (total - 1) if total > 1 else 0.0       # progress inside the zone, 0..1

        length = float(np.clip(s["duration"] * 1.5 * length_scale * compression, 2.0, 12.0))
        height = hmin + (hmax - hmin) * float(pitch[i])
        spacing = 2.5 - (2.5 - 0.6) * float(dens[i])
        ribs = max(2, int(length / spacing))
        openness = float(energy[i])
        light, layers, tilt = 0.6, 0, 0.0
        base = {"height": round(height, 2), "openness": round(openness, 2), "ribs": ribs}

        if zone == "intro":        # enclosed, soft light, sparse structure
            openness *= 0.3
            ribs = max(2, int(ribs * 0.5))
            light = 0.3
        elif zone == "rhythm":     # repeated ribs, spacing follows note density
            ribs = int(ribs * 1.5) + 1
        elif zone == "harmony":    # overlapping layers at different heights
            layers, light = 2, 0.55
        elif zone == "climax":     # tall, leaning walls, spires, dynamic light
            height *= 1.4
            tilt = 0.18
            light = 0.7 + 0.3 * (1 - abs(2 * t - 1))
        elif zone == "outro":      # gradually calmer: lower, more open, dimmer
            height *= 1 - 0.5 * t
            openness += (1 - openness) * 0.5 * t
            ribs = max(2, int(ribs * (1 - 0.5 * t)))
            light = 0.5 * (1 - t) + 0.1

        h_prev, move = heading, 0.0
        if path_mode == "level":   # old rule: turn by pitch height (tends to loop)
            heading += (float(pitch[i]) - 0.5) * turn_strength * 0.5
        else:                      # new rule: turn by pitch movement, relaxing back to straight
            move = float(pitch_sm[i] - pitch_sm[i - 1]) if i > 0 else 0.0
            heading = heading * 0.9 + move * turn_strength * 6
        dx, dz = math.sin(heading), math.cos(heading)
        out.append({
            "segment": i, "zone": zone,
            "start_time": round(s["start"], 2), "duration": round(s["duration"], 2),
            "height": round(height, 2), "length": round(length, 2),
            "spacing": round(spacing, 2), "ribs": ribs,
            "openness": round(openness, 2), "density": round(float(dens[i]), 2),
            "material": _material(float(bright[i])),
            "light": round(light, 2), "layers": layers, "tilt": tilt,
            "raw": {"pitch_midi": round(float(s["pitch_midi"]), 2), "rms": round(float(s["rms"]), 4),
                    "centroid": round(float(s["centroid"]), 1), "onset_density": round(float(s["onset_density"]), 2)},
            "norm": {"pitch": round(float(pitch[i]), 3), "energy": round(float(energy[i]), 3),
                     "bright": round(float(bright[i]), 3), "density": round(float(dens[i]), 3)},
            "base": base, "move": round(move, 3), "turn_deg": round(math.degrees(heading - h_prev), 1),
            "zt": round(t, 3),
            "heading": round(heading, 3),
            "x0": round(px, 2), "z0": round(pz, 2),
            "x": round(px + dx * length / 2, 2), "z": round(pz + dz * length / 2, 2),
        })
        px += dx * length
        pz += dz * length
    _architect(out, length_scale)
    counts = {z: zl.count(z) for z in ZONE_ORDER + ["none"] if z in zl}
    return {"tempo": round(tempo, 1), "compression": round(compression, 2), "width": width, "zones": counts, "segments": out}
