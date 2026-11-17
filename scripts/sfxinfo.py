"""Measure SFX files: duration, onset, peak, tail, brightness, low-end share, envelope sketch. usage: sfxinfo.py files..."""
import sys, subprocess, numpy as np, glob, os
for f in sys.argv[1:]:
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.int16).astype(np.float32)/32768
    if len(x)==0: continue
    n=320; e=np.array([np.sqrt((x[i:i+n]**2).mean()) for i in range(0,len(x)-n,n)])+1e-9
    pk=int(e.argmax()); d=len(x)/16000
    db=20*np.log10(e/e.max())
    on=next(i for i,v in enumerate(db) if v>-20)*0.02
    tail=len(db)-next(i for i,v in enumerate(db[::-1]) if v>-30)
    sp=np.abs(np.fft.rfft(x)); fq=np.fft.rfftfreq(len(x),1/16000); cen=(sp*fq).sum()/sp.sum()
    lo=(sp[fq<150]**2).sum()/(sp**2).sum()
    # envelope sketch: 10 buckets
    b=[int(max(0,min(9,(v+40)/4))) for v in np.interp(np.linspace(0,len(db)-1,16),range(len(db)),db)]
    print(f"{os.path.basename(f)[:26]:26s} d={d:5.2f} on={on:4.2f} pk={pk*0.02:4.2f} end={tail*0.02:5.2f} cen={cen:5.0f}Hz low={lo:.2f} env={''.join(str(v) for v in b)}")
