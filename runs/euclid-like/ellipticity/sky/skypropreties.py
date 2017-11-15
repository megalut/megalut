import numpy as np
import scipy.stats as stats
import utils

def draw_magnitudes(size, mmin, mmax, slope=None, intercept=None):
    
    if slope is None:
        slope = 0.374248706584
    
    if intercept is None:
        intercept = -8.2493271124

    tmin = 10.**(slope*mmin+intercept)
    tmax = 10.**(slope*mmax+intercept)
    T = (tmax - tmin) / slope

    mags = np.array([])
    while (np.size(mags) < size):
        x = np.random.uniform(mmin, mmax, size)
        u = np.random.uniform(0, 1., size)

        p = (10.**(slope*x+intercept)) / slope / T
        m = x[p > u]
       
        mags = np.concatenate([mags, m])
        #print '...', np.size(mags)
    
    return mags[:size]

def get_size_params(magnitudes, slope_mean=None, intercept_mean=None, slope_width=None, intercept_width=None):

    if slope_mean is None:
        slope_mean = -0.108308701293
    
    if intercept_mean is None:
        intercept_mean = 2.07381404192
        
    if slope_width is None:
        slope_width = -0.0214786512765
    
    if intercept_width is None:
        intercept_width = 0.690127543846
        
    mean = slope_mean * magnitudes + intercept_mean
    width = slope_width * magnitudes + intercept_width
    
    return mean, width

def draw_halflightradius(magnitudes, a=-0.58, slope_mean=None, intercept_mean=None, slope_width=None, intercept_width=None, max_cutoff=4.5):
    
    locs, scales = get_size_params(magnitudes, slope_mean, intercept_mean, slope_width, intercept_width)
    
    rs = []
    
    for loc, scale in zip(locs, scales):
        rs.append(stats.skewnorm.rvs(a=a, loc=loc, scale=scale)) 

    rs = np.array(rs)

    return np.clip(10**(np.array(rs)), 0., max_cutoff)

def draw_ellipticities(size, e0=0.25, cutoff=0.9):
   
    e = stats.rayleigh.rvs(loc=0, scale=e0, size=size)
    
    e[e>cutoff] *= np.random.rand(np.size(e[e>cutoff])) * cutoff
    
    return e

def draw_sersicn(size, shape=None, loc=None, scale=None, bins=None, cutoff_min=0.3, cutoff_max=4.5):

    if shape is None:
        shape = 1.
        
    if loc is None:
        loc = 0. 
        
    if scale is None :
        scale = 1.2
    
    if bins is None:
        bins = np.sort(np.concatenate([np.linspace(cutoff_min, 3, 15), np.linspace(3.2, cutoff_max, 5)]))
        bins = bins[1:]    
    
    n = stats.lognorm.rvs(s=shape, loc=loc, scale=scale, size=size)
    
    n = n[n<cutoff_max]
    n = n[n>cutoff_min]
    
    n = bins[np.digitize(n, bins)]
    
    # Since we cut some of the index out, add more examples to get to size now
    while np.size(n) < size:
        n2n, _ = draw_sersicn(size-np.size(n), shape, loc, scale, bins, cutoff_min, cutoff_max)
        n = np.concatenate([n, n2n])

    return n, bins
    
def get_sky(zodical_mag, exposure, zeropoint, gain, pixel_scale=0.1):
    """
    :param zodical_mag: in mag/arcsec2
    """
    
    sky = utils.mag2flux(zodical_mag, exposuretime=exposure, gain=gain, zeropoint=zeropoint)
    
    sky *= pixel_scale * pixel_scale
    return sky


    