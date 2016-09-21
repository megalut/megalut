"""
To be able to create a single training set for all branches,
we stack the starfield images into one single FITS file,
and create a single star catalog.
"""

import multiprocessing
import datetime
import numpy as np
import astropy.table

from astropy.io import fits

import megalut

import megalutgreat3

import config
import measfcts

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the run
great3 = config.load_run()


stampsize = great3.stampsize()
assert stampsize%2 == 0
sfside = 3 * stampsize
stararray = np.zeros((sfside, sfside*len(config.subfields)))


for (i, subfield) in enumerate(config.subfields):

	# We read in the FITS image
	startile = megalut.tools.io.fromfits(great3.starimgfilepath(subfield))
	stararray[:, i*sfside:(i+1)*sfside] = startile # So the bottom 9 stars get the first subfield number.
	
megalut.tools.io.tofits(stararray, great3.path("obs", "allstars.fits"))



# Now make a simple catalog for these:
stars = []
for (s, subfield) in enumerate(config.subfields):
	for i in range(3):
		for j in range(3):
			stars.append( [0.5 + stampsize/2.0 + i*stampsize, 0.5 + stampsize/2.0 + j*stampsize + s*sfside, subfield] )

stars = np.array(stars)
starcat = astropy.table.Table([stars[:,0], stars[:,1], stars[:,2]], names=('psfx', 'psfy', 'subfield'), dtype=(np.float, np.float, np.int))
#print starcat
	
	

# We attach the image:
starcat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
	filepath=great3.path("obs", "allstars.fits"),
	xname="psfx",
	yname="psfy",
	stampsize=great3.stampsize(),
	workdir=great3.path("obs", "allstars_measworkdir")
	)


# Run the measurement:
starcat = measfcts.psf(starcat, branch=great3)
#print starcat[["psfx", "psfy", "psf_sewpy_XWIN_IMAGE", "psf_sewpy_YWIN_IMAGE", "psf_adamom_x", "psf_adamom_y"]]
#print starcat


# And save the catalog
megalut.tools.io.writepickle(starcat, great3.path("obs", "allstars_meascat.pkl"))



