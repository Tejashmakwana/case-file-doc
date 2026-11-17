"""Turn a HeyGen create_speech result into the film's narration: exact word times, longer pauses where the
story needs silence, loudness with headroom for the hits.
Run from the project root:
  python3 tools/vo_pauses.py <create_speech result .json> [--add "vanishes>The:0.5" "Vincenzo:0.4" ...]
Each --add puts extra silence BEFORE a word: "Word:secs", "prev>Word:secs" (the word that follows prev) or
"Word#2:secs" (its second occurrence). Instant voices ignore <break> tags and speed, and `[pause]` gives only
~0.3-0.6 s, so the 1.2 s silences before the name, the turn and the counterweight are made here.
Writes assets/audio/vo_raw.wav (if missing), vo_norm.wav and transcript.json (HeyGen's own word times, shifted;
no transcription needed). Then: python3 tools/score.py --words."""
import json, os, subprocess, sys, urllib.request, wave
import numpy as np

if len(sys.argv) < 2: sys.exit(__doc__)
res = json.load(open(sys.argv[1]))
adds = sys.argv[sys.argv.index("--add") + 1:] if "--add" in sys.argv else []
raw = "assets/audio/vo_raw.wav"
if not os.path.exists(raw):
    open(raw, "wb").write(urllib.request.urlopen(res["audio_url"]).read())
ws = [w for w in res["original_words"] if w["text"].strip("[]").lower() != "pause"]
SR = 48000
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
norm = lambda t: t.strip(".,?!:;\"'").lower()


def find(spec):
    prev, n = None, 1
    if ">" in spec: prev, spec = spec.split(">", 1)
    if "#" in spec: spec, k = spec.split("#"); n = int(k)
    hits = 0
    for i, w in enumerate(ws):
        if norm(w["text"]) == spec.lower() and (prev is None or (i and norm(ws[i - 1]["text"]) == prev.lower())):
            hits += 1
            if hits == n: return i
    sys.exit(f"--add: no word {spec!r}" + (f" after {prev!r}" if prev else "") + f" (occurrence {n})")


ins = sorted((find(a.rsplit(":", 1)[0]), float(a.rsplit(":", 1)[1])) for a in adds)
parts, prev, shift = [], 0, np.zeros(len(ws))
for i, add in ins:
    cut = int((ws[i - 1]["end_time"] + ws[i]["start_time"]) / 2 * SR) if i else 0
    parts += [x[prev:cut], np.zeros(int(add * SR), np.float32)]; prev = cut; shift[i:] += add
parts.append(x[prev:]); y = np.concatenate(parts)
os.makedirs("scratch", exist_ok=True)
with wave.open("scratch/vo_edit.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "scratch/vo_edit.wav", "-af", "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.8",
                "-ar", str(SR), "assets/audio/vo_norm.wav"], check=True)
tr = [{"id": f"w{i}", "text": w["text"], "start": round(w["start_time"] + shift[i], 3), "end": round(w["end_time"] + shift[i], 3)}
      for i, w in enumerate(ws)]
json.dump(tr, open("assets/audio/transcript.json", "w"), indent=0)
print(f"{len(tr)} words, {len(ins)} pauses lengthened, narration {len(y) / SR:.2f}s -> assets/audio/vo_norm.wav + transcript.json")
print(f"set VO = [(0.8, 0.0, {len(y) / SR:.2f})] in tools/cues.py")
