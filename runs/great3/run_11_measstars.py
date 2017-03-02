"""
Measures features of the PSFs, 
individually for each subfield.
"""
import multiprocessing
import datetime
import numpy as np
import astropy.table

import megalut

import config
import measfcts

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


for subfield in config.great3.subfields:


	# We don't bother reading the starcat, and just make one
	stars = []
	for i in range(3):
		for j in range(3):
			stars.append( [0.5 + config.great3.stampsize()/2.0 + i*config.great3.stampsize(), 0.5 + config.great3.stampsize()/2.0 + j*config.great3.stampsize()] )
	stars = np.array(stars)
	
	starcat = astropy.table.Table([stars[:,0], stars[:,1]], names=('psfx', 'psfy'))
	#print starcat
	
	# We add the subfield number to the catalog, might be handy later.
	starcat["subfield"] = subfield
	
	
	# To measure the stars, we attach the image:
	starcat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=config.great3.starimgfilepath(subfield),
		xname="psfx",
		yname="psfy",
		stampsize=config.great3.stampsize(),
		workdir=config.great3.path("obs", "star_%i_measworkdir" % subfield)
		)

	starcat = measfcts.psf(starcat, branch=config.great3)
	#print starcat[["psfx", "psfy", "psf_sewpy_XWIN_IMAGE", "psf_sewpy_YWIN_IMAGE", "psf_adamom_x", "psf_adamom_y"]]
	#print starcat

	megalut.tools.io.writepickle(starcat, config.great3.path("obs", "star_%i_meascat.pkl" % subfield))
	

