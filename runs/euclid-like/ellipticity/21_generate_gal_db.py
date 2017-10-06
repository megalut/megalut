from sky import skypropreties as sky
import megalut
from astropy.table import Table, Column
import astropy.units as u
import config
import numpy as np
import os

import logging
logger = logging.getLogger(__name__)

simdir = config.simdir


import pylab as plt
###################################################################################################

def contracted_rayleigh(sigma, max_val, p, size=1):
    """
    A distribution with finite support.
    """
    tmp = np.random.rayleigh(sigma, size=size)
    return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))

###################################################################################################


whichset = 'train'
distrib = "uniform"

# How many galaxies?
n_gal = 1e6

# What distribution
name_distrib = "{}_{}".format(distrib, whichset)

n_gal = int(n_gal)

if not os.path.exists(config.dbdir):
    os.mkdir(config.dbdir)

outfname = os.path.join(config.dbdir, "{}.fits".format(name_distrib))
if os.path.exists(outfname):
    raise IOError("This file already exists: {}".format(outfname))
galdb = Table()

if distrib == "euclid":
    
    # Ellipticities
    gs = sky.draw_ellipticities(size=n_gal)
    theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0, size=n_gal)
    (g1s, g2s) = (gs * np.cos(2.0 * theta), gs * np.sin(2.0 * theta))
    
    g1s = np.clip(g1s, -0.9, 0.9)
    g2s = np.clip(g2s, -0.9, 0.9)
    
    # Profile
    sersicn, _ = sky.draw_sersicn(size=n_gal)
    
    # mag
    mags = sky.draw_magnitudes(size=n_gal, mmin=20, mmax=24)    
    flux = 10**(-0.4 * (mags - config.zeropoint)) * config.exposuretime / np.abs(config.gain)

    # Size
    rad = sky.draw_halflightradius(mags)
    
    # Computing surface brightness
    sb = mags / ((rad * 2.)**2. * np.pi)

elif distrib == "default":
    
    gs = contracted_rayleigh(0.2, 0.6, 4, size=n_gal) # there is no shear, so let's make it a bit broader
    
    theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0, size=n_gal)        
    (g1s, g2s) = (gs * np.cos(2.0 * theta), gs * np.sin(2.0 * theta))
    
    sersicn = np.random.choice(np.concatenate([np.linspace(0.3, 4, 10), np.linspace(0.3, 2, 10)]), size=n_gal)
    surface_brigthness = np.random.uniform(0.8, 1.2, size=n_gal)
    
    rad = np.random.uniform(1.0, 2., size=n_gal)
    flux = np.pi * rad * rad * 10**(-surface_brigthness) * 1e4

    mags = -1. * np.ones_like(rad)

elif distrib == "uniform":
    
    # Ellipticities
    gs = sky.draw_ellipticities(size=n_gal)
    theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0, size=n_gal)
    (g1s, g2s) = (gs * np.cos(2.0 * theta), gs * np.sin(2.0 * theta))
    
    g1s = np.clip(g1s, -0.9, 0.9)
    g2s = np.clip(g2s, -0.9, 0.9)
    
    # Profile
    sersicn = np.random.choice(np.concatenate([np.linspace(0.3, 4, 10), np.linspace(0.3, 2, 10)]), size=n_gal)
    
    # mag
    mags = np.random.uniform(20.0, 24., size=n_gal)
    flux = 10**(-0.4 * (mags - config.zeropoint)) * config.exposuretime / np.abs(config.gain)

    # Size
    rad = np.random.uniform(0.1, 1.9, size=n_gal)
    
    # Computing surface brightness
    sb = mags / ((rad * 2.)**2. * np.pi)

else:
    
    raise NotImplemented()

# Populate the table    
galdb['g'] = Column(gs)
galdb['theta'] = Column(theta, unit=u.radian)
galdb['g1'] = Column(g1s)
galdb['g2'] = Column(g2s)
galdb['sersicn'] = Column(sersicn)
galdb['mag'] = Column(mags, u.ABmag)
galdb['flux'] = Column(flux, u.adu)
galdb['rad'] = Column(rad, u.arcsecond)
galdb['surface_brigthness'] = Column(sb)

sourcefluxes = flux * np.abs(config.gain)
skynoisefluxes = config.gain *sky.get_sky(zodical_mag=config.skylevel, exposure=config.exposuretime, zeropoint=config.zeropoint, gain=np.abs(config.gain), pixel_scale=config.pixelscale)
skynoisefluxes *= skynoisefluxes
areas = np.pi * (rad * 2.) ** 2

noises = np.sqrt(sourcefluxes + areas * skynoisefluxes)
galdb['snr_calc'] = Column(sourcefluxes / noises)

galdb.write(outfname)



