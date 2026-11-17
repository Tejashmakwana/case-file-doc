"""Instruments and sound effects made in code (numpy only). score.py composes them for one film.
Every function returns a float array at SR (mono, or (n, 2) stereo) and is deterministic for a given seed."""
import numpy as np

SR = 48000
NOTES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
         "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
ROOT = 2  # set by set_key()


def set_key(name):
    global ROOT
    ROOT = NOTES[name]


def hz(semi, octave):
    """frequency of the key's root + semi semitones, in an octave (A4 = 440)."""
    return 440.0 * 2 ** ((ROOT + semi + 12 * (octave + 1) - 69) / 12)


# ---------------------------------------------------------------- dsp
def t_(d): return np.arange(int(SR * d)) / SR


def fft_filter(x, resp):
    n = 1 << (len(x) - 1).bit_length()
    X = np.fft.rfft(x, n); f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(X * resp(f), n)[: len(x)]


def lp(x, fc, order=2): return fft_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))
def hp(x, fc, order=2): return fft_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))
def bp(x, lo, hi): return hp(lp(x, hi), lo)


def peaks(x, centres, q=6.0, floor=0.02):
    """resonances (formants, an instrument body): gaussian peaks in log-frequency."""
    def r(f):
        lf = np.log2(np.maximum(f, 20))
        return floor + sum(a * np.exp(-0.5 * ((lf - np.log2(c)) * q) ** 2) for c, a in centres)
    return fft_filter(x, r)


def env(n, a=0.01, r=0.05):
    e = np.ones(n); na, nr = max(1, min(n, int(SR * a))), max(1, min(n, int(SR * r)))
    e[:na] = np.linspace(0, 1, na) ** 2; e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def dec(d, tau): return np.exp(-t_(d) / tau)


def saw(freq, d, harmonics=24, vib=None):
    t = t_(d); f = np.full_like(t, float(freq)) if np.isscalar(freq) else freq
    if vib is not None: f = f * vib
    ph = 2 * np.pi * np.cumsum(f) / SR
    nmax = max(1, int(min(harmonics, SR / 2 / np.max(f))))
    return sum(np.sin(k * ph) / k for k in range(1, nmax + 1))


def reverb(x, wet=0.3, decay=2.0, stereo=False, seed=0):
    r = np.random.default_rng(99 + seed); n = int(SR * decay)
    def conv():
        h = lp(r.standard_normal(n) * np.exp(-np.arange(n) / (SR * decay / 6.5)), 4500)
        L = len(x) + n; m = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:L]
        return y / (np.abs(y).max() + 1e-9) * (np.abs(x).max() + 1e-9)
    dry = np.concatenate([x, np.zeros(n)]) * (1 - wet)
    if not stereo: return dry + wet * conv()
    return np.stack([dry + wet * conv(), dry + wet * conv()], 1)


def place(dst, src, at):
    i = int(SR * at)
    if i >= len(dst): return dst
    j = min(len(dst), i + len(src)); dst[i:j] += src[: j - i]; return dst


def fit(x, n):
    """exactly n samples: pad with silence or cut with a short fade."""
    if len(x) >= n:
        y = x[:n].copy(); k = min(n, int(SR * 0.05)); f = np.linspace(1, 0, k)
        y[-k:] *= f if y.ndim == 1 else f[:, None]; return y
    pad = np.zeros((n - len(x),) + x.shape[1:]); return np.concatenate([x, pad])


def norm(x, peak=0.89, rms_db=None):
    if rms_db is not None:
        x = x * (10 ** (rms_db / 20) / (np.sqrt((x ** 2).mean()) + 1e-12))
        m = np.abs(x).max(); return x / m * 0.95 if m > 0.95 else x
    return x / (np.abs(x).max() + 1e-9) * peak


