---
name: case-file-doc
description: >-
  Make a narrated investigative documentary cold open (a Netflix-style doc trailer, 60-120 s) on HyperFrames: a
  real story researched from real reporting (posts, outlets' pages, the subject's own letter or filing, real
  footage and one real soundbite), told by one deep narrator through four paper-and-evidence worlds: a concrete
  wall with a red date stamp, a document under a 3D camera with a highlighter swept on the spoken words, grunge
  newsprint kinetic type with red and yellow word bars, and a cork board in the dark with a moving spotlight, red
  string and a magnifier. 2.39:1 letterbox, grain, 11 ready scene templates, and a score and sound effects composed
  in code for each film from its script (a drone, strings, pad, choir swells, a Ping Boom on the name, every effect
  sized to its action). Every claim attributed. Use for "the Jensen doc style", "case file doc", "make a
  documentary about <person / company / news story>", "Netflix doc trailer", "investigative doc", "doc cold open
  from this post".
---

# Case File Doc

A real story, told like a case being opened: the date, their own words, who they are, how they rose, the turn,
the reporting, the open question, the title. Everything ships in this folder: the scene templates, the fonts and
grounds, and the code that composes the music and effects. No sound files, no reference footage.
Build to the `/hyperframes` contract (load it first if it isn't loaded).

**Read before building:** `references/story.md` (beats, script, voice) · `references/look.md` (worlds, tokens,
type, motion) · `references/devices.md` (every effect, which template holds it). Read `references/research.md`
before sourcing and `references/sound.md` before writing the cues.

## Hard rules

1. **Every claim traces to SOURCES.md.** On screen, every allegation carries its outlet and date, and the script
   says "reported", "believes", "allegedly", "according to". Quotes are exact. The film ends on a question,
   never a verdict, and includes the counterweight (what is not known or not proven).
2. **Real material only.** The actual document, post, article and footage. Leave out images tagged as AI-made,
   glamour or sexualised photos, deepfakes and face swaps. People who are not the subject (spouses, family, the
   other person) are shown factually and never mocked.
3. **Rights are the person's call.** News footage, press photos and other people's posts are FLAG in SOURCES.md;
   show the flags before the render.
4. **Sound is composed in code for this film** (`tools/score.py` from `tools/cues.py`). Never pull in music or
   sample libraries.
5. **Two gates.** Gate 1: script + shot list + SOURCES with flags + voice pick, before any voice credits or
   building. Gate 2: the Studio preview, before the render. Nothing is published or posted.
6. **A short film, not a slideshow.** No chapter cards. Not everything pops: calm fades, hard cuts, one device
   per line. One Ping Boom on the name with silence before it. Logos are the official mark wiped on in ink.
7. **Nothing placeholder ships.** Every `ph_` file and placeholder line in a template is replaced; a frame that
   still shows one is not done. Media treatments are baked with `tools/bake.py`, never CSS filters.
8. **Contract traps:** scale a wrapper, never the `<video>`; no CSS `transform` on an element GSAP also
   transforms; every `<audio>` has an id; all randomness seeded. `add-scene.py` keeps inner ids unique.

## Workflow

0. **Scaffold:** `bash <skill>/scripts/new-doc.sh <name> [seconds]` → `~/hf-projects/<name>/` with fonts, grounds
   (paper, newsprint, concrete, cork, grain), the letterboxed `index.html`, labelled `ph_` placeholder media,
   `SPEC.md`, `SOURCES.md` and `tools/` (add-scene, the 11 templates, score + synthlib, cues, mixcheck, bake,
   strobe, sheet, sfxinfo).
1. **Research** (research.md): the post or story the person gives, its primary document, the outlets' reports
   with dates, footage of the subject, one real voice. Fill SOURCES.md as you go.
2. **Script and spec** (story.md): `vo_text.txt` with break tags, `SPEC.md` (goal, shots with times, one device
   each, QA moments). → **Gate 1.**
3. **Voice:** HeyGen `create_speech` with `withTimestamps: true` (default "Wade – Resonant & Narrative"), then
   `python3 tools/vo_pauses.py <result.json> --add ...` (lengthens the story's silences, writes vo_norm.wav and an
   exact transcript), then `python3 tools/score.py --words`. story.md, Voice.
4. **Media:** originals into `assets/img`, `assets/vid`; baked into `assets/photos`, `assets/clips`; strobe frames
   into `assets/strobe`; official logo SVGs into `assets/logos`.
5. **Scenes:** `python3 tools/add-scene.py --list`, then one `add-scene.py <template> <scene-id> <start> <dur>` per
   beat (story.md maps beats to templates). In each scene: real text and media in, tweens retimed to the word
   onsets (comment each with its word and time), marker strokes moved onto the new words. Independent scenes can
   be built in parallel by subagents when each gets its SPEC row, the onsets, look.md and devices.md.
6. **Sound** (sound.md): write the score and the effect cues in `tools/cues.py` against the script, then
   `python3 tools/score.py` and `python3 tools/mixcheck.py`. Re-run score.py after any retiming.
7. **Check:** `npx hyperframes check` with 0 errors (known-OK warnings: nested media start basis, z −1 word bars,
   duplicate strobe images, low contrast while the wall dives into the page, a silent placeholder soundbite).
   `npx hyperframes snapshot --at <every QA second>` and look at every frame: dates on one line, highlights and
   strokes under the right words, nothing in the letterbox, no black scene, no `ph_` label left.
8. **Preview:** `npx hyperframes preview --background`, open it in the person's Chrome, listen together.
   → **Gate 2.**
9. **Render:** `npx hyperframes render -q delivery -o renders/<name>.mp4`; re-transcribe the render and diff it
   against `vo_text.txt`; write `REVIEW.md` (check result, loudness, claims attributed, what was only measured).

## Files

- `references/` story · look · devices · research · sound
- `scripts/` new-doc.sh · add-scene.py · score.py + synthlib.py (all music and SFX, numpy only) · placeholders.py
  · tex.py (grounds) · bake.py (bw / sepia / clean) · strobe.py (face-matched frames + sheet) · mixcheck.py ·
  sheet.py · sfxinfo.py
- `template/` index.html (letterbox, grain, AUDIO markers) · cues.py · SPEC.md · SOURCES.md · `scenes/` the 11
  world templates (wall-date, document, newsprint-origin, newsprint-rise, board, report, clipping, consequence,
  soundbite, question, title)
- `assets/` fonts (Anton, Old Standard TT, Special Elite, Permanent Marker, Courier Prime: OFL / Apache 2.0) ·
  tex (grain, cork)
