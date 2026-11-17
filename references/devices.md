# Devices

Every device below is working code in a scene template (`template/scenes/<name>.html`, copied into each project
as `tools/scenes/`; the template is named in each heading) unless marked BORROWED.
`python3 tools/add-scene.py <template> <scene-id> <start> <duration>` puts one in the film with unique ids. Then
replace every placeholder line and `ph_` file with the real material and retime the tweens to the narration's
word onsets (`python3 tools/score.py --words`), writing the word and onset above each tween
(`// "<the company>" 2.28 — the mark wipes on`). Marker strokes (underlines, rings, arrows) are drawn in fixed
coordinates: after replacing text, snapshot and move them onto the new words. One device carries each line; the
rest of the frame holds still or drifts.

Shared snippets used throughout:

```js
// draw-on stroke: give the SVG path pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="110"
tl.to("#ring", { strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut" }, t);
// typewriter: one step per character
tl.fromTo("#line", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 1.25, ease: "steps(27)" }, t);
// bar behind a word: .bar{position:absolute;inset:6px 0 2px 0;z-index:-1;transform-origin:0 50%} inside a
// position:relative inline-block wrapper; the LINE gets isolation:isolate so the bar never drops behind footage
tl.fromTo("#bar", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, t);
// roughened print edge on display type
// <filter id="xx-rough"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="9"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter>
```

## The wall (wall-date, title)

**Date stamp.** The hook. Anton 300 px red `#c8102e` letters (`<span>` each, text-shadow `0 5px 0 rgba(20,8,8,.55)`)
fade on one by one, stagger 0.06 s, on the spoken date; a lime `#c9d400` bar wipes under it (scaleX, 0.35 s
power3.out) and the year lands on it in ink. Concrete ground, radial shade, slow camera pull 1.12 → 1.0 over 5.4 s.
The first Ping Boom hit lands on the date (sound.md).

**Pinned polaroid, flashed on.** `#f3efe6` frame, padding `18px 18px 64px`, a red pin (radial-gradient ball),
a Permanent Marker caption. The portrait waits dimmed (black layer at 0.55) and snaps to full in 0.12 s with a
camera-flash SFX on "the most powerful man in…". A second polaroid slides in x −90 → 0, rotation −9 → −6.

**Object becomes the world** (transition). A paper slides up onto the wall (y 520 → 0, expo.out 0.7 s), then the
camera dives into it (scale 3.4, power3.in 1.15 s) and the scene fades in its last 0.18 s over the next scene,
which is the same paper, full frame.

## The document (document, clipping, consequence)

**Document dolly.** A 2000×1500 paper (`paper.png` or newsprint) inside a `perspective: 1900px` stage; the camera
is the paper's transform: start `rotationX 24, rotationZ −4, scale 1.55`, travel along the line being read
(`x` tweens of 2–2.4 s power1/2.inOut), end flatter (`rotationX 7, scale 0.9`) to reveal the page. Depth of field:
two full-width `backdrop-filter: blur(9px)` bands top and bottom with gradient masks, so only the read line is
sharp. Text: Old Standard TT 46 px / 74 px line height, real wording, exactly as published. Lines the camera
never reads sit blurred under the bands and the letterbox: give each of them `data-layout-ignore` (they are
texture), or `check` fails them on contrast and reading time. The read lines stay checked.

**Highlighter sweep, timed to the voice.** `.hl { background-image: linear-gradient(#f2d300,#f2d300);
background-repeat:no-repeat; background-position:0 70%; background-size:0% 62%; mix-blend-mode:multiply }`;
tween `backgroundSize` to `100% 62%` over exactly the span the narrator reads it (1.0–1.6 s, power1.inOut).
Then a red marker underline or arrow draws on (draw-on, 0.4–0.5 s) at the end of the phrase.

**Source tape.** Every document and clip carries its source: black `#151412` tape, Special Elite 30–38 px cream,
`OUTLET · MONTH D, YYYY`, slides in x −60 → 0 (expo.out 0.45 s), types on with steps(n). In the letterbox safe
area (top ≥ 160 px or bottom ≤ 900 px).

**Rolling date counter.** `MAR 1<br>MAR 2<br>MAR 3` in an `overflow:hidden` box one line tall; tween `y` by two
line heights (0.6 s power3.inOut) on "two days later". Use it for any passage of time.

**Torn-paper exit.** Clip the scene root with a jagged polygon edge and sweep it across (0.3 s power3.in):
seeded jag array (LCG), `polygon(100% 0%, X+jag[i]% (i/30*100)%, …, 100% 100%)` from X=−12 to X=116 (clipping).

