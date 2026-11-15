from PIL import Image, ImageFilter
import numpy as np, potrace, sys
S=__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/'
thr=int(sys.argv[1]); col=sys.argv[2]
g=Image.open(S+'home/topo-background.png').convert('L'); k=3
up=g.resize((g.width*k,g.height*k),Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.0))
a=np.array(up)>thr
path=potrace.Bitmap(~a).trace(turdsize=20, alphamax=1.2, opticurve=True, opttolerance=0.3)
W,H=g.width*k,g.height*k; parts=[]
for c in path:
    sp=c.start_point; d=[f"M{sp.x:.1f},{sp.y:.1f}"]
    for s in c.segments:
        d.append(f"L{s.c.x:.1f},{s.c.y:.1f}L{s.end_point.x:.1f},{s.end_point.y:.1f}" if s.is_corner else f"C{s.c1.x:.1f},{s.c1.y:.1f} {s.c2.x:.1f},{s.c2.y:.1f} {s.end_point.x:.1f},{s.end_point.y:.1f}")
    parts.append(''.join(d)+'Z')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#000"/><path fill="{col}" fill-rule="evenodd" d="{"".join(parts)}"/></svg>'
open(S+'topo/topo.svg','w').write(svg); print(len(svg), len(path))
