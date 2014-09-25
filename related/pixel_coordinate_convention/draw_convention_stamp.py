import galsim
import astropy
import os

gal = galsim.Gaussian(flux=1.0, sigma=3.0)
img = gal.draw()
img.write("tmp.fits")

# Of course, GalSim adds half a ton of WCS and reference pixel headers...
# So we remove all these, building just a minimal heaader
# We also shift the source by 1.0 pixel, to get different x and y.

img = astropy.io.fits.getdata("tmp.fits").transpose()

img[1:,:] = img[:-1,:]
img[0,:] = 0.0

#img[0,:] = 0.0
#img[-1,:] = 0.0
#img[:, 0] = 0.0
#img[:, -1] = 0.0

astropy.io.fits.writeto("convention_stamp.fits", img.transpose(), clobber=1)

os.remove("tmp.fits")


# In ds9 and in SExtractor, this galaxy is located at 9.5, 8.5

