# The film's sound, written against its script. `python3 tools/score.py` composes every layer and effect in code
# to fit these cues and writes them into index.html. `python3 tools/score.py --words` lists each narrated word
# with its film time; `--plan` prints the resolved timeline without writing.

KEY = "D"                      # one minor key for every music layer
VO_SRC = "audio/vo_norm.wav"
TRANSCRIPT = "assets/audio/transcript.json"  # written by: npx hyperframes transcribe assets/audio/vo_norm.wav
# (film start, start inside the vo file, length). Split the take to open a gap for a soundbite.
VO = [
    (0.8, 0.0, 60.0),
]

# ---- the score, beat by beat (film time; word("...") = when the narrator says it) ----------------------
# hit(at, kind="hook" | "name" | "title")   Ping Boom: reversed swell -> bell + sub boom; clears the music before it
# drone(start, end)                          the bed under the whole film
# strings(start, end, phrase=1|2)            bowed minor melody, stretched to fit; ends (0.35 s fade) on the turn
# pad(start, end)                            minor chords under the case section, ~8 s each
# swell(peak)                                choir crescendo peaking at `peak` (into the turn, into the title)
# riser(end, dur=3)                          rises for 3 s and ends ON a slam word
# every layer takes vol=; the 1 s before each clearing hit is silent automatically. A word said twice: word("x", n=2).
#
# hit(word("<the date word>") + 0.14, kind="hook")      # the date lands
# drone(0, 86.9)
# hit(word("<the name>"), kind="name")               # the NAME, the one hit of the story
# strings(word("<the name>"), word("But this") - 0.1)     # origin and rise; stops dead on the turn ("But this ...")
# swell(word("But this"))
# pad(word("But this") + 0.3, word("<counterweight first words>"))    # the case
# riser(word("<slam word>"))                             # the report's slam word
# strings(word("<question line first words>"), 89.8, phrase=2)
# swell(89.8)
# hit(89.85, kind="title")

# ---- sound effects: (scene id, SCENE-LOCAL time of the picture event, kind[, {params}]) --------------------
# kinds: click pin tick type{chars,dur} roll{dur,n} flash swish{dur} whoosh{dur} flip{dur} whip{dur,dir}
#        lights boom stamp slam{glitch} impact glitch{dur} exit{dur} beep rip{dur} string{dur} marker{dur}
# every cue takes "vol" in its params. Use "film" as the scene id for film time.
SFX = [
    # ("s1-wall", 3.62, "flash"),                              # dimmed portrait flashes on
    # ("s1-wall", 4.0, "swish", {"dur": 0.5}),                 # polaroid slides in
    # ("s3-origin", 8.55, "type", {"chars": 23, "dur": 1.0}),  # a 23-character line types on in 1 s
    # ("s5-board", 3.3, "string", {"dur": 0.6}),               # red string to the next photo
    # ("s5-board", 8.15, "stamp"),                             # UNDER FEDERAL INVESTIGATION
    # ("s6-report", 6.0, "slam"),                              # the slam word
]
