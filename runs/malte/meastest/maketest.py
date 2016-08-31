import galsim
import astropy
import megalut
import megalut.meas
import megalut.meas.aperphot
import os
import numpy as np

# We make a FITS image

a = np.zeros((100, 100))
a[30:36,40:46] = 10.0
a[70:75,80:85] = 10.0

#a += np.random.randn(a.size).reshape(a.shape)
astropy.io.fits.writeto("test.fits", a.transpose(), clobber=1)


# A catalog to describe the two sources (and one source out of the image:

x = [33.5, 73.0, -8]
y = [43.5, 83.0, -8]
tru_max_rad=[3.0, 2.5, 0.0]
cat = astropy.table.Table((x, y, tru_max_rad), names=["x", "y", "tru_max_rad"])
cat.meta["img"] = megalut.tools.imageinfo.ImageInfo("test.fits")
#print cat


# We can run a measurment on them:

#cat = megalut.meas.skystats.measfct(cat, stampsize=20)
cat = megalut.meas.galsim_adamom.measfct(cat, stampsize=20)
cat = megalut.meas.aperphot.measfct(cat, xname="x", yname="y", radii=[1, 2, 2.5, 2.51, 3, 3.01])

print cat
