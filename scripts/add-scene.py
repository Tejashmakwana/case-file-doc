"""Add a scene to the film from a world template.
Run from the project root: python3 tools/add-scene.py <template> <scene-id> <start> <duration>
  e.g. python3 tools/add-scene.py board s5-board 35.3 14.5
Copies tools/scenes/<template>.html to compositions/<scene-id>.html with every id renamed from tpl-* to
<scene-id>-* (so no inner id can equal a host id), and hosts it in index.html one z-index below the scene
before it, so its exit reveals the next one. Templates: python3 tools/add-scene.py --list"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "scenes")
INFO = {
    "wall-date": "concrete wall: red date stamp + lime year bar, pinned polaroids, a page slides up and the camera dives in",
    "document": "a primary document under a 3D camera: depth of field, highlighter on the spoken words, red marker, source tape",
    "newsprint-origin": "grunge newsprint: the NAME (hard cut on the hit), facts on red/yellow bars, page flip, ring + label, typewriter",
    "newsprint-rise": "year slab, official logo wiped on in ink, footage + tape, face-matched strobe under a big line, word on a yellow bar",
    "board": "cork board in the dark: lights on, moving spotlight, photo comes alive, red string, magnifier, typed card, stamp",
    "report": "front-page spread: date stamp, masthead, redaction bars, the reported sentence word by word, RGB-split slam word",
    "clipping": "rolling date counter, a newsprint clipping dollied with two highlights and an underline, torn-paper exit",
    "consequence": "the real document card with drawn underlines, echo-slam word on a strip, cut to the portrait, boxed question",
    "soundbite": "a real clip with its own sound, speaker label, via line, typed quote captions",
    "question": "the counterweight typed on paper, footage, the whole board, the open question, the light closes",
    "title": "concrete title card: THE / NAME / NOUN on a red bar, ink circle and arrow, WHAT WE KNOW tape, sources line",
}

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "--list"):
    print(__doc__)
    for k, v in INFO.items(): print(f"  {k:17s} {v}")
    sys.exit(0)
if len(sys.argv) != 5:
    sys.exit("usage: add-scene.py <template> <scene-id> <start> <duration>")
tpl, sid, start, dur = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
src = os.path.join(TPL, tpl + ".html")
if not os.path.exists(src): sys.exit(f"no template {tpl!r}; one of: {', '.join(INFO)}")
if not re.fullmatch(r"[a-z][a-z0-9-]*", sid): sys.exit("scene-id: lowercase letters, digits and dashes, starting with a letter (e.g. s5-board)")
dst = os.path.join("compositions", sid + ".html")
if os.path.exists(dst): sys.exit(f"{dst} already exists")

html = open("index.html").read()
live = re.sub(r"<!--.*?-->", "", html, flags=re.S)  # the template's example host sits in a comment
if f'id="{sid}"' in live: sys.exit(f"index.html already hosts {sid}")
hosts = re.findall(r"<div[^>]*data-composition-src[^>]*>", live)

s = open(src).read()
s = s.replace('"tpl"', f'"{sid}"')
s = re.sub(r"(?<![\w-])tpl-", sid + "-", s)
os.makedirs("compositions", exist_ok=True)
open(dst, "w").write(s)

z = 30 - len(hosts)
track = len(hosts) + 1
host = (f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start}"'
        f' data-duration="{dur}" data-track-index="{track}" data-track-kind="graphics" data-width="1920" data-height="1080"'
        f' style="z-index: {z}"></div>\n')
anchor = '      <div id="grain"'
html = html.replace(anchor, host + anchor, 1)
open("index.html", "w").write(html)
print(f"{dst} from {tpl} at {start}s for {dur}s (z {z}). Retime its tweens to the narration and replace every ph_ file and placeholder line.")
