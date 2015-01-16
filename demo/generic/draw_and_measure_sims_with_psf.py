"""
Another demo about drawing simulated galaxies.
This time we use PSFs provided in psfs/
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import megalut
import megalut.sim
import megalut.meas

import numpy as np
import astropy

############################################################################################
# Note that all this is an illustration of the low-level functions.
# To draw and measure sims in real life, have a look at the much shorter "run" demos.
############################################################################################



# As before, we first set the desired distributions of parameters:

class Flux600(megalut.sim.params.Params):
	def get_flux(self):
		return 600.0
mysimparams = Flux600()

# And we prepare a catalog of 20 x 20 simulated galaxies:

galcat = megalut.sim.stampgrid.drawcat(mysimparams, n=20, stampsize=48)

print galcat[:5]


# Now, we prepare the PSF stuff. We'll use existing PSF stamps.
# We need an image with PSF stamps, and we need to add new columns in galcat.
# To specify the image, we will add an ImageInfo object to catalog.

# This PSF image comes with a catalog, which is not in form of an ImageInfo object.
# (After all, that's what we want to demo here.)
# So let's first have a look:

psfcat = megalut.tools.io.readpickle("psfs/cat_psfgrid.pkl")
print psfcat[:5]
print len(psfcat)
print psfcat.meta

# Now we can prepare the ImageInfo object from scratch, and already attach it to the galcat.
galcat.meta["psf"] = megalut.tools.imageinfo.ImageInfo("psfs/psfgrid.fits", xname="psfx", yname="psfy", stampsize=32)

# Now we have to add "psfx" and "psfy" columns to our galcat, and fill in a value for each row.
# Oops, this catalog has only 100 PSFs, but we want to simulate 400 galaxies !
# So let's randomly assign a PSF to each galaxy in galcat.
# Here is a neat way of doing this:

matched_psfcat = psfcat[np.random.randint(low=0, high=100, size=400)] # We love astropy.table :)
# Note BTW that this makes a copy (not just refs).

# Now we add the PSF positions to the galcat:
galcat["psfx"] = matched_psfcat["psfx"]
galcat["psfy"] = matched_psfcat["psfy"]

# Note that the PSFs don't even have to be on a grid, any x and y coordinates are fine.
# We could also give the same x and y for each galaxy, so that only one PSF gets used.

print galcat[:5]

# We are now ready to feed this into drawimg :

megalut.sim.stampgrid.drawimg(galcat,
	simgalimgfilepath="simgalimg.fits",
	simtrugalimgfilepath="simtrugalimg.fits",
	simpsfimgfilepath="simpsfimg.fits"
	)

# We can directly proceed by measuring the images

gridimg = megalut.tools.image.loadimg("simgalimg.fits")
meascat = megalut.meas.galsim_adamom.measure(gridimg, galcat, stampsize=48, prefix="mes_")

# meascat is the output catalog, it contains the measured features:
print meascat[:5]

# We save it into a pickle
megalut.tools.io.writepickle(meascat, "meascat.pkl")

print "If you see masked values here, despite the fact that mes_flag is 0, update your numpy !"

# Let's make a simple comparision plot:
import matplotlib.pyplot as plt
resi_x = meascat["mes_x"] - meascat["x"]
resi_y = meascat["mes_y"] - meascat["y"]
flag = meascat["mes_flag"]
plt.scatter(resi_x, resi_y, c=flag, lw=0, s=30)
plt.xlabel("mes_x residual")
plt.ylabel("mes_y residual")
plt.title("This is offset as the PSFs are not centered, fix me!")
plt.show()


