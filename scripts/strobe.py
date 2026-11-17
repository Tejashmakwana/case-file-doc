"""Candidate frames for a shape-matched strobe: every frame shows the same face at the same place
and size, so a 6-frame-per-image burst reads as one person flickering through time.
usage: python3 strobe.py <outdir> <video> [<video> ...] [--every 1.5] [--face-w 150] [--no-face]
Writes <outdir>/NN_<src>_<t>.jpg (1920x1080, face centre at 960,430) and <outdir>/_sheet.jpg.
Face detection fails on wide stage shots: then pick tight frames by hand with --no-face (plain
cover-cropped frames) and keep only the ones whose head sits in the same spot. LOOK at the sheet
and hand-pick 8-12; never use the whole set blind."""
import argparse, os, subprocess
import cv2, numpy as np

p = argparse.ArgumentParser()
p.add_argument("outdir"); p.add_argument("videos", nargs="+")
p.add_argument("--every", type=float, default=1.5)
p.add_argument("--face-w", type=float, default=150.0)
p.add_argument("--no-face", action="store_true")
a = p.parse_args()
os.makedirs(a.outdir, exist_ok=True)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
k = 0
for src in a.videos:
    cap = cv2.VideoCapture(src)
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)
    t = 0.0
    while t < dur:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, fr = cap.read(); t += a.every
        if not ok:
            continue
        if a.no_face:
            h, w = fr.shape[:2]; s = max(1920 / w, 1080 / h)
            img = cv2.resize(fr, (int(w * s + 0.5), int(h * s + 0.5)))
            y0 = (img.shape[0] - 1080) // 2; x0 = (img.shape[1] - 1920) // 2
            img = img[y0:y0 + 1080, x0:x0 + 1920]
        else:
            fs = casc.detectMultiScale(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY), 1.1, 6, minSize=(55, 55))
            if len(fs) != 1:
                continue
            x, y, w, h = fs[0]
            s = min(a.face_w / w, 2.6)
            M = np.float32([[s, 0, 960 - (x + w / 2) * s], [0, s, 430 - (y + h / 2) * s]])
            img = cv2.warpAffine(fr, M, (1920, 1080), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
            if (img.max(axis=2) < 6).mean() > 0.10:  # the crop left the frame
                continue
        name = os.path.splitext(os.path.basename(src))[0][:12]
        cv2.imwrite(os.path.join(a.outdir, f"{k:02d}_{name}_{t - a.every:.1f}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        k += 1
print("candidates", k)
if k:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(a.outdir, "[0-9]*.jpg"),
                    "-vf", f"scale=320:-2,tile=6x{(k + 5) // 6}", "-frames:v", "1", os.path.join(a.outdir, "_sheet.jpg")])
    print("look at", os.path.join(a.outdir, "_sheet.jpg"))
