"""Estimate the film's loudness without rendering: mix every <audio> in index.html plus every
<video data-has-audio="true"> inside the scenes (soundbites), then measure with ebur128.
Run from the project root: python3 tools/mixcheck.py [out.wav]
Targets before render: integrated -14 to -16 LUFS, true peak below -1 dBTP, voice always on top."""
import os, re, subprocess, sys

html = open("index.html").read()
live = re.sub(r"<!--.*?-->", "", html, flags=re.S)


def attrs(tag):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


root = attrs(re.search(r'<div[^>]*data-composition-id="main"[^>]*>', html).group(0))
total = float(root["data-duration"])
items = [attrs(t) for t in re.findall(r"<audio [^>]*>", live)]
# soundbites: videos that keep their own sound inside a scene
for host in re.findall(r"<div[^>]*data-composition-src[^>]*>", live):
    h = attrs(host)
    path = h["data-composition-src"]
    if not os.path.exists(path):
        continue
    for v in re.findall(r"<video [^>]*>", open(path).read()):
        a = attrs(v)
        if a.get("data-has-audio") == "true":
            a["data-start"] = str(float(h["data-start"]) + float(a.get("data-start", 0)))
            items.append(a)

inputs, filt = [], []
for i, a in enumerate(items):
    st = float(a.get("data-start", 0)); du = float(a.get("data-duration", 30)); ms = float(a.get("data-media-start", 0))
    v = float(a.get("data-volume", 1)); fi = float(a.get("data-fade-in", 0)); fo = float(a.get("data-fade-out", 0))
    inputs += ["-i", a["src"]]
    f = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={ms}:{ms + du},asetpts=PTS-STARTPTS,volume={v}"
    if fi: f += f",afade=t=in:st=0:d={fi}"
    if fo: f += f",afade=t=out:st={max(0, du - fo)}:d={fo}"
    f += f",adelay={int(st * 1000)}|{int(st * 1000)}[a{i}]"
    filt.append(f)
filt.append("".join(f"[a{i}]" for i in range(len(items))) + f"amix=inputs={len(items)}:normalize=0:duration=longest,atrim=0:{total}[out]")
out = sys.argv[1] if len(sys.argv) > 1 else "scratch/mixcheck.wav"
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", out], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print(f"{len(items)} sources mixed -> {out}")
print("\n".join(l for l in r.split("Summary:")[-1].splitlines() if "I:" in l or "Peak:" in l or "LRA:" in l))
pk = re.findall(r"Peak:\s+(-?[\d.]+)", r)
if pk and float(pk[-1]) > -1.0:  # name the moments so the fix is a volume, not a guess
    import wave, numpy as np
    w = wave.open(out); x = np.abs(np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768)
    a = x.reshape(-1, w.getnchannels()).max(1); sr = w.getframerate(); seen = []
    for i in np.argsort(a)[::-1]:
        if all(abs(i / sr - t) > 0.5 for t in seen): seen.append(i / sr)
        if len(seen) == 3: break
    near = lambda t: [it.get("id") for it in items if float(it.get("data-start", 0)) <= t <= float(it.get("data-start", 0)) + float(it.get("data-duration", 0))]
    for t in seen: print(f"  over -1 dBTP near {t:.2f}s: {', '.join(i for i in near(t) if i)}  -> lower the hit/sfx vol there")
