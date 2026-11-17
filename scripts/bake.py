"""Bake the film's treatments into media with ffmpeg. Never grade media with CSS filters.
usage:
  python3 bake.py photo <in> <out.jpg> --look bw|sepia|clean [--w 1600]
  python3 bake.py clip  <in> <out.mp4> --look bw|sepia|clean [--ss 12.5 --t 4]
Looks:
  bw    newsprint world: greyscale, contrast 1.35, slight crush, fine grain
  sepia cork-board world: warm sepia, lifted blacks, soft grain
  clean keynote / footage that should stay in colour: mild contrast, no grade
Clips come out 1920x1080 (cover-cropped), 30 fps CFR, keyframe every second, no audio unless --keep-audio."""
import argparse, subprocess

LOOK = {
    "bw": "format=gray,eq=contrast=1.35:brightness=-0.02,noise=alls=9:allf=t,format=yuv420p",
    "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.12:brightness=0.01:gamma=0.95,noise=alls=6:allf=t,format=yuv420p",
    "clean": "eq=contrast=1.06:saturation=0.92,format=yuv420p",
}
COVER = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"

p = argparse.ArgumentParser()
p.add_argument("kind", choices=["photo", "clip"])
p.add_argument("src"); p.add_argument("dst")
p.add_argument("--look", default="bw", choices=LOOK)
p.add_argument("--w", type=int, default=1600, help="photo width (height keeps aspect)")
p.add_argument("--ss", type=float); p.add_argument("--t", type=float)
p.add_argument("--keep-audio", action="store_true")
a = p.parse_args()

if a.kind == "photo":
    vf = f"scale={a.w}:-2," + LOOK[a.look].replace(":allf=t", "")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vf", vf, "-frames:v", "1", "-q:v", "3", a.dst]
else:
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if a.ss is not None: cmd += ["-ss", str(a.ss)]
    cmd += ["-i", a.src]
    if a.t is not None: cmd += ["-t", str(a.t)]
    cmd += ["-vf", f"{COVER},fps=30,{LOOK[a.look]}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-g", "30", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "192k"] if a.keep_audio else ["-an"]
    cmd += [a.dst]
subprocess.run(cmd, check=True)
print("baked", a.look, "->", a.dst)
