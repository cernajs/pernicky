import numpy as np
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon
def smooth_outline(p, step=0.25, sigma_mm=1.5):
    """Resample the closed outline evenly and Gaussian-smooth it along its length."""
    r=p.exterior
    n=int(r.length/step)
    pts=np.array([r.interpolate(i*r.length/n).coords[0] for i in range(n)])
    sig=sigma_mm/step
    pts=np.c_[gaussian_filter1d(pts[:,0],sig,mode='wrap'),gaussian_filter1d(pts[:,1],sig,mode='wrap')]
    return Polygon(pts).buffer(0).simplify(0.02)
