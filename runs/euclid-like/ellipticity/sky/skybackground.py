import astropy
import astropy.units as u
import astropy.constants as c
import astropy.io.fits as fits
import astropy.table.table as Tab
import numpy as np
import pylab as plt
import utils

# Source of the data: http://euclid2017.london/slides/Monday/Session3/SurveyStatus-Scaramella.pdf [Euclid Consortium meeting slides]

x1 = 0.648 # um
lny1 = np.log10(700)

x2 = 1.805 # um
lny2 = np.log10(100)
# Units of the zodical backgroun nW/m2/um/sr
# y = exp(ax + b)

a = (lny2 - lny1) / (x2 - x1)
b = lny1 - a * x1

# Integrate on VIS-like (assumes a step function for the transmittance
lambda_in = 5500. * u.AA
lambda_out = 9000. * u.AA

wv = np.arange(0.55, 0.9005, 0.0005) * u.um

nu = c.c / wv 
nu = (nu).decompose().to(u.Hz)

# Computes the expected Zodical background at a fct of wavelenghts
# units of zodical_bckgr = nJ/s/m2/um/sr
yy = np.array(wv)
zodical_bckgr = 10**(a * yy + b) * u.nW / u.m / u.m/ u.um / u.sr
zodical_bckgr = zodical_bckgr.to(u.W / u.m / u.m/ u.m / u.sr)

# units of zodical_bckgr_nu = nJ/s/nu/m2/sr
zodical_bckgr_nu = (((yy * u.um).to(u.m))**2 / c.c * zodical_bckgr)

zodical_bckgr_ABmag = utils.ABmag(nu , zodical_bckgr_nu)
print "Estimated zodical background for Euclid %1.3f ABmag / arcsec^2" % zodical_bckgr_ABmag