**Real document, real underline.** The actual screenshot (a letter, a filing) as a tall card, slow scale 0.92 →
1.12 over 3.4 s; red `#ff2a3d` underlines drawn on the quoted lines in the image's own coordinates (SVG with the
image's viewBox, `preserveAspectRatio="none"`).

## Newsprint (newsprint-origin, newsprint-rise, report)

**Grunge kinetic type.** Newsprint ground with a 6-column ghost text layer (Old Standard 15 px at 15% ink,
`data-layout-ignore`) of the real background facts. Anton 200–255 px ink with the rough filter for the name and
the big words; 96–100 px for the line under it, one word on a red bar (white text) or a yellow bar (ink text):
`BORN IN [PLACE]`, `MOVED AWAY AT [11]`. Lines fade on (0.3–0.35 s); bars wipe 0.1–0.25 s after the word.
The NAME hard-cuts on with the Ping Boom; no fade.

**Page flip.** The next layout swings in like a page turned onto the stack: `rotationY −96 → 0`,
`transformOrigin "0% 50%"`, 0.5 s power3.out, inside a `perspective: 2200px` stage, `backface-visibility:hidden`,
shadow `-30px 0 60px rgba(0,0,0,.45)`.

**Double-print word.** `FIRST JOB` in ink, then a red copy on top wipes on left to right (clip-path, 0.55 s).

**Circle, arrow, marker label.** On a photo of the person named: a hand-drawn red ring (draw-on 0.55 s), an arrow
(0.35 s), and a Permanent Marker label rotated −4° (`the person, named`) wiping on with clip-path.

**Year slab + logo in ink.** A 500 px year (`1999`) drifting x −40 over 4 s; the company's OFFICIAL logo, split
into mark and wordmark SVGs, wiped on with `clip-path inset(0 100% 0 0) → 0` 0.6 s each, `mix-blend-mode: multiply`
so it prints into the paper. Never a rotated coloured box.

**Report spread (report).** The strongest reporting beat, laid out like a front page: a date stamp (red Anton
150 px + lime year bar), a masthead in Old Standard Bold with letter-spacing 6 px and a typed dateline, then the
reported sentence word by word (pop, below), ending in a red Anton 230 px SLAM word. Beside it: the footage in a
black frame on a rotated yellow block, a credit line under it, and 5 black redaction bars that flick on line by
line (`steps(2)` 0.08 s, stagger 0.09) and flicker again on the slam.

**RGB-split slam.** The slam word gets `filter:url(#rgb)`: feColorMatrix splits R and GB, each through an
`feOffset` with an id; on the hit, tween their `dx` with keyframes over 0.24 s:
`{ keyframes: { attr: [{dx:26},{dx:-8},{dx:16},{dx:0}] } }` (R) and `[-18,10,-6,0]` (GB). The word itself is a
`tl.set` (hard on), with impact + glitch SFX.

**Echo slam.** Two blurred 35% ghosts of a word converge from y −150 and +150 (0.35 s power3.in), vanish, and the
real word sets hard in the same frame (`INDEPENDENT` / `INVESTIGATION`, consequence), on a newsprint strip that
slid up from below (y 420 → 0, expo.out).

**Word pop** (blur 6 → 0, 0.13 s). For a reported sentence built word by word on the onsets. Use it on ONE
sentence per scene at most; a film where everything pops reads as a slideshow.

## Footage and stills (newsprint-rise, soundbite, question)

**Face-matched strobe.** 8–12 keynote frames with the face at the same spot and size (`tools/strobe.py`),
6 frames (0.2 s) each, a 1.0 → 1.03 push per frame, a click on each (rotate click_1/2/4), under a big line
(`THE FASTEST GROWING NAME IN ITS FIELD`) with a red box wiping behind the key words. Each strobe image is a
`.clip` div with its own data-start/duration.

**Footage beat.** Baked clip, full frame, inside a wrapper you scale (1.0 → 1.06–1.1 over the clip, ease none);
a bottom scrim; white Anton lines on it; one word on a yellow bar. Scale the wrapper, never the `<video>`.

**Soundbite.** A real person saying it (the clip keeps its sound: `data-has-audio="true"`, data-volume ~2 to sit
with the narrator), a cream source label `PERSON · DATE`, `via OUTLET`, and the quote typed below in boxed
Special Elite 50 px captions, one clip per phrase. Open a gap in the narration for it (split the VO in cues.py).

**Rack-focus in** (BORROWED, editor-v1 `focus_in`). A new still or clip opens at `filter: blur(8px)` and sharpens
over 9 frames (0.3 s, power2.out). Use on the first frame of a footage beat after a dip.