# ---------------------------------------------------------------- music (one minor key)
PHRASES = {
    1: [(7, 3.0), (8, 1.5), (7, 2.0), (3, 3.0), (2, 1.5), (0, 4.0), (-2, 2.0), (0, 3.0)],
    2: [(12, 3.0), (10, 1.5), (8, 2.0), (7, 4.0), (3, 2.0), (5, 2.0), (2, 2.0), (0, 5.0)],
}
CELLO = [0, -4, -7, -5]          # i, bVI, iv, v under each phrase
CHORDS = [[0, 3, 7], [-4, 0, 3], [5, 8, 12], [7, 10, 14]]


def drone(d, seed=0):
    """low root + fifth + octave, two detuned voices, a breathing filter and an airy "ooh"."""
    r = np.random.default_rng(seed); t = t_(d)
    tones = sum(saw(hz(s, o) * det, d, 16) * g for s, o, g in [(0, 2, 1.0), (7, 2, 0.55), (0, 3, 0.35)] for det in (0.9985, 1.0015))
    breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / 17.0 - np.pi / 2)
    body = lp(tones, 260, 3) * (1 - breath) + lp(tones, 700, 3) * breath
    air = peaks(r.standard_normal(len(t)), [(310, 1.0), (870, 0.6)], q=9, floor=0.0) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 23.0)) * 0.12
    return norm(fit(reverb(body + air, 0.35, 4.0, stereo=True, seed=seed), len(t)), rms_db=-20)


def strings(d, phrase=1, seed=0):
    """a bowed minor melody over a cello line, stretched to fill d seconds exactly."""
    r = np.random.default_rng(seed)
    nat = sum(x for _, x in PHRASES[1])
    loops = max(1, int(round(d / nat)))
    seq = [PHRASES[1 + ((phrase - 1 + i) % 2)] for i in range(loops)]
    notes = [n for ph in seq for n in ph]
    k = (d - 1.2) / sum(x for _, x in notes)
    v = np.zeros(int(SR * (d + 1))); at = 0.0
    for semi, dd in notes:
        dd *= k; n = dd + 0.35; tt = t_(n)
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.4 * tt + r.uniform(0, 6)) * np.clip((tt - 0.35) / 0.6, 0, 1)
        tone = saw(hz(semi, 4), n, 30, vib) + 0.04 * r.standard_normal(len(tt))
        place(v, tone * env(len(tt), min(0.28, dd / 3), min(0.45, dd / 2)), at); at += dd
    v = peaks(v, [(460, 1.0), (1100, 0.7), (2800, 0.55), (4200, 0.25)], q=3.0, floor=0.05)
    cello = np.zeros_like(v); cl = [c for _ in seq for c in CELLO]; cd = (d - 0.5) / len(cl)
    for i, semi in enumerate(cl):
        tt = t_(cd + 0.6)
        tone = saw(hz(semi, 3), cd + 0.6, 24, 1 + 0.004 * np.sin(2 * np.pi * 4.8 * tt))
        place(cello, lp(tone, 900) * env(len(tt), min(0.9, cd / 3), min(1.2, cd / 2)), i * cd)
    return norm(fit(reverb(v + 0.55 * cello, 0.38, 3.2, stereo=True, seed=seed), int(SR * d)), rms_db=-20)


def pad(d, seed=0):
    """slow supersaw minor chords i - bVI - iv - v, one change every ~8 s, filling d exactly."""
    n = max(1, int(round(d / 8.0))); cl = d / n
    x = np.zeros(int(SR * (d + 2)))
    for i in range(n):
        ch = CHORDS[i % len(CHORDS)]
        seg = sum(saw(hz(s, 3) * det, cl + 2.0, 18) for s in ch for det in (0.994, 0.998, 1.0, 1.002, 1.006))
        place(x, lp(seg, 1100, 2) * env(len(seg), min(2.2, cl / 3), 2.4), i * cl)
    x += lp(saw(hz(0, 2), len(x) / SR, 10), 200) * 0.6
    return norm(fit(reverb(x, 0.45, 4.5, stereo=True, seed=seed), int(SR * d)), rms_db=-20)


