"""Generates the original sample tracks in assets/samples/ (synthesised from scratch, no copyrighted material).
Run:  python tools/make_samples.py   (needs numpy, scipy and ffmpeg)"""
import os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

SR = 22050
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
lp = lambda x, a: lfilter([a], [1, -(1 - a)], x)


def tone(m, dur, wave="saw", vol=.2, a=.01, r=.15, cut=.3, det=0.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = NOTE(m)
    def w(ff):
        ph = (ff * t) % 1
        return {"saw": 2 * ph - 1, "sq": np.sign(ph - .5) * .7, "tri": 4 * np.abs(ph - .5) - 1}.get(wave, np.sin(2 * np.pi * ff * t))
    x = w(f) + (w(f * (1 + det)) if det else 0)
    x = lp(x, cut) if cut < 1 else x
    e = np.ones(n); an = max(1, int(a * SR)); rn = max(1, min(n, int(r * SR)))
    e[:an] = np.linspace(0, 1, an); e[-rn:] *= np.linspace(1, 0, rn)
    return x * e * vol


def kick(v=.7):
    t = np.arange(int(.22 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 18) + 45) / SR) * np.exp(-t * 14) * v


def hat(v=.15):
    n = int(.05 * SR); return np.random.randn(n) * np.exp(-np.arange(n) / SR * 90) * v


def snare(v=.4):
    n = int(.18 * SR); t = np.arange(n) / SR
    return (np.random.randn(n) * .7 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t * 22) * v


def put(buf, x, at):
    i = int(at * SR)
    if i < len(buf):
        j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]


def zone(fr):
    return "intro" if fr < .15 else "rhythm" if fr < .40 else "harmony" if fr < .60 else "climax" if fr < .82 else "outro"


def render(s, seconds=60):
    np.random.seed(s["seed"]); rng = np.random.default_rng(s["seed"])
    beat = 60 / s["bpm"]; nb = int(seconds / beat)
    buf = np.zeros(int(seconds * SR) + SR)
    gain = {"intro": .55, "rhythm": .3, "harmony": 1.0, "climax": .8, "outro": .5}
    pick = lambda oct_: s["key"] + s["scale"][rng.integers(len(s["scale"]))] + oct_
    for bar in range(nb // 4 + 1):
        tb = bar * 4 * beat; z = zone(tb / seconds); ch = s["chords"][bar % len(s["chords"])]
        for m in ch:
            put(buf, tone(m, 4 * beat + .3, s["pad"], .09 * gain[z], a=.4, r=.6, cut=s["cut"], det=.006), tb)
            if z == "harmony":
                put(buf, tone(m + 12, 4 * beat + .3, "tri", .05, a=.6, r=.8, cut=.5), tb)
    for b in range(nb):
        tb = b * beat; z = zone(tb / seconds); ch = s["chords"][(b // 4) % len(s["chords"])]
        if z in ("rhythm", "climax"):
            if s["kick"] == "four" or b % 2 == 0: put(buf, kick(), tb)
            put(buf, tone(ch[0] - 12, beat * .9, s["bass"], .18, a=.005, r=.1, cut=.08), tb)
            for h in ((0, .5) if z == "rhythm" else (0, .25, .5, .75)): put(buf, hat(.12 if z == "rhythm" else .18), tb + h * beat)
            if s["snare"] and b % 4 in (1, 3): put(buf, snare(), tb)
            if s["arp"]:
                for k, h in enumerate((0, .5) if z == "rhythm" else (0, .25, .5, .75)):
                    put(buf, tone(ch[k % 3] + 12 + (12 if z == "climax" and k % 2 else 0), beat * .22, s["lead"], .07, a=.003, r=.08, cut=.5), tb + h * beat)
        if z == "climax" and b % 2 == 0: put(buf, tone(pick(24), beat * 1.6, s["lead"], .1, a=.02, r=.3, cut=.6), tb)
        if z == "harmony" and b % 4 == 0: put(buf, tone(pick(12), beat * 3.5, "sine", .1, a=.3, r=.8), tb)
        if z in ("intro", "outro") and b % 8 == 0: put(buf, tone(pick(12), beat * 3, "sine", .07, a=.2, r=.8), tb)
    buf = buf[: int(seconds * SR)]
    fade = int(3 * SR); buf[-fade:] *= np.linspace(1, 0, fade)
    return np.tanh(buf / (np.abs(buf).max() + 1e-9) * 1.6) * .9


TRACKS = {
    "hazy-rooms": dict(bpm=68, key=57, scale=[0, 3, 5, 7, 10], chords=[[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]], pad="saw", cut=.12, lead="sine", bass="saw", kick="half", snare=True, arp=False, seed=1),
    "neon-drive": dict(bpm=122, key=54, scale=[0, 2, 3, 5, 7, 8, 10], chords=[[54, 57, 61], [50, 54, 57], [57, 61, 64], [52, 56, 59]], pad="saw", cut=.2, lead="saw", bass="saw", kick="four", snare=True, arp=True, seed=2),
    "glass-piano": dict(bpm=80, key=60, scale=[0, 2, 4, 7, 9], chords=[[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]], pad="tri", cut=.3, lead="tri", bass="tri", kick="half", snare=False, arp=True, seed=3),
    "pulse-city": dict(bpm=140, key=52, scale=[0, 3, 5, 7, 10], chords=[[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]], pad="sq", cut=.15, lead="sq", bass="sq", kick="four", snare=True, arp=True, seed=4),
}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "samples")
    os.makedirs(out, exist_ok=True)
    for name, spec in TRACKS.items():
        wav = os.path.join(out, name + ".wav")
        wavfile.write(wav, SR, (render(spec) * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-b:a", "96k", os.path.join(out, name + ".mp3")], check=True)
        os.remove(wav); print("made", name)