**Counter in irregular steps** (BORROWED, doc-ad-style). For a number the narrator says (a market cap, a
sentence length): `tl.set(el, {textContent})` through 6–8 uneven values every 2–3 frames (e.g. 997 → 2,329 →
3,661 → 4,000), the final value holds, a click on each step.

## The board (board, question)

**Cork board in the dark, moving spotlight.** Cork ground under one camera div (`#cam`, transform-origin centre)
with sepia polaroids, a sepia newspaper clipping, an index card, pins and red string (`#b3121f`, 5 px, draw-on
per string). Light = two oversized layers over everything, driven by CSS variables:

```css
.light { position:absolute; left:-400px; top:-400px; width:2720px; height:1880px; --sx:770px; --sy:666px; --sr:300px; pointer-events:none; }
#dark { background: radial-gradient(circle var(--sr) at var(--sx) var(--sy), rgba(8,6,3,0) 0%, rgba(8,6,3,0) 76%, rgba(8,6,3,.94) 100%); }
#warm { background: radial-gradient(circle var(--sr) at var(--sx) var(--sy), rgba(255,196,120,.30) 0%, rgba(255,196,120,.10) 60%, rgba(255,196,120,0) 78%); mix-blend-mode: overlay; }
```
Move camera and light TOGETHER (same start, duration, ease): `tl.to(C, {x,y,scale})` + `tl.to(".light",
{"--sx":…, "--sy":…, "--sr":…})`, 0.5–0.7 s power2/3.inOut, following a string from one face to the next.
Mark `#dark` `data-layout-allow-occlusion`.

**Lights on.** The scene opens on black that fades out in 0.25 s with a long click + sub tone: the turn ("But this
fall…"), after the previous scene dipped to black and the music cut.

**Photo comes alive.** Push into one polaroid (scale up, power2.in 0.5 s) and fade its footage in full frame
(0.18 s) with a `REPORTED FOOTAGE` tape; 1.5 s later, cut back to the board.

**Magnifier.** A 260 px ring (12 px `#cfd2d6` border, inset highlight) with a wooden handle, holding the same photo
offset and enlarged (`img` at ~1.65×, negative left/top), slides in (x/y 60 → 0, 0.7 s) over the face being named;
a marker alias label `(alias)` wipes on beside it.

**Rubber stamp.** Red 7 px bordered Anton `UNDER FEDERAL<br>INVESTIGATION`, rotation −8°, `mix-blend-mode:
multiply`, lands from scale 1.08 in 0.1 s with impact_2; fades to 0.35 when the camera moves on.

**Index card typed.** Ruled card (repeating-linear-gradient blue lines every 49 px), Anton title, Special Elite
lines typed with steps(n chars), the key phrase then highlighted.

**The open question.** Wide board, every string leading to the subject; camera eases out (1.2 → 0.93, 3.6 s); the
light settles on him; the question in Permanent Marker types on; a red ring draws around his photo on the
question's last word; the light closes (`--sr` → 420, 0.7 s power2.in) and the frame goes black (0.3 s).

## The counterweight (question)

**Typed on blank paper.** After the accusations, the facts that cut the other way, centred, Special Elite 56 px
typed with steps(n), one key word underlined in red: `There is no public evidence / that the subject [knowingly] did
what is alleged.` Paper ground, a 3.5% creep, nothing else on screen. Never skip this beat when the story
is an allegation.

## The title (title)

**Circled end card.** Concrete wall, a newsprint strip along the bottom. `THE` (Anton 64, tracking 10) /
`NAME` (Anton 210, rough) / `NOUN` (Anton 190 cream on a red bar that wipes on). A pen-filter ink circle draws
around it (0.6 s), an arrow points in, a black `WHAT WE KNOW` tape types on, the month, an orange rule, and the
sources line in Special Elite 28 px on the strip. The final Ping Boom/impact lands as the name shows.

## Transitions between scenes

Allowed: object-becomes-world dive · page flip · torn paper · whip (camera x −3200, 0.45 s power3.in, with a
cyber swipe) · dip to black 0.2–0.55 s (before the turn and before a soundbite) · hard cut on a hit.
**1–2 frame negative** (BORROWED, editor-v1/doc-ad): a full invert flash at most twice per film, on the hardest
turn. **Stretch slam** (BORROWED, doc-ad-style): one word as a 2-frame clone at `scaleY 4.4` with a vertical blur
(`feGaussianBlur stdDeviation="0 18"`), then it sets at hero size; at most once.
Not allowed: chapter cards, crossfades between unrelated worlds, anything easing in after it has landed.
