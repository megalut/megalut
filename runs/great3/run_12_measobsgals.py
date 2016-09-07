"""
Attach the PSF measurements to the galaxy catalogs, and run the galaxy shape measurments.
Again individually for each subfields (but multi-cpu).
"""

import multiprocessing
import datetime
import numpy as np
import astropy.table

import megalut.tools as tools
import megalut.meas as meas

import megalutgreat3 as mg3

import config
import measfcts

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the run
great3 = config.load_run()


incatfilepaths = []
outcatfilepaths = []


# Prepare the input catalogs:

for subfield in config.subfields:


	starcat = tools.io.readpickle(great3.path("obs", "star_%i_meascat.pkl" % subfield))
	#print starcat
				
	incat = mg3.io.readgalcat(great3, subfield)
	
	
	# We add PSF info to this field. PSFs are already measured, and we take a random one (among 9) for each galaxy.
	
	starcat.meta = {} # Dump the "img" entry
	#matchedstarcat = starcat[np.zeros(len(incat), dtype=int)]
	matchedstarcat = starcat[np.random.randint(9, size=len(incat))]
	
	assert len(incat) == len(matchedstarcat)
	for colname in incat.colnames:
		if colname in matchedstarcat.colnames:
			raise RuntimeError("colname %s appears twice" % colname)
	
	incat = astropy.table.hstack([incat, matchedstarcat], join_type="exact", metadata_conflicts="error")
	
	#print incat.colnames
	#print incat[("ID", "x", "psfy", "psf_adamom_y", "psf_adamom_sigma")]
	
	# Add the reference to the img and psf stamps:
	
	incat.meta["img"] = tools.imageinfo.ImageInfo(
		filepath=great3.galimgfilepath(subfield),
		xname="x",
		yname="y",
		stampsize=great3.stampsize(),
		workdir=great3.path("obs", "img_%i_measworkdir" % subfield)
		)

	incat.meta["psf"] = tools.imageinfo.ImageInfo(
		filepath=great3.starimgfilepath(subfield),
		xname="psfx",
		yname="psfy",
		stampsize=great3.stampsize(),
		workdir=None
		)

	# Write the input catalog
	incatfilepath = great3.path("obs", "img_%i_incat.pkl" % subfield)
	tools.io.writepickle(incat, incatfilepath)
	incatfilepaths.append(incatfilepath)
	
	# Prepare the filepath for the output catalog
	outcatfilepath = great3.path("obs", "img_%i_meascat.pkl" % subfield)
	outcatfilepaths.append(outcatfilepath)


# And we're ready to run the measurements


# We pass some kwargs for the measfct
measfctkwargs = {"branch":great3}

# And we run with ncpu
meas.run.general(incatfilepaths, outcatfilepaths, measfcts.gal, measfctkwargs=measfctkwargs,
					ncpu=config.ncpu, skipdone=config.skipdone)

