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
# We need an image with PSF stamps, and we need to add new columns in galcat.
# For the image, we can either specify a Galsim image, or a filepath.

#psfimg = megalut.tools.image.loadimg("psfs/psfgrid.fits")
psfimg = "psfs/psfgrid.fits"
psfcat = megalut.tools.io.readpickle("psfs/cat_psfgrid.pkl")
print psfcat[:5]
print len(psfcat)

# The only columns we care about are those giving the position of each PSF, called psfgridx and psfgridy in this case.
# Oops, this catalog has only 100 PSFs, but we want to simulate 400 galaxies !
# So let's randomly assign a PSF to each galaxy in galcat.
# Here is a neat way of doing this:

matched_psfcat = psfcat[np.random.randint(low=0, high=100, size=400)] # We love astropy.table :)
# Note BTW that this makes a copy (not just refs).


# Now we add the PSF positions to the galcat:
galcat["psfx"] = matched_psfcat["psfgridx"]
galcat["psfy"] = matched_psfcat["psfgridy"]

# Note that the PSFs don't even have to be on a grid, any x and y coordinates are fine.
# We could also give the same x and y for each galaxy, so that only one PSF gets used.

# We also need galcat.meta to hold the psfstampsize (which can be different from the galcat stampsize !)
# For this demo catalog, it's correctly set, to 32:

galcat.meta["psfstampsize"] = psfcat.meta["stampsize"]

print galcat[:5]

# We are now ready to feed this into drawimg :

megalut.sim.stampgrid.drawimg(galcat, psfimg=psfimg,
	psfxname="psfx", psfyname="psfy",
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


