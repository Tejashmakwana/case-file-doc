# Look

Four physical worlds that read as one investigation: the case file on a wall, the document under a camera, the
newspaper that tells the story, the board in the dark.

## Frame

- 1920×1080, 30 fps, **2.39:1 letterbox**: black bars 138 px top and bottom at z 90 in index.html. Picture lives
  between y 138 and 942; keep text and faces inside y 160–900.
- Film grain over everything: `assets/tex/grain.png`, overlay blend, opacity 0.18, jumped to a seeded position
  every 2 frames (template index.html). `data-motion-blur="on"` on the root.
- Scenes overlap their neighbours by 0.1–0.4 s and sit one z-index below the previous scene, so each exit reveals
  the next one underneath.

## Worlds

| world | ground | light | media treatment | used for |
|---|---|---|---|---|
| wall | `concrete.png`, radial shade to 55% black at the edges | flat, cool | portraits clean or bw in polaroids | the date hook, the title |
| document | `paper.png` (letters) or `newsprint.png` (clippings) on a 3D plane; dark `#1a1714` behind | soft, DOF bands | the real screenshot | primary documents, reports |
| newsprint | `newsprint.png` + 6-column ghost text at 15% | flat | `bw` (greyscale, contrast 1.35, grain) | who they are, the rise, report spreads |
| board | `cork.png` under a 94%-dark vignette with a warm spotlight | one moving spot | `sepia` | the other people, the links, the question |
| footage | full-frame baked clip, bottom scrim | as shot | `bw` for news, `clean` for keynotes | the rise, soundbites |

## Tokens

```
ink        #141210   (text on paper; soft ink #1d1a16 / #26221c)
paper      #e2d4b8   newsprint #e8e2d4   card #f4efe2   polaroid #efe9dc–#f6f2ea
concrete   #46484c (#2c2e31 behind)      board dark rgba(8,6,3,.94)   doc backdrop #1a1714
red        #c8102e   (ONE hit word per shot; marker strokes; stamps; string #b3121f; bright marker #e8102a/#ff2a3d on dark)
yellow     #f2d300   (highlighter, multiply, ~62% of line height; yellow word bars)
lime       #c9d400   (the year bar under a date stamp only)
orange     #e8701a   (one rule on the title card)
tape       #151412 with cream #efe7d6 text
```

## Type (bundled in assets/fonts)

| role | font | size |
|---|---|---|
| display, names, slams, dates | Anton | 150–500 px, tracking −1% (−2 to −6 px), line height 0.9 |
| documents, mastheads, ghost columns | Old Standard TT (Regular/Bold/Italic) | 46–70 px documents, 15 px columns |
| typewriter, source tapes, captions on clips | Special Elite | 28–56 px |
| hand labels on photos, the question | Permanent Marker | 30–76 px |
| spare mono | Courier Prime | |

Each scene declares its own `@font-face` with `src: url("assets/fonts/<file>.ttf")`.

## Motion

- Arrivals: expo.out / power2.out 0.45–0.7 s. Slams: hard `tl.set` or 0.1–0.13 s. Exits: power3.in 0.25–0.45 s.
- Camera: every scene has one slow camera (scale 1.0 → 1.035–1.1, or a pull 1.12 → 1.0) for its whole length.
  Camera moves between subjects 0.5–0.7 s power2/3.inOut.
- Highlighter and typewriter durations equal the narrator's reading of those words.
- Something changes every 0.5–1.5 s (a word, a highlight, a camera move, a string). A still hold longer than 2 s
  is a mistake unless a line is typing or the camera is travelling.
- Titles and words land and stop. Nothing drifts or breathes after it has landed except the scene camera.
- Animate transforms, opacity, clip-path, background-size, CSS variables and SVG attrs. Never top/left/width/height.

## Banned

Chapter cards between beats · pop-in on every element · a dark void with floating cards · glow, particles, lens
flares · purple/neon gradients · a coloured box rotated behind a logo · CSS filters on photos or clips (bake
them) · AI-generated or glamour photos · on-screen claims without a source tag · a docked channel logo.