def swell(seed=0, peak=5.3, d=10.0):
    """a choir "aah" crescendo whose loudest moment is `peak` s into the returned array."""
    tt = t_(d)
    ch = sum(saw(hz(s, o) * det, d, 28, 1 + 0.005 * np.sin(2 * np.pi * (5 + k) * tt + k))
             for k, (s, o) in enumerate([(0, 3), (7, 3), (0, 4), (3, 4), (7, 4)]) for det in (0.997, 1.003))
    ch = peaks(ch, [(750, 1.0), (1200, 0.8), (2600, 0.45)], q=5.0, floor=0.02)
    shape = np.where(tt < peak, (tt / peak) ** 2.2, np.exp(-(tt - peak) / 1.3))
    return norm(fit(reverb(ch * shape, 0.4, 3.5, stereo=True, seed=seed), len(tt)))


def hit(kind="name", seed=0, lead=3.0):
    """Ping Boom: a reversed swell `lead` s long into a bell "ping" + sub "boom", then a long tail.
    kind: name (key root) | hook (minor sixth, for the opening) | title (root, darker, longer)."""
    semi = {"name": 0, "hook": 8, "title": 0}[kind]
    bt = t_(6.5)
    ping = sum(g * np.sin(2 * np.pi * hz(semi, 5 if kind != "title" else 4) * m * bt) * np.exp(-bt / tau)
               for m, g, tau in [(1, 1.0, 2.2), (2.0, 0.5, 1.4), (2.76, 0.35, 0.9), (4.07, 0.2, 0.5), (5.4, 0.12, 0.3)])
    f = hz(semi, 1) * (1 + 1.2 * np.exp(-bt / 0.09))
    boom = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-bt / (1.6 if kind != "title" else 2.4)))
    r = np.random.default_rng(seed)
    click = np.zeros_like(bt); nc = int(SR * 0.03); click[:nc] = bp(r.standard_normal(nc), 800, 6000) * np.linspace(1, 0, nc)
    h = (0.55 * ping + boom + 0.35 * click) * (1 + 0.6 * np.exp(-bt / 0.04)) * env(len(bt), 0.0005, 2.0)
    tail = 0.3 * reverb(h, 1.0, 5.0, stereo=True, seed=seed); tail[: len(h)] += h[:, None]
    sw = reverb(0.6 * ping, 1.0, lead, seed=seed + 1)[: int(SR * lead)][::-1]
    sw = sw * np.linspace(0, 1, len(sw)) ** 2.5
    x = np.zeros((int(SR * lead) + len(tail), 2)); x[: len(sw)] += sw[:, None] * 0.6; x[int(SR * lead):] += tail
    return norm(x)


def riser(d=3.0, seed=0):
    """noise + tone rising for d seconds; loudest at its very end."""
    r = np.random.default_rng(seed); tt = t_(d); ramp = (tt / d) ** 2.5
    nz = r.standard_normal(len(tt)); body = lp(nz, 500) * (1 - ramp) + hp(nz, 1500) * ramp
    tone = np.sin(2 * np.pi * np.cumsum(200 * 8 ** (tt / d)) / SR)
    return norm((0.8 * body + 0.3 * tone) * ramp)


# ---------------------------------------------------------------- sound effects
def _tick(r, f=None, d=0.07, tau=None, nb=None, body=0.5):
    f = f or r.uniform(800, 2600); tau = tau or r.uniform(0.004, 0.009)
    lo = r.uniform(600, 2500); nb = nb or (lo, lo * r.uniform(3, 4.5))
    return bp(r.standard_normal(int(SR * d)), *nb) * dec(d, tau) + body * np.sin(2 * np.pi * f * t_(d)) * dec(d, tau * 2.5)


def _whoosh(r, d, lo, hi, pk, ka=1.5, kr=0.1):
    tt = t_(d); e = np.where(tt < pk, (tt / pk) ** ka, np.exp(-(tt - pk) / kr))
    nz = r.standard_normal(len(tt)); mix = np.clip(tt / d, 0, 1)
    return (bp(nz, lo, lo * 3) * (1 - mix) + bp(nz, hi / 3, hi) * mix) * e


