#!/usr/bin/env bash
# Scaffold a case-file documentary project.
# usage: bash new-doc.sh <name> [duration_s=90] [parent_dir=~/hf-projects]
# Makes <parent>/<name>/ : a blank HyperFrames project + fonts, textures (paper/newsprint/concrete/cork/grain),
# the letterboxed index.html, tools/ (add-scene.py + the 11 world templates in tools/scenes, score.py which composes
# all music + SFX in code from tools/cues.py, mix check, baker, strobe picker, contact sheets), labelled ph_* placeholder
# media so templates render at once, and SPEC.md / SOURCES.md to fill in. No audio files are bundled.
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:?usage: new-doc.sh <name> [duration_s] [parent_dir]}"
DUR="${2:-90}"
PARENT="${3:-$HOME/hf-projects}"
DIR="$PARENT/$NAME"
[ -e "$DIR" ] && { echo "already exists: $DIR (pick another name, or work in it)"; exit 1; }

mkdir -p "$PARENT"
npx --yes hyperframes@latest init "$DIR" --skip-skills --non-interactive >/dev/null
cd "$DIR"
rm -f index.html
mkdir -p compositions tools scratch assets/{fonts,tex,audio,photos,clips,strobe,logos,img,vid}

cp "$SKILL"/assets/fonts/*.ttf assets/fonts/
cp "$SKILL"/assets/tex/grain.png assets/tex/
ffmpeg -v error -y -i "$SKILL"/assets/tex/cork.jpg assets/tex/cork.png
python3 "$SKILL"/scripts/tex.py assets/tex >/dev/null

sed "s/__DURATION__/$DUR/g" "$SKILL"/template/index.html > index.html
sed "s/__TITLE__/$NAME/g" "$SKILL"/template/SPEC.md > SPEC.md
cp "$SKILL"/template/SOURCES.md SOURCES.md
cp "$SKILL"/template/cues.py tools/cues.py
for f in score.py synthlib.py vo_pauses.py add-scene.py placeholders.py mixcheck.py bake.py strobe.py sheet.py sfxinfo.py; do cp "$SKILL/scripts/$f" tools/; done
cp -R "$SKILL"/template/scenes tools/scenes
python3 tools/placeholders.py >/dev/null

echo "ready: $DIR  (${DUR}s, 1920x1080, 2.39:1 letterbox)"
echo "next: research -> SOURCES.md, script + SPEC.md, then show the person before any voice or build"
