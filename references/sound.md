# Sound

Every sound in the film is made in code for this film: no music library, no sample packs. `tools/cues.py` is
the score and the effects list, written against the script; `python3 tools/score.py` synthesises each layer and
each effect to fit (numpy, seeded, ~5–15 s) and writes the `<audio>` tags into index.html.
`python3 tools/mixcheck.py` estimates loudness before you render.

## Writing the cues

1. `python3 tools/score.py --words` lists every narrated word with its film time.
2. Write the score in `tools/cues.py` with `word("...")` so music follows the script, not fixed numbers.
3. Write one SFX cue per visible action, in scene-local time (the number in that scene's GSAP timeline).
4. `python3 tools/score.py --plan` prints the resolved timeline. `python3 tools/score.py` writes it.
Re-run `score.py` whenever the narration, a scene host or a cue moves; it regenerates everything.

## The score (one minor key, `KEY = "D"` by default; pick another if the narrator's pitch fights it)

| call | what it makes | where it goes |
|---|---|---|
| `hit(word(date) + 0.14, kind="hook")` | Ping Boom on the key's minor sixth: a 3 s reversed swell into a bell + sub boom | the date lands |
| `drone(0, end)` | root + fifth saws, a slow breathing filter, an airy "ooh" | under the whole film |
| `hit(word(name), kind="name")` | Ping Boom on the root | the NAME, the one hit of the story |
| `strings(word(name), word("But this") - 0.1)` | bowed minor melody over a cello line, stretched to the span | origin and rise; stops dead on the turn |
| `swell(word("But this"))` | choir "aah" crescendo peaking on the given time | into the turn, into the title |
| `pad(turn + 0.3, counterweight)` | slow supersaw chords i–♭VI–iv–v, ~8 s each | the case section |
| `riser(word(slam word))` | 3 s rise that peaks at its end | ends ON the report's slam word |
| `strings(question line, title, phrase=2)` | the second phrase | the open question |
| `hit(title time, kind="title")` | darker, longer Ping Boom | the title card |

**Silence before every hit is automatic:** each `hit(clear=True)` pulls every other layer to silence over the second
before it and brings them back over 2.5 s after. Hits closer than 3 s apart trigger a warning. Layers carry their
own fades; set `vol=` per layer when the mix needs it. Defaults: drone 0.3, strings 0.3, pad 0.35, swell 0.3,
hit 0.4, riser 0.25 (layers are rendered at −20 dBFS RMS; hits peak at −1 dBFS).

## Effects (each cue synthesised for its action, its own seed, loudest moment one frame after the picture)

| kind {params} | for | default vol |
|---|---|---|
| `click`, `pin`, `tick` | a small reveal, a pin, one strobe frame (tick each frame) | 0.3 / 0.3 / 0.16 |
| `type {chars, dur}` | a typewriter line: one key per character over the typing time | 0.25 |
| `roll {dur, n}` | a date or number counter | 0.28 |
| `flash` | a photo flashes on, a push into a photo | 0.3 |
| `swish {dur}`, `whoosh {dur}`, `flip {dur}` | paper slides on, a long paper/camera move, a page swings over | 0.2 / 0.28 / 0.25 |
| `whip {dur, dir}` | a camera whip, a layout swing | 0.28 |
| `lights` | the board's lights come on (the turn) | 0.35 |
| `boom` | a new world arrives | 0.2 |
| `stamp` | a rubber stamp, a pinned card | 0.3 |
| `slam {glitch}`, `impact` | a slam word (with a glitch on an RGB split), the title | 0.3 / 0.25 |
| `glitch {dur}` | redaction flicker, a broken frame | 0.25 |
| `exit {dur}` | a scene leaves, a dip | 0.22 |
| `beep`, `rip {dur}`, `string {dur}`, `marker {dur}` | a broadcast beep, torn paper, red string pulled taut, a felt-marker circle or underline | 0.18 / 0.25 / 0.2 / 0.12 |

Density: about 0.7 cues a second over the film (75 in 97 s). No sound for something that doesn't move, no whoosh on a
fade. The soundbite plays over the drone/pad only; leave its scene free of effects.

## Voice and mix

- Normalise the narration with headroom for the hits:
  `ffmpeg -i vo.wav -af "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.8" -ar 48000 assets/audio/vo_norm.wav`.
- `python3 tools/mixcheck.py` → integrated −14 to −16 LUFS, true peak below −1 dBTP. A test film measured voice
  −15 LUFS, music −22 LUFS (7 LU under the voice), whole mix −15.6 LUFS. If the peak is over, lower the hit `vol`.
- Never put a hit on a word the viewer must hear other than the name: it masks consonants. After the render,
  re-transcribe the MP4 and diff it against `vo_text.txt`; a word a hit masked shows up wrong.
- Measurements are not listening: play the mix in the Studio preview with the person before the render, and say
  plainly in REVIEW.md what was only measured.
