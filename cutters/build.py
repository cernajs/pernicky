import json, numpy as np, trimesh, os
from shapely.geometry import Polygon
from shapely.ops import unary_union
OUT='/home/user/pernicky/cutters'; os.makedirs(OUT,exist_ok=True)
H_TARGET=130.0
d=json.load(open('outlines.json'))
svg_parts=[]
for name,pts in d.items():
    a=np.array(pts); a[:,1]*=-1
    p=Polygon(a).buffer(0).simplify(0.1)
    minx,miny,maxx,maxy=p.bounds
    s=H_TARGET/(maxy-miny)
    a=(np.array(p.exterior.coords)-[minx,miny])*s
    p=Polygon(a).buffer(0)
    p=p.buffer(0.5,join_style=1).buffer(-0.5,join_style=1)  # tiny smoothing
    def ring(o): return p.buffer(o,join_style=1,resolution=8).difference(p)
    def ex(poly,z0,z1):
        m=trimesh.creation.extrude_polygon(poly,z1-z0); m.apply_translation([0,0,z0]); return m
    parts=[ex(ring(5.0),0,2.0),      # grip rim on the print bed
           ex(ring(1.6),0,7.0),      # wall
           ex(ring(0.8),0,10.0)]     # thin cutting edge, 10 mm total
    m=trimesh.boolean.union(parts, engine='manifold')
    m.export(f'{OUT}/{name}_cutter.stl')
    b=p.bounds
    print(name, f'cookie {b[2]-b[0]:.1f} x {b[3]-b[1]:.1f} mm', 'watertight', m.is_watertight, len(m.faces))
    # SVG of the outline (mm)
    c=np.array(p.exterior.coords); c[:,1]=H_TARGET-c[:,1]
    dpath='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in c)+' Z'
    W=b[2]-b[0]
    open(f'{OUT}/{name}_outline.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.2f}mm" height="{H_TARGET}mm" viewBox="0 0 {W:.2f} {H_TARGET}"><path d="{dpath}" fill="#c33"/></svg>')
