# Research and media

The film is only as good as its evidence. Find the primary document, the reporting (outlet + date), real
footage of the subject, and one real voice. Write everything into `SOURCES.md` as you go.

## Where to look (in order)

1. **The story's own thread on X** (the person usually hands you a post). Open it in the person's Chrome with the
   claude-in-chrome extension (they're logged in; X blocks logged-out reading). Read the post, the quote posts and
   replies for: screenshots of the primary document, outlets' own posts with their headline images, news clips.
2. **The outlets' own posts and pages**: FT, NYT, Reuters, Bloomberg, the local press where it happened. Paywalled
   articles: use the outlet's X post / headline card and the parts quoted by other outlets; never invent the body.
   Recreate a clipping (s7-nyt) only with the outlet's exact published sentence, and label it with outlet · date.
3. **The subject's own words**: letters, filings, statements, posts. The real screenshot beats a recreation.
4. **Footage of the subject**: their keynotes / interviews on their own YouTube channel (yt-dlp
   `--download-sections "*12:30-12:45" --force-keyframes-at-cuts`), news footage of the event (FLAG).
5. **Logos**: the official mark as SVG (Wikimedia Commons, the company's press kit). Split mark and wordmark into
   two SVGs for the ink wipe.

## Chrome extension tricks (paid for once)

- `javascript_tool` output is cut off near 1000 characters. Write the result into the page instead
  (`document.body.innerHTML = '<main><article><pre>' + JSON.stringify(data) + '</pre></article></main>'`) and read
  it back with `get_page_text`.
- Collect media URLs from the DOM (`img[src*="pbs.twimg.com/media"]`), then fetch the original size with
  `?format=jpg&name=orig` via curl. Post text and media also come from `https://api.fxtwitter.com/<user>/status/<id>`.
- X video: `yt-dlp "https://x.com/<user>/status/<id>"` (or the fxtwitter `videos[].url`).
- Wikimedia Commons answers 429 to quick parallel downloads: fetch one file at a time with a short sleep and
  retry on 429, with a User-Agent. Its API gives licence, date and author per file (`prop=imageinfo&iiprop=
  url|size|extmetadata&iiurlwidth=2400`); write them into SOURCES.md.
- Make a contact sheet of everything collected (`tools/sheet.py` for clips, an ffmpeg tile for stills) and LOOK
  before choosing. `file *.jpg` after downloads: redirects and bot walls save HTML as .jpg.

## What to keep out

- **AI-generated images.** On X they're often tagged ("AI合成", "AI generated", a community note, a Grok/Imagine
  watermark). Leave them out even when they're the most viral picture of the story.
- Glamour, sexualised or paparazzi-style photos of the people involved; photos of private family members beyond a
  public, captioned event photo used once.
- Deepfakes, face swaps, meme edits of real people.
- Anything you cannot trace to who published it first.

## SOURCES.md discipline

- Every script line with a fact gets a claims row. A serious allegation needs the outlet named on screen and,
  where possible, a second outlet that reports the same.
- Every media file gets a row: URL, account, date, licence/use, status OK / FLAG / OUT. News footage, press photos
  and other people's posts are FLAG (commentary use); the person decides before the render.
- Dates are the publication dates, written the way they go on screen (`NOV 6, 2026`).

## Prep

Raw downloads go in `assets/img/` and `assets/vid/`; only baked files enter scenes:
`python3 tools/bake.py photo assets/img/x.jpg assets/photos/x_sepia.jpg --look sepia` (board),
`--look bw` (newsprint and report spreads), `clean` for keynote colour and logos' photos.
Clips: `python3 tools/bake.py clip assets/vid/x.mp4 assets/clips/x_bw.mp4 --look bw --ss 12.5 --t 4`
(a soundbite keeps its sound with `--keep-audio`). Strobe frames: `python3 tools/strobe.py assets/strobe/cand
assets/vid/keynote1.mp4 assets/vid/keynote2.mp4`, then copy the 8–12 that match into `assets/strobe/`.
Hard-link large media shared between projects (`ln`) rather than copying it.
