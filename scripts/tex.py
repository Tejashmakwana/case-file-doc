"""Paper, newsprint and concrete grounds for the four worlds, made with numpy (seeded, no network).
usage: python3 tex.py <project>/assets/tex
Writes paper.png (beige document), newsprint.png (lighter, greyer), concrete.png (cool grey, lit from the left)."""
import sys, os, subprocess
import numpy as np

out = sys.argv[1] if len(sys.argv) > 1 else "assets/tex"
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(7)
W, H = 2048, 1152


def octave(w, h, cell):
    gw, gh = w // cell + 2, h // cell + 2
    g = rng.random((gh, gw)).astype(np.float32)
    ys = np.linspace(0, gh - 2, h, endpoint=False); xs = np.linspace(0, gw - 2, w, endpoint=False)
    y0 = ys.astype(int); x0 = xs.astype(int); fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def fbm(cells, weights):
    n = sum(w * octave(W, H, c) for c, w in zip(cells, weights))
    return (n - n.min()) / (n.max() - n.min())


def save(img, name):
    img = np.clip(img, 0, 255).astype(np.uint8)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                    "-i", "-", os.path.join(out, name)], input=img.tobytes(), check=True)


blot = fbm([512, 256, 128, 64], [0.4, 0.3, 0.2, 0.1]); fine = rng.random((H, W)).astype(np.float32)
fib = fbm([8, 4], [0.6, 0.4])
yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
vig = np.clip(1 - 0.22 * np.maximum(r - 0.55, 0) ** 1.4, 0, 1)
# paper: warm beige, blotchy stains, fine fibres, darker edges
shade = (0.90 + 0.10 * blot - 0.06 * np.clip((blot - 0.6) / 0.3, 0, 1) ** 2 + 0.025 * (fine - 0.5) + 0.03 * (fib - 0.5)) * vig
paper = np.array([226, 212, 184], np.float32)[None, None, :] * shade[..., None]; paper[..., 2] -= 10 * blot
save(paper, "paper.png")
# newsprint: lighter, greyer
news = np.array([232, 226, 212], np.float32)[None, None, :] * (0.93 + 0.06 * blot + 0.03 * (fine - 0.5))[..., None] * vig[..., None]
save(news, "newsprint.png")
# concrete: cool grey, pits, light from the left
cn = fbm([256, 96, 32, 12, 4], [0.3, 0.25, 0.2, 0.15, 0.1]); pits = (rng.random((H, W)) > 0.9985).astype(np.float32)
g = (112 + 62 * cn - 40 * pits) * (0.75 + 0.35 * (1 - xx / W))
save(np.stack([g * 0.97, g, g * 1.03], -1), "concrete.png")
print("wrote paper.png newsprint.png concrete.png ->", out)
