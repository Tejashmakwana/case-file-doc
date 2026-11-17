"""Compose this film's music and sound effects in code, from its script and cue sheet, and write them into
index.html between <!-- AUDIO:BEGIN --> and <!-- AUDIO:END -->.
Run from the project root:
  python3 tools/score.py            # synthesise everything for tools/cues.py and write the audio block
  python3 tools/score.py --words    # print every narrated word with its FILM time (to write cues)
  python3 tools/score.py --plan     # resolve the cue sheet and print the timeline, write nothing

How it fits the film:
- Music layers are rendered to exactly the span they cover (strings stretch their phrases, the pad changes chord
  about every 8 s inside its span), in the film's KEY, with fades baked in.
- word("Reyes") turns a spoken word into film time (transcript + VO placement), so hits follow the script.
- Every hit(clear=True) empties the music before it: other layers fall silent over the 1 s before the hit and
  come back over 2.5 s after it.
- Each SFX cue is synthesised for that cue (a typewriter line gets one key per character, a whoosh lasts as long as
  the camera move) with its own seed, so no two cues sound identical. Its loudest moment is placed one frame after
  the picture event."""
import json, os, re, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import synthlib as S

FPS = 30
html_path = "index.html"
html = open(html_path).read()
live = re.sub(r"<!--.*?-->", "", html, flags=re.S)


def attrs(tag): return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


HOSTS = {"film": 0.0}
for tag_ in re.findall(r"<div[^>]*data-composition-src[^>]*>", live):
    a = attrs(tag_); HOSTS[a["data-composition-id"]] = float(a["data-start"])
TOTAL = float(attrs(re.search(r'<div[^>]*data-composition-id="main"[^>]*>', html).group(0))["data-duration"])

# ---------------------------------------------------------------- the cue-sheet language
MUSIC, _ns = [], {}


def _words():
    path = _ns.get("TRANSCRIPT", "assets/audio/transcript.json")
    if not os.path.exists(path):
        sys.exit(f"no transcript at {path}: run `npx hyperframes transcribe assets/audio/vo_norm.wav` first")
    words = json.load(open(path))
    words = words.get("words", words) if isinstance(words, dict) else words
    out = []
    for w in words:
        txt = re.sub(r"[^\w']", "", w["text"].lower())
        if not txt: continue
        for st, ms, du in _ns["VO"]:          # vo-file time -> film time
            if ms <= w["start"] < ms + du:
                out.append((txt, st + w["start"] - ms, w["text"])); break
    return out


def word(text, n=1, nudge=0.0):
    """film time where the n-th occurrence of `text` (one or more words) starts being said."""
    want = [re.sub(r"[^\w']", "", x.lower()) for x in text.split()]
    ws = _words(); hits = 0
    for i in range(len(ws) - len(want) + 1):
        if [w[0] for w in ws[i:i + len(want)]] == want:
            hits += 1
            if hits == n: return round(ws[i][1] + nudge, 3)
    import difflib
    near = difflib.get_close_matches(want[0], sorted({w[0] for w in ws}), n=4, cutoff=0.5)
    hint = ", ".join(f'"{x}" at {next(t for w, t, _ in ws if w == x):.2f}s' for x in near) or "nothing close"
    sys.exit(f'word("{text}", n={n}) is not in the transcript (found {hits}). Closest: {hint}. Names are often misheard: '
             f'use the word as transcribed, or correct its "text" in the transcript file (keep the times).')


def drone(start, end, vol=0.3, fi=1.2, fo=3.0):
    MUSIC.append(dict(type="drone", start=start, end=end, vol=vol, fi=fi, fo=fo))


def strings(start, end, phrase=1, vol=0.3, fi=1.5, fo=0.35):
    MUSIC.append(dict(type="strings", start=start, end=end, phrase=phrase, vol=vol, fi=fi, fo=fo))


def pad(start, end, vol=0.35, fi=1.2, fo=0.8):
    MUSIC.append(dict(type="pad", start=start, end=end, vol=vol, fi=fi, fo=fo))


def swell(peak, vol=0.3):
    MUSIC.append(dict(type="swell", start=peak - 5.3, end=peak + 4.7, at=peak, vol=vol, fi=0, fo=0))


def hit(at, kind="name", vol=0.4, clear=True):
    MUSIC.append(dict(type="hit", kind=kind, start=at - 3.0, end=at + 8.0, at=at, vol=vol, clear=clear, fi=0, fo=1.5))


def riser(end, dur=3.0, vol=0.25):
    MUSIC.append(dict(type="riser", start=end - dur, end=end + 0.05, at=end, vol=vol, fi=0, fo=0))


_ns.update(word=word, drone=drone, strings=strings, pad=pad, swell=swell, hit=hit, riser=riser)

if "--words" in sys.argv:  # only VO and TRANSCRIPT are needed; the rest of cues.py may not be written yet
    src = open("tools/cues.py").read()
    for m in re.finditer(r"^(VO|TRANSCRIPT)\s*=\s*(\[.*?\]|\".*?\")\s*$", src, re.M | re.S):
        _ns[m.group(1)] = eval(m.group(2))
    for txt, t, raw in _words(): print(f"{t:8.2f}  {raw}")
    sys.exit()

exec(open("tools/cues.py").read(), _ns)
S.set_key(_ns.get("KEY", "D"))
VO_SRC, VO, SFX = _ns["VO_SRC"], _ns["VO"], _ns.get("SFX", [])

# ---------------------------------------------------------------- resolve + render
hits = sorted(m["at"] for m in MUSIC if m["type"] == "hit" and m["clear"])


