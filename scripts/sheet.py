"""Contact sheet of a video with timestamps. usage: sheet.py in.mp4 out.jpg N cols [start end [thumb_w]]"""
import subprocess, sys, json
# usage: sheet.py in.mp4 out.jpg N cols [start end]
f, out, n, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
d = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).decode())
s = float(sys.argv[5]) if len(sys.argv)>5 else 0; e = float(sys.argv[6]) if len(sys.argv)>6 else d
fps = n/(e-s)
W = int(sys.argv[7]) if len(sys.argv)>7 else 240
vf = f"fps={fps},scale={W}:-2,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='%{{pts\\:hms}}':fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6:x=3:y=3,tile={cols}x{(n+cols-1)//cols}"
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(s),'-to',str(e),'-copyts','-i',f,'-vf',vf,'-frames:v','1',out])
