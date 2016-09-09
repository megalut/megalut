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

import megalut.tools as tools
import megalut.meas as meas

import megalutgreat3 as mg3

import config
import g3measfct as measfct

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the run
great3 = config.load_run()


sfside = 3 * great3.stampsize()
stararray = np.zeros((sfside, sfside*len(config.subfields)))


for (i, subfield) in enumerate(config.subfields):

	
	# We read in the FITS image
	startile = tools.io.fromfits(great3.starimgfilepath(subfield))
	stararray[:, i*sfside:(i+1)*sfside] = startile
	
tools.io.tofits(stararray, great3.get_path("obs", "allstars.fits"))


# Now make a simple catalog for these:

stars = []
for i in range(3):
	for j in range(3*len(config.subfields)):
		stars.append( [0.5 + great3.stampsize()/2.0 + i*great3.stampsize(), 0.5 + great3.stampsize()/2.0 + j*great3.stampsize()] )

stars = np.array(stars)
starcat = astropy.table.Table([stars[:,0], stars[:,1]], names=('psfx', 'psfy'))
#print starcat
	
	
# We attach the image:
starcat.meta["img"] = tools.imageinfo.ImageInfo(
	filepath=great3.get_path("obs", "allstars.fits"),
	xname="psfx",
	yname="psfy",
	stampsize=great3.stampsize(),
	workdir=great3.get_path("obs", "allstars_measworkdir")
	)

# Run the measurement:
starcat = measfct.psf(starcat, branch=great3)
#print starcat[["psfx", "psfy", "psf_sewpy_XWIN_IMAGE", "psf_sewpy_YWIN_IMAGE", "psf_adamom_x", "psf_adamom_y"]]
#print starcat

# And save the catalog
tools.io.writepickle(starcat, great3.get_path("obs", "allstars_meascat.pkl"))