def clear_gain(t):
    """film-time gain for non-hit layers: silent just before every clearing hit, back over 2.5 s."""
    g = np.ones_like(t)
    for h in hits:
        g = np.minimum(g, np.interp(t, [h - 1.0, h - 0.35, h, h + 2.5], [1, 0, 0, 1], left=1, right=1))
    return g


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1 if x.ndim == 1 else 2); w.setsampwidth(2); w.setframerate(S.SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def tag(id_, src, start, dur, vol, track):
    return (f'      <audio id="{id_}" class="clip" src="assets/{src}" data-start="{start:.3f}" data-duration="{dur:.3f}"'
            f' data-volume="{vol}" data-track-index="{track}"></audio>')


plan = "--plan" in sys.argv
for m in sorted(MUSIC, key=lambda m: m["start"]):
    print(f"  {m['type']:8s} {max(0, m['start']):7.2f} -> {min(TOTAL, m['end']):7.2f}" + (f"  hit at {m['at']:.2f}" if "at" in m else ""))
for i, h in enumerate(hits[1:]):
    if h - hits[i] < 3.0: print(f"  warning: hits at {hits[i]:.2f} and {h:.2f} are under 3 s apart; the second one won't land on silence")
missing = sorted({c[0] for c in SFX if c[0] not in HOSTS})
if missing: sys.exit(f"SFX name scenes not hosted in index.html: {missing} (hosts: {sorted(HOSTS)})")
bad = sorted({c[2] for c in SFX if c[2] not in S.SFX_KINDS})
if bad: sys.exit(f"unknown SFX kinds {bad}; use one of: {' '.join(S.SFX_KINDS)}")
print(f"  {len(SFX)} sfx cues, key {_ns.get('KEY', 'D')} minor")
if plan: sys.exit()

md, sd = "assets/audio/score", "assets/sfx/gen"
for d in (md, sd):
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".wav"): os.remove(os.path.join(d, f))

lines = ["      <!-- voice: the clock of the film -->"]
for i, (st, ms, du) in enumerate(VO):
    a = f'      <audio id="vo-{i + 1}" class="clip" src="assets/{VO_SRC}" data-start="{st:.3f}" data-duration="{du:.3f}"'
    lines.append(a + (f' data-media-start="{ms}"' if ms else "") + ' data-volume="1" data-track-index="20"></audio>')

lines.append(f"      <!-- music: composed by tools/score.py in {_ns.get('KEY', 'D')} minor -->")
for i, m in enumerate(sorted(MUSIC, key=lambda m: m["start"])):
    seed = 100 + i; length = m["end"] - m["start"]
    if m["type"] == "drone": x = S.drone(length, seed)
    elif m["type"] == "strings": x = S.strings(length, m["phrase"], seed)
    elif m["type"] == "pad": x = S.pad(length, seed)
    elif m["type"] == "swell": x = S.swell(seed)
    elif m["type"] == "hit": x = S.hit(m["kind"], seed)
    else: x = S.riser(m["at"] - m["start"], seed)
    x = S.fit(x, int(S.SR * length))
    if x.ndim == 1: x = np.stack([x, x], 1)
    n = len(x); tt = np.arange(n) / S.SR
    fade = np.ones(n)
    if m["fi"]: fade *= np.clip(tt / m["fi"], 0, 1) ** 2
    if m["fo"]: fade *= np.clip((length - tt) / m["fo"], 0, 1) ** 2
    if m["type"] != "hit": fade *= clear_gain(m["start"] + tt)
    x = x * fade[:, None]
    start = m["start"]
    if start < 0: x = x[int(-start * S.SR):]; start = 0.0
    x = x[: int((TOTAL - start) * S.SR)]
    name = f"{i:02d}_{m['type']}" + (f"_{m['kind']}" if m["type"] == "hit" else "") + ".wav"
    write(os.path.join(md, name), x)
    lines.append(tag(f"mus-{i:02d}-{m['type']}", f"audio/score/{name}", start, len(x) / S.SR, m["vol"], 21 + i))

lines.append("      <!-- sound effects: synthesised per cue, loudest moment one frame after the picture -->")
for i, cue in enumerate(SFX):
    sc, t, kind = cue[:3]; p = dict(cue[3]) if len(cue) > 3 else {}
    x = S.norm(S.sfx(kind, p, seed=1000 + i))
    env_ = np.abs(x); w = int(S.SR * 0.01)
    pk = int(np.argmax([env_[j:j + w].max() for j in range(0, max(1, len(x) - w), w)])) * 0.01
    start = HOSTS[sc] + t + 1 / FPS - pk
    if start < 0: x = x[int(-start * S.SR):]; start = 0.0
    x = x[: max(1, int((TOTAL - start) * S.SR))]
    name = f"{i:03d}_{sc}_{kind}.wav"
    write(os.path.join(sd, name), x)
    lines.append(tag(f"sfx-{i:03d}", f"sfx/gen/{name}", start, len(x) / S.SR, p.get("vol", S.SFX_VOL[kind]), 40 + i % 14))

begin, end = "<!-- AUDIO:BEGIN -->", "      <!-- AUDIO:END -->"
a = html.index(begin) + len(begin); b = html.index(end)
open(html_path, "w").write(html[:a] + "\n" + "\n".join(lines) + "\n" + html[b:])
print(f"wrote {len(MUSIC)} music layers -> {md}, {len(SFX)} sfx -> {sd}, {len(VO)} vo segments -> index.html")
