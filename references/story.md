# Story, script and voice

## The shape (a cold open, 60–120 s)

Thirteen beats. Keep the order; drop or merge beats for a shorter film, never the hook, the turn, the
counterweight or the question. Times are for a ~97 s film.

| # | beat | template | what the narrator does | the shape of the line | ~s |
|---|---|---|---|---|---|
| 1 | **the date** | wall-date | names the day it broke and who it is about, no name yet | "March third, 2026. The most <superlative> <role> in <field> sends <audience> a letter." | 0–7 |
| 2 | **their own words** | document | quotes the primary document exactly, highlighter on the quote | "'<quoted line>,' <he/she/they> write(s)." | 7–13 |
| 3 | **who they are** | newsprint-origin | the NAME (Ping Boom, hard cut) and 3–4 origin facts, one per line | "<Name> was born in <place>… <first job>… met <person> at <place>." | 13–24 |
| 4 | **the rise** | newsprint-rise | the year it started, the logo, how big it got, a strobe | "In <year>, <started what> in <where>. <Years> later, <how big>." | 24–35 |
| 5 | **the turn** | board (opens on black) | music cuts; lights on | "But this <season>, a different story surfaced." | 35 |
| 6 | **the other person / thing** | board | who, what they are linked to, what that is accused of; every claim hedged | "<Their name> is <name>. <Role> at <org>, under investigation for allegedly <claim>." | 35–49 |
| 7 | **the reporting** | report | outlet + date + the reported sentence, one slam word | "On <date>, <outlet> reported that <who> believes <claim>." | 49–57 |
| 8 | **the escalation** | clipping | the next report | "Two days later, according to <outlet>, <what happened>." | 57–64 |
| 9 | **the consequence** | consequence | what is now happening, in the subject's own document | "Now, <who> has opened <what>, into whether <question>." | 64–72 |
| 10 | **a real voice** | soundbite | someone with standing says one line, on camera | the clip itself | 72–76 |
| 11 | **the counterweight** | question (part 1) | what is NOT known or not proven, plainly | "There is no public evidence that <name> knowingly <did it>." | 76–81 |
| 12 | **the question** | question (part 2) | the one open question, as a question | "But for <who they are>, one question now hangs over everything. <Question>?" | 81–89 |
| 13 | **the title** | title | THE <NAME> <NOUN>, circled; sources line | (no narration; the title hit) | 89–97 |

Other storylines that fit the same worlds (offer them when the story isn't a scandal):
**The document, line by line** (the film never leaves one primary document; each line opens a window onto the
reporting behind it) · **Two timelines** (the subject's rise against the investigation's dates, colliding on one day).

## Writing the script

- About 150 spoken words a minute including pauses (215 words ≈ 85 s of voice at speed 0.95).
- Short declarative lines. One fact per line. Numbers and dates spelled as said ("twenty twenty-six").
- Pauses are written in: `<break time="0.4s"/>` between facts in a beat, 0.7–1.0 s between beats, **1.2 s before
  the name, before the turn and before the counterweight** (the silence is where the hits and the dip live).
- The name is withheld for the first beat and lands at the start of beat 3.
- Attribution in the sentence itself: "<outlet> reported that <who> believes…", "according to <outlet>",
  "allegedly". Never let a slam word stand without its source on screen.
- Quotes from documents are exact. Paraphrase is the narrator's, and says so.
- The counterweight is mandatory for any allegation. The ending is a question, not a verdict.
- No jokes about, and no judgement of, people who are not the subject (spouses, family, the other person).
- Write `vo_text.txt` (the exact text with break tags) and a `SCRIPT.md` table: line → scene → device → source row.

## Gate 1: show before you spend

Show the person: the script, the shot list (SPEC.md SHOTS), the SOURCES table with every FLAG, and the voice
pick. Wait for a go. No voice generation, downloads at scale, or scene building before it.

## Voice

- HeyGen `create_speech` (via the heygen MCP): pick from `list_voices`, audition 3–4 deep narrative voices on the
  first two lines and let the person choose by ear. Default: **"Wade – Resonant & Narrative"**
  `a3a4aa242aaf431ea8ec2c4b3bb332fa`, `withTimestamps: true`, `expressivenessBoost: 0.6`, language `en`.
  Other good fits: Sterling (cinematic), Garrettson. Credits are spent here, so this happens after gate 1.
- Wade (and every public voice) is an *instant* voice: `<break>` tags are refused, `speed` is ignored, and the
  pronunciation dictionary failed validation. Write `[pause]` between beats and punctuation inside them (`...` for a
  held beat). The result is too long to read inline: it lands in a tool-results file; keep its path.
- `python3 tools/vo_pauses.py <that file> --add "vanishes>The:0.5" "Vincenzo:0.4" ...` downloads the audio,
  lengthens the silences the story needs (before the name, the turn, the counterweight, the question), normalises
  with headroom for the hits, and writes `assets/audio/transcript.json` from HeyGen's own word times (exact; no
  transcription). Check names by ear-proxy with `npx hyperframes transcribe` on the result only if in doubt.
- `python3 tools/score.py --words` lists each word with its film time. A word said twice needs `n=`
  (`word("Leonardo", n=2)`); a phrase can pin it (`word("nineteen thirty")`).
- The voice is the clock. Every scene's tweens are keyed to these onsets; write them as comments.
- A soundbite gets a gap: split the VO into segments in `tools/cues.py` (`VO = [(0.8, 0, 70.9), (76.1, 71.75, 11.0)]`).
