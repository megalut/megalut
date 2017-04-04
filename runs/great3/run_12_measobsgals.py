"""
Attach the PSF measurements to the galaxy catalogs, and run the galaxy shape measurments.
Again individually for each subfields (but multi-cpu).
"""

import multiprocessing
import datetime
import numpy as np
import astropy.table

import megalut
import megalutgreat3

import config
import measfcts

import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)


incatfilepaths = []
outcatfilepaths = []


# Prepare the input catalogs:

for subfield in config.great3.subfields:

	config.great3.mkdirs(subfield)

	starcat = megalut.tools.io.readpickle(config.great3.subpath(subfield, "obs", "star_meascat.pkl"))
	#print starcat
				
	incat = megalutgreat3.io.readgalcat(config.great3, subfield)
	
	
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
	
	incat.meta["img"] = megalut.tools.imageinfo.ImageInfo(
		filepath=config.great3.galimgfilepath(subfield),
		xname="x",
		yname="y",
		stampsize=config.great3.stampsize(),
		workdir=config.great3.subpath(subfield, "obs", "img_measworkdir")
		)

	incat.meta["psf"] = megalut.tools.imageinfo.ImageInfo(
		filepath=config.great3.starimgfilepath(subfield),
		xname="psfx",
		yname="psfy",
		stampsize=config.great3.stampsize(),
		workdir=None
		)

	# Write the input catalog
	incatfilepath = config.great3.subpath(subfield, "obs", "img_incat.pkl")
	megalut.tools.io.writepickle(incat, incatfilepath)
	incatfilepaths.append(incatfilepath)
	
	# Prepare the filepath for the output catalog
	outcatfilepath = config.great3.subpath(subfield, "obs", "img_meascat.pkl")
	outcatfilepaths.append(outcatfilepath)


# And we're ready to run the measurements


# We pass some kwargs for the measfct
measfctkwargs = {"branch":config.great3}

# And we run with ncpu
megalut.meas.run.general(incatfilepaths, outcatfilepaths, measfcts.gal, measfctkwargs=measfctkwargs,
					ncpu=config.great3.ncpu, skipdone=config.great3.skipdone)