def sfx(kind, p, seed):
    """One effect sized to its action. p: dict of params (dur, chars, n, dir, ...)."""
    r = np.random.default_rng(seed)
    g = lambda k, dflt: p.get(k, dflt)
    if kind in ("click", "pin", "tick"):
        x = _tick(r, d=0.07 if kind != "tick" else 0.05)
        return reverb(x, 0.08 if kind != "pin" else 0.15, 0.15)
    if kind == "type":                         # a typewriter line: one key per character over dur
        dur = g("dur", 1.0); n = int(min(g("chars", 20), 80))
        x = np.zeros(int(SR * (dur + 0.2))); times = np.linspace(0, dur, n) + r.uniform(-0.012, 0.012, n)
        for tm in np.clip(times, 0, dur):
            heavy = r.random() < 0.12
            place(x, _tick(r, tau=0.012 if heavy else None) * (1.0 if heavy else r.uniform(0.55, 0.9)), tm)
        return x
    if kind == "roll":                          # a counter / date roll: n ratchet clicks over dur, slowing down
        dur = g("dur", 0.6); n = int(g("n", 8))
        x = np.zeros(int(SR * (dur + 0.2)))
        for i in range(n): place(x, _tick(r, body=0.8) * (0.6 + 0.4 * i / max(1, n - 1)), dur * (i / max(1, n - 1)) ** 1.6)
        return x
    if kind == "flash":                         # camera: shutter clack, then a charge whine
        x = np.zeros(int(SR * 2.0)); place(x, _tick(r, 1400, 0.08, 0.008), 0); place(x, _tick(r, 800, 0.08, 0.01, (400, 4000)), 0.045)
        tt = t_(1.6); place(x, np.sin(2 * np.pi * np.cumsum(3000 + 5000 * (tt / 1.6) ** 0.7) / SR) * np.minimum(tt / 0.1, 1) * np.exp(-tt / 0.5) * 0.18, 0.12)
        return reverb(x, 0.15, 0.5)[: len(x)]
    if kind == "swish":                         # paper slides on, a tape, a polaroid
        d = g("dur", 0.34); return _whoosh(r, d, 800, 7000, d * 0.25, 1.5, d * 0.2)
    if kind == "whoosh":                        # a long paper move, a camera travel
        d = g("dur", 1.0); return fit(reverb(_whoosh(r, d, 300, 4000, d * 0.45, 2.0, d * 0.18), 0.2, 0.6), int(SR * d))
    if kind == "flip":                          # a page swings over
        d = g("dur", 0.45); return _whoosh(r, d, 600, 6000, d * 0.27, 1.2, 0.1) + 0.3 * _tick(r, 500, d, 0.02, (200, 2000))
    if kind == "whip":                          # a hard camera whip / layout swing
        d = g("dur", 1.4); tt = t_(d); up = g("dir", "down") == "up"
        f0, f1 = (300, 2600) if up else (2400, 300); f = f0 * (f1 / f0) ** np.clip(tt / 0.5, 0, 1)
        fm = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.3 * np.sin(2 * np.pi * 37 * tt))) / SR)
        e = np.minimum(tt / 0.02, 1) * np.exp(-tt / 0.22)
        return fit(reverb((0.6 * fm + 0.5 * bp(r.standard_normal(len(tt)), 1000, 8000)) * e, 0.3, 1.2), len(tt))
    if kind == "lights":                        # lights on: a switch ka-chunk + a low swell
        x = np.zeros(int(SR * 1.4)); place(x, _tick(r, 1100, 0.09, 0.01), 0); place(x, _tick(r, 700, 0.12, 0.014, (300, 3000), 0.9), 0.06)
        tt = t_(0.9); place(x, np.sin(2 * np.pi * 48 * tt) * np.sin(np.pi * tt / 0.9) ** 1.5 * 0.8, 0.0)
        return fit(reverb(x, 0.3, 1.2), len(x))
    if kind == "boom":                          # a new world arrives
        tt = t_(1.22); f = 62 * (1 + 0.8 * np.exp(-tt / 0.05))
        return np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.35)) * env(len(tt), 0.003, 0.2)
    if kind == "stamp":                         # rubber stamp / pinned card lands
        tt = t_(0.46)
        x = np.sin(2 * np.pi * 95 * tt) * np.exp(-tt / 0.05) + bp(r.standard_normal(len(tt)), 200, 2500) * np.exp(-tt / 0.03) * 0.8
        return fit(reverb(x, 0.12, 0.4), len(tt))
    if kind in ("slam", "impact"):              # a slam word, the title
        tt = t_(0.9)
        thump = np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(55 * (1 + 1.5 * np.exp(-tt / 0.03))) / SR) * np.exp(-tt / 0.25))
        ring = sum(np.sin(2 * np.pi * fr * tt) * a for fr, a in [(410, 1), (1130, 0.6), (2370, 0.3)]) * np.exp(-tt / 0.18) * 0.25
        crack = np.zeros_like(tt); nc = int(SR * 0.04); crack[:nc] = bp(r.standard_normal(nc), 1000, 9000) * np.linspace(1, 0, nc)
        x = thump + ring + 0.6 * crack
        if g("glitch", kind == "slam"): x = x + 0.5 * fit(sfx("glitch", {}, seed + 1), len(x))
        return fit(reverb(x, 0.25, 0.9), len(tt))
    if kind == "glitch":                        # RGB split, redaction flicker, a datamosh frame
        d = g("dur", 0.27); x = np.zeros(int(SR * d))
        for j in range(int(d / 0.035)):
            n = int(SR * 0.03)
            seg = np.sign(np.sin(2 * np.pi * r.uniform(150, 1800) * t_(0.03))) * 0.6 + r.standard_normal(n) * 0.4
            place(x, np.round(seg * 4) / 4, j * 0.035)
        return x
    if kind == "exit":                          # a scene leaves: sweep down
        d = g("dur", 0.75); tt = t_(d); f = 1800 * (60 / 1800) ** (tt / d)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + lp(r.standard_normal(len(tt)), 2500) * 0.5) * np.exp(-tt / (d * 0.4)) * np.minimum(tt / 0.01, 1)
    if kind == "beep":                          # a radio / broadcast beep
        x = np.zeros(int(SR * 0.53))
        for at in (0.0, 0.2): place(x, np.sin(2 * np.pi * 1320 * t_(0.12)) * env(int(SR * 0.12), 0.004, 0.01), at)
        return bp(x, 300, 3500)
    if kind == "rip":                           # torn paper
        d = g("dur", 0.42); tt = t_(d)
        grains = np.repeat(r.uniform(0.2, 1, int(d * 200) + 1), SR // 200)[: len(tt)]
        return bp(r.standard_normal(len(tt)), 900, 8000) * grains * np.sin(np.pi * tt / d) ** 0.5
    if kind == "string":                        # red string pulled taut between pins
        d = g("dur", 0.6); tt = t_(d)
        zip_ = bp(r.standard_normal(len(tt)), 1500, 6000) * (0.3 + 0.7 * (np.sin(2 * np.pi * 40 * tt) > 0))
        twang = np.sin(2 * np.pi * 180 * (t_(0.4))) * dec(0.4, 0.08)
        x = zip_ * np.sin(np.pi * tt / d) * 0.6; return place(np.concatenate([x, np.zeros(int(SR * 0.4))]), twang, d - 0.02)
    if kind == "marker":                        # a felt marker: circle, underline, arrow
        d = g("dur", 0.5); tt = t_(d)
        return bp(r.standard_normal(len(tt)), 1800, 5000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * tt))) * env(len(tt), 0.02, 0.06) * 0.6
    raise ValueError(f"unknown sfx kind {kind!r}")


SFX_KINDS = "click pin tick type roll flash swish whoosh flip whip lights boom stamp slam impact glitch exit beep rip string marker".split()
SFX_VOL = {"click": .3, "pin": .3, "tick": .16, "type": .25, "roll": .28, "flash": .3, "swish": .2, "whoosh": .28,
           "flip": .25, "whip": .28, "lights": .35, "boom": .2, "stamp": .3, "slam": .3, "impact": .25,
           "glitch": .25, "exit": .22, "beep": .18, "rip": .25, "string": .2, "marker": .12}
