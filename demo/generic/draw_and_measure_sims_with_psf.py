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


# As before, we first set the desired distributions of parameters:

class Flux600(megalut.sim.params.Params):
	def get_flux(self):
		return 600.0
mysimparams = Flux600()

# And we prepare a catalog of 20 x 20 simulated galaxies:

galcat = megalut.sim.stampgrid.drawcat(mysimparams, n=20, stampsize=48)

print galcat[:5]


# Now, we prepare the PSF stuff. In this case we'll use existing files.
# We need an image with PSF stamps, and a catalog of this image.
# For the image, we can either specify a Galsim image, or a filepath.

#psfimg = megalut.tools.image.loadimg("psfs/psfgrid.fits")
psfimg = "psfs/psfgrid.fits"
psfcat = megalut.tools.io.readpickle("psfs/cat_psfgrid.pkl")
print psfcat[:5]

# The only columns we care about are those giving the position of each PSF, called psfgridx and psfgridy in this case.
# We will later tell drawimg to use these columns.
# You could very well prepare a catalog containing only x and y, nothing else.
# Note that the PSFs don't even have to be on a grid !

# We also need psfcat.meta to hold the stampsize (which can be different from the galcat stampsize !)
# For this demo catalog, it's correctly set, to 32:

print psfcat.meta["stampsize"]


# There is one more constraint:

print len(psfcat)

# Oops, this catalog has only 100 PSFs, but we want to simulate 400 galaxies !
# We *have* to provide a PSF catalog of the same length as the galcat.
# So let's build this catalog by randomly picking PSFs:

matched_psfcat = psfcat[np.random.randint(low=0, high=100, size=400)] # We love astropy.table :)
# Note that this makes a copy (not just refs), exactly as we want.


# We are now ready to feed this into drawimg :

megalut.sim.stampgrid.drawimg(galcat, psfcat=matched_psfcat, psfimg=psfimg,
	psfxname="psfgridx", psfyname="psfgridy",
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

# Let's make a simple comparision plot:
import matplotlib.pyplot as plt
resi_x = meascat["mes_x"] - meascat["x"]
resi_y = meascat["mes_y"] - meascat["y"]
flag = meascat["mes_flag"]
plt.scatter(resi_x, resi_y, c=flag, lw=0, s=30)
plt.xlabel("mes_x residual")
plt.ylabel("mes_y residual")
plt.show()


