"""Placeholder media so every scene template renders before the real material is in.
Run from the project root (new-doc.sh does): python3 tools/placeholders.py
Every file starts with ph_ and is labelled on screen; a render that still shows one is not finished.
  assets/photos/ph_portrait{,_bw,_sepia}.jpg  ph_person2_{bw,sepia}.jpg  ph_event{,_sepia}.jpg  ph_clipping_sepia.jpg
  assets/photos/ph_document.jpg (1206x1918, a primary document)   assets/strobe/ph_strobe_01..06.jpg
  assets/clips/ph_footage_bw.mp4  ph_keynote.mp4  ph_soundbite.mp4 (with a silent sound track)
  assets/logos/ph_mark.svg  ph_word.svg"""
import os, subprocess
import numpy as np

FONT = "assets/fonts/Anton-Regular.ttf"
rng = np.random.default_rng(3)
for d in ("assets/photos", "assets/strobe", "assets/clips", "assets/logos"):
    os.makedirs(d, exist_ok=True)


def ff(args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def silhouette(w, h, cx=0.5, cy=0.42, s=1.0, tone=(120, 124, 130)):
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    img = np.ones((h, w, 3)) * np.array(tone) * (0.75 + 0.35 * (1 - yy))[..., None]
    head = ((xx - cx) / (0.11 * s * h / w)) ** 2 + ((yy - cy) / (0.15 * s)) ** 2 < 1
    body = (((xx - cx) / (0.30 * s * h / w)) ** 2 + ((yy - (cy + 0.5 * s)) / (0.32 * s)) ** 2 < 1) & (yy > cy + 0.16 * s)
    img[head | body] = np.array(tone) * 0.32
    img += rng.normal(0, 6, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def save(img, path, label, look=None):
    h, w = img.shape[:2]
    vf = f"drawtext=fontfile={FONT}:text='{label}':fontcolor=white@0.85:fontsize={max(18, w // 22)}:x=(w-tw)/2:y=h-th-{h // 18}:box=1:boxcolor=black@0.45:boxborderw=10"
    if look == "bw": vf = "format=gray,eq=contrast=1.35," + vf
    if look == "sepia": vf = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131," + vf
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-i", "-",
                    "-vf", vf, "-frames:v", "1", "-q:v", "3", path], input=img.tobytes(), check=True)


P = "assets/photos/"
save(silhouette(1200, 1500), P + "ph_portrait.jpg", "SUBJECT PORTRAIT")
save(silhouette(1200, 1500), P + "ph_portrait_bw.jpg", "SUBJECT PORTRAIT", "bw")
save(silhouette(1200, 1500), P + "ph_portrait_sepia.jpg", "SUBJECT PORTRAIT", "sepia")
save(silhouette(1200, 1500, cx=0.48, cy=0.4, tone=(150, 140, 132)), P + "ph_person2_sepia.jpg", "SECOND PERSON", "sepia")
save(silhouette(1200, 1500, cx=0.48, cy=0.4, tone=(150, 140, 132)), P + "ph_person2_bw.jpg", "SECOND PERSON", "bw")
wide = np.maximum(silhouette(1800, 1200, cx=0.35, s=0.7), silhouette(1800, 1200, cx=0.68, cy=0.45, s=0.65))
save(wide, P + "ph_event.jpg", "EVENT PHOTO")
save(wide, P + "ph_event_sepia.jpg", "EVENT PHOTO", "sepia")
paper = np.ones((1100, 1650, 3)) * np.array([228, 222, 206]) + rng.normal(0, 5, (1100, 1650, 3))
for y in range(260, 1060, 34):
    for c in range(3):
        x0 = 60 + c * 530; paper[y:y + 12, x0:x0 + 480 - rng.integers(0, 120)] = 70
paper[60:220, 60:1590] = 30
save(np.clip(paper, 0, 255).astype(np.uint8), P + "ph_clipping_sepia.jpg", "NEWSPAPER CLIPPING", "sepia")
doc = np.ones((1918, 1206, 3)) * 246 + rng.normal(0, 3, (1918, 1206, 3))
for y in range(220, 1800, 53):
    doc[y:y + 16, 112:1040 - rng.integers(0, 300)] = 60
save(np.clip(doc, 0, 255).astype(np.uint8), P + "ph_document.jpg", "PRIMARY DOCUMENT")
for i in range(6):  # strobe: the face at the same spot and size in every frame
    save(silhouette(1920, 1080, cx=0.5, cy=0.4, s=0.9, tone=(60 + 30 * i, 70 + 18 * i, 90 + 10 * i)),
         f"assets/strobe/ph_strobe_{i + 1:02d}.jpg", f"STROBE FRAME {i + 1}")
save(silhouette(1920, 1080, cx=0.62, s=0.9), "scratch/ph_still.jpg", "PLACEHOLDER FOOTAGE")
C = "assets/clips/"
zoom = "scale=1920:1080,fps=30"
ff(["-loop", "1", "-i", "scratch/ph_still.jpg", "-t", "10", "-vf", f"{zoom},format=gray,format=yuv420p", "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", C + "ph_footage_bw.mp4"])
ff(["-loop", "1", "-i", "scratch/ph_still.jpg", "-t", "10", "-vf", f"{zoom},format=yuv420p", "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", C + "ph_keynote.mp4"])
ff(["-loop", "1", "-i", "scratch/ph_still.jpg", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "6",
    "-vf", f"{zoom},format=yuv420p", "-c:v", "libx264", "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", C + "ph_soundbite.mp4"])
open("assets/logos/ph_mark.svg", "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 368"><rect x="40" y="34" width="300" height="300" rx="40" fill="none" stroke="#141210" stroke-width="34"/><circle cx="190" cy="184" r="70" fill="#141210"/></svg>')
open("assets/logos/ph_word.svg", "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 368"><text x="425" y="206" font-family="Arial Black, Arial" font-weight="900" font-size="52" fill="#141210" text-anchor="middle">LOGO</text></svg>')
print("placeholders written (ph_*)")
